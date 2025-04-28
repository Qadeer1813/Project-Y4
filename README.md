# Elderly Care Management System

Project Author: Qadeer Hussain
SETU Carlow
Date: 28/04/2025

# NOTE

Please make the following file in the \Elderly Care Management System\CareNet\CareNet directory 
File is called config.py
This file includes thew following 
```
DB_CONFIG = {
    'user': '',
    'password': '',
    'host': '',
    'database': 'carenet',
    'port': 3306
}

API_TOKEN = ""
API_BASE_URL = ""
API_ENDPOINTS = {
    'current_key': f"{API_BASE_URL}/current-key",
    'check_key': f"{API_BASE_URL}/check-key",
    'rotate_key': f"{API_BASE_URL}/rotate-key"
}
# Global flag for maintenance mode
MAINTENANCE_MODE = False
```


To make a user when you first launch the app you must create a supervuser run this in shell
```
import bcrypt
from CareNet.app import get_db_connection

username = ""
password = ""
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute(
    "INSERT INTO users (Username, Password, role) VALUES (%s, %s, %s)",
    (username, hashed, 'admin')
)
conn.commit()
cursor.close()
conn.close()

print("SUPERUSER CREATED")
```
In the Carenet Database this is the following SQL Query
```
CREATE TABLE IF NOT EXISTS `patient_profile` (
  `Patient_ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` text NOT NULL,
  `DOB` text NOT NULL,
  `Contact_Number` text NOT NULL DEFAULT '+353',
  `Email_Address` text NOT NULL,
  `Home_Address` text NOT NULL,
  `Next_Of_Kin_Name` text NOT NULL,
  `Emergency_Contact_Number` text NOT NULL,
  `Next_Of_Kin_Home_Address` text NOT NULL,
  `Emergency_Email_Address` text NOT NULL,
  PRIMARY KEY (`Patient_ID`)
);

CREATE TABLE IF NOT EXISTS medical_dashboard (
    Patient_Medical_Dashboard_ID INT NOT NULL AUTO_INCREMENT,
    Patient_ID INT NOT NULL,
    Medications TEXT NOT NULL,
    Medical_History TEXT,
    Allergies TEXT,
    PRIMARY KEY (Patient_Medical_Dashboard_ID),
    FOREIGN KEY (Patient_ID) REFERENCES patient_profile(Patient_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS medical_files (
    Medical_Files_ID INT PRIMARY KEY AUTO_INCREMENT,
    Patient_Medical_Dashboard_ID INT NOT NULL,
    File_Name VARCHAR(255),
    File_Data LONGBLOB,
    FOREIGN KEY (Patient_Medical_Dashboard_ID) REFERENCES medical_dashboard(Patient_Medical_Dashboard_ID)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS roster (
    Roster_ID INT AUTO_INCREMENT PRIMARY KEY,
    Day TEXT NOT NULL,
    Shift_Time TEXT NOT NULL,
    Carer TEXT NOT NULL,
    Patient TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS care_planner (
    Care_Planner_ID INT AUTO_INCREMENT PRIMARY KEY,
    Patient_ID INT NOT NULL,
    Daily_Activities TEXT NOT NULL,
    Notes TEXT NOT NULL,
    FOREIGN KEY (Patient_ID) REFERENCES patient_profile(Patient_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `users` (
  `User_Id` int(11) NOT NULL AUTO_INCREMENT,
  `Username` varchar(100) NOT NULL,
  `Password` text NOT NULL,
  `role` enum('admin','carer') NOT NULL,
  PRIMARY KEY (`User_Id`),
  UNIQUE KEY `Username` (`Username`)
);


```

In the Key Server database run the following SQL Query
```
CREATE TABLE api_tokens (
    Token_ID INT AUTO_INCREMENT PRIMARY KEY,
    Token VARCHAR(255) NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Is_Valid BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS key_management (
  Key_ID int(11) NOT NULL AUTO_INCREMENT,
  Encryption_Key text NOT NULL,
  Is_Valid tinyint(1) DEFAULT 1,
  Created_At datetime DEFAULT current_timestamp(),
  PRIMARY KEY (Key_ID)
) 

```
Thank you
