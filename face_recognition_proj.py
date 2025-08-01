import os
import cv2
import face_recognition
import numpy as np
import pymysql
import pymysql.err
from datetime import datetime, time as dt_time

# --- MySQL Configuration ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Taru..KA.15',
    'database': 'attendance_system'
}

def get_db_connection():
    return pymysql.connect(**db_config)

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            date DATE,
            time TIME,
            slot VARCHAR(10),
            UNIQUE(name, date, slot)
        )
    """)
    conn.commit()
    conn.close()

def mark_attendance(name, slot):
    now = datetime.now()
    date_today = now.date()
    time_now = now.time()

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO attendance (name, date, time, slot)
            VALUES (%s, %s, %s, %s)
        """, (name, date_today, time_now, slot))
        conn.commit()
    except pymysql.err.IntegrityError:
        pass  # Already marked for this slot today
    conn.close()

def load_known_faces(folder_path="output"):
    known_face_encodings = []
    known_face_names = []

    for person_name in os.listdir(folder_path):
        person_dir = os.path.join(folder_path, person_name)
        if not os.path.isdir(person_dir):
            continue

        for filename in os.listdir(person_dir):
            filepath = os.path.join(person_dir, filename)
            try:
                image = face_recognition.load_image_file(filepath)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    known_face_encodings.append(encodings[0])
                    known_face_names.append(person_name)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

    return known_face_encodings, known_face_names

def get_current_slot():
    now = datetime.now().time()
    if dt_time(6, 0) <= now <= dt_time(7, 0):
        return "Entry"
    elif dt_time(17, 0) <= now <= dt_time(18, 0):
        return "Exit"
    return None

def main():
    initialize_database()
    known_face_encodings, known_face_names = load_known_faces()

    if not known_face_encodings:
        print("No known faces loaded. Please check the output folder.")
        return

    video_capture = cv2.VideoCapture(0)
    print("Starting live face recognition. Press 'q' to exit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Camera frame not captured. Exiting.")
            break

        slot = get_current_slot()
        if not slot:
            cv2.putText(frame, "Not in valid time slot (9–10 AM or 5–6 PM)", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.imshow("Live Face Recognition", frame)
            if cv2.waitKey(500) & 0xFF == ord('q'):
                break
            continue

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            if name != "Unknown":
                mark_attendance(name, slot)

            # Rescale for display
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        cv2.imshow("Live Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
