import cv2
import os
import numpy as np
import serial  # PySerial for ESP32 communication
import time

# Setup Serial Communication
ser = serial.Serial("COM3", 115200, timeout=1)  # Update COM port
time.sleep(2)  # Allow ESP32 to initialize

# Paths for Face Dataset & Model
DATASET_PATH = "faces"
MODEL_PATH = "face_model.xml"

# Load Haarcascade Classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def send_to_esp32(message):
    """Send data to ESP32 with newline"""
    ser.write(f"{message}\n".encode())
    print(f"Sent to ESP32: {message}")
    time.sleep(0.5)  # Small delay to prevent data loss

def recognize_faces():
    """Detect faces and send status to ESP32"""
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found! Train the model first.")
        return

    # Load trained model
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)

    # Create label dictionary
    label_dict = {}
    for file in os.listdir(DATASET_PATH):
        if file.endswith(".jpg"):
            label = file.split("_")[0]
            if label not in label_dict:
                label_dict[label] = len(label_dict)

    # Start webcam
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            label, confidence = recognizer.predict(face)

            if confidence < 50:
                name = [key for key, val in label_dict.items() if val == label][0]
                text = f"Authorized: {name}"
            else:
                text = "Intruder"

            print(f"Sending to ESP32: {text}")
            send_to_esp32(text)  # Send data to ESP32

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    ser.close()  # Close Serial Connection

if __name__ == "__main__":
    recognize_faces()
