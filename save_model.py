import face_recognition
import pickle
import os

# Directories
KNOWN_DIR = "known_person"
CRIMINAL_DIR = "criminal_person"

known_encodings = []
known_names = []
criminal_encodings = []
criminal_names = []

print("[INFO] Encoding images...")


def process_directory(directory, encodings_list, names_list, label):
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            name = filename.split("_")[0]  # Extract person's name from filename
            img_path = os.path.join(directory, filename)

            image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                encodings_list.append(encodings[0])
                names_list.append(name)

    print(f"[INFO] Encoded {len(encodings_list)} faces from {label}")


# Process known and criminal persons
process_directory(KNOWN_DIR, known_encodings, known_names, "Known Persons")
process_directory(CRIMINAL_DIR, criminal_encodings, criminal_names, "Criminal Persons")

# Save encodings
data = {
    "known_encodings": known_encodings,
    "known_names": known_names,
    "criminal_encodings": criminal_encodings,
    "criminal_names": criminal_names
}

with open("your_model_name.pkl", "wb") as f:
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

print("[INFO] Encodings saved successfully!")
