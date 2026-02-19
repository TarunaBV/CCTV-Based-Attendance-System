# CCTV-Based-Attendance-System

# --> Clone Repository
git clone https://github.com/yourusername/face-attendance.git
cd face-attendance

# --> Install Dependencies
pip install -r requirements.txt

# --> Create the Database and tables

  **Database : face_db**
  CREATE DATABASE face_db;

  **Use the table face_db :**
  USE face_db;

  **Table 1 : admins**
  CREATE TABLE admins (
    admin_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  **Table 2 : employees**
  CREATE TABLE employees (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    embedding LONGBLOB,
    password_hash VARCHAR(255),
    contact_number VARCHAR(15)
  );

  **Table 3 : attendance**
  CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(10),
    date DATE,
    in1 TIME,
    out1 TIME,
    in2 TIME,
    out2 TIME,
    
    CONSTRAINT attendance_ibfk_1
    FOREIGN KEY (emp_id)
    REFERENCES employees(emp_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
  );

# --> Change database password
Give the password of your database in 
  "password": "xyz" in app.py AND
  MYSQL_PASSWORD = "xyz" in recognize.py

# --> Change the rtsp link
Give the rtsp link of your camera in **cv2.VideoCapture("rtsp://10.76.127.5:5000/")** in both the files.
If you want to use the webcam, simply use 0. **cv2.VideoCapture(0)**

# --> Setup Twilio
Use twilio api for the real time whatsapp messages. Use your SID and TOKEN.

# --> Run the application
python app.py
  Register an employee
python recognize.py
  Attendance marking
