import cv2
import os
import time


def capture_frames(output_folder, time_limit=5):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(0)  # Open the default camera
    if not cap.isOpened():
        print("Error: Could not access the camera.")
        return

    start_time = time.time()
    frame_count = 0

    while (time.time() - start_time) < time_limit:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_filename, frame)
        frame_count += 1

        cv2.imshow("Captured Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Captured {frame_count} frames in {time_limit} seconds and saved to {output_folder}")


if __name__ == "__main__":
    output_folder = "captured_frames"
    capture_frames(output_folder)
