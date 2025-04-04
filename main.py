import cv2
import os
import numpy as np

# Paths
DATASET_PATH = "faces"
MODEL_PATH = "face_model.xml"

# Create dataset directory if not exists
if not os.path.exists(DATASET_PATH):
    os.makedirs(DATASET_PATH)

# Load OpenCV's Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def capture_faces(label):
    """Captures face images and saves them to the dataset."""
    cap = cv2.VideoCapture(0)
    count = 0

    while count < 100:  # Capture 50 images per person
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            filename = f"{DATASET_PATH}/{label}_{count}.jpg"
            cv2.imwrite(filename, face)
            count += 1
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Capturing Faces", frame)
        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Captured {count} images for {label}")

def train_model():
    """Loads images, resizes them, trains LBPH face recognizer, and saves the model."""
    faces, labels = [], []
    label_dict = {}
    label_id = 0

    for file in os.listdir(DATASET_PATH):
        if file.endswith(".jpg"):
            label = file.split("_")[0]
            if label not in label_dict:
                label_dict[label] = label_id
                label_id += 1

            img_path = os.path.join(DATASET_PATH, file)
            face = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            face = cv2.resize(face, (400, 400))  # Ensure all images are the same size
            faces.append(np.array(face, dtype=np.uint8))  # Convert to NumPy array
            labels.append(label_dict[label])

    if len(faces) == 0:
        print("No face data found! Please capture faces first.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels, dtype=np.int32))  # Ensure integer labels
    recognizer.save(MODEL_PATH)

    print(f"Model trained and saved as {MODEL_PATH}")


def recognize_faces():
    """Loads trained model and detects faces in real-time."""
    if not os.path.exists(MODEL_PATH):
        print("Model not found! Please train the model first.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)

    # Load labels
    label_dict = {}
    for file in os.listdir(DATASET_PATH):
        if file.endswith(".jpg"):
            label = file.split("_")[0]
            if label not in label_dict:
                label_dict[label] = len(label_dict)

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
                text = f"{name} ({confidence:.2f})"
                color = (0, 255, 0)
            else:
                text = "Unauthorised Personnel"
                color = (0, 0, 255)

            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    while True:
        print("\n1. Capture Faces\n2. Train Model\n3. Recognize Faces\n4. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            label = input("Enter person's name: ")
            capture_faces(label)
        elif choice == "2":
            train_model()
        elif choice == "3":
            recognize_faces()
        elif choice == "4":
            break
        else:
            print("Invalid choice! Try again.")
            