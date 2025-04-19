import sys
import cv2
import os
import pickle
import numpy as np
import face_recognition
import pandas as pd
from datetime import datetime
import winsound  # For beep sound (Windows)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget
from google.cloud import storage


def upload_to_firebase_storage(local_path, remote_path):
    bucket_name = 'your-bucket-name.appspot.com'  # ✅ Replace with your Firebase Storage bucket name

    storage_client = storage.Client.from_service_account_json("your-fcm-service-file.json")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(remote_path)

    blob.upload_from_filename(local_path)
    blob.make_public()  # Makes the file publicly accessible

    return blob.public_url


class FaceRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Face Recognition System")
        self.setGeometry(100, 100, 800, 600)

        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)

        self.toggle_button = QPushButton("Switch to Video", self)
        self.toggle_button.clicked.connect(self.toggle_camera)

        self.upload_button = QPushButton("Upload Video", self)
        self.upload_button.clicked.connect(self.load_video)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.upload_button)
        self.setLayout(layout)

        self.is_camera = True
        self.video_path = None
        self.capture = cv2.VideoCapture(0)

        self.known_encodings, self.known_names, self.criminal_encodings, self.criminal_names = self.load_encodings()
        self.recognition_log = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def toggle_camera(self):
        if self.is_camera:
            if self.video_path:
                self.capture = cv2.VideoCapture(self.video_path)
                self.toggle_button.setText("Switch to Camera")
                self.is_camera = False
        else:
            self.capture = cv2.VideoCapture(0)
            self.toggle_button.setText("Switch to Video")
            self.is_camera = True

    def load_video(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_name:
            self.video_path = file_name
            self.capture = cv2.VideoCapture(self.video_path)
            if not self.capture.isOpened():
                print(f"Failed to open video file: {self.video_path}")
                self.video_path = None
            else:
                self.is_camera = False
                self.toggle_button.setText("Switch to Camera")

    def load_encodings(self):
        if os.path.exists("your-trained-modal.pkl"):  #generate model before run code
            with open("your-trained-modal.pkl", "rb") as f:
                data = pickle.load(f)
            return data["known_encodings"], data["known_names"], data["criminal_encodings"], data["criminal_names"]
        else:
            print("[ERROR] Encodings file not found! Run save_encodings.py first.")
            return [], [], [], []

    def recognize_faces(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            name = "Unknown"
            color = (0, 0, 255)

            if self.known_encodings:
                face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < 0.5:
                    name = self.known_names[best_match_index]
                    color = (0, 255, 0)

            if self.criminal_encodings:
                face_distances = face_recognition.face_distance(self.criminal_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < 0.5:
                    name = self.criminal_names[best_match_index]
                    color = (0, 0, 255)
                    winsound.Beep(1000, 500)

                    # Save and upload image
                    timestamp = datetime.now()
                    date = timestamp.strftime("%Y-%m-%d")
                    time = timestamp.strftime("%H:%M:%S")
                    filename = f"{name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, frame)

                    #remote_path = f"suspects/{filename}"
                    #image_url = upload_to_firebase_storage(filename, remote_path)
                    image_url = ''
                    self.send_criminal_notification(name, date, time, image_url)

                    os.remove(filename)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.recognition_log.append([timestamp, name])

        return frame

    def update_frame(self):
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                frame = self.recognize_faces(frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def save_report(self):
        df = pd.DataFrame(self.recognition_log, columns=["Timestamp", "Name"])
        df.to_excel("face_recognition_report.xlsx", index=False)
        print("[INFO] Report saved as face_recognition_report.xlsx")

    def closeEvent(self, event):
        self.save_report()
        self.timer.stop()
        self.capture.release()
        cv2.destroyAllWindows()
        event.accept()

    def send_criminal_notification(self, name, date, time, image_url):
        import requests
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account
        import json

        SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
        SERVICE_ACCOUNT_FILE = 'your-service-file.json'

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        credentials.refresh(Request())
        access_token = credentials.token

        project_id = 'your-firebase-project'
        url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; UTF-8",
        }

        message = {
            "message": {
                "topic": "criminal_alerts",
                "data": {
                    "title": "Criminal Detected!",
                    "message": f"Name: {name}, Date: {date}, Time: {time}",
                    "name": name,
                    "date": date,
                    "time": time,
                    "image": image_url
                }
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(message))
        print("Status Code:", response.status_code)
        print("Response:", response.json())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec_())
