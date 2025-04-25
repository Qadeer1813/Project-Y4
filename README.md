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
API_BASE_URL = "http://localhost:8001/"
API_ENDPOINTS = {
    'current_key': f"{API_BASE_URL}/current-key",
    'check_key': f"{API_BASE_URL}/check-key",
    'rotate_key': f"{API_BASE_URL}/rotate-key"
}
# Global flag for maintenance mode
MAINTENANCE_MODE = False
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
)

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
