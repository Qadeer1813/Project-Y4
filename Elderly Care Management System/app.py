import os
import mysql.connector
from dotenv import load_dotenv
from functions import *

# Load environment variables
load_dotenv()

# Fetch the encryption key from the environment variable
key = os.getenv("DB_ENCRYPTION_KEY")
if key is None:
    raise ValueError("No encryption key found in environment variables.")
key = key.encode()

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            user='root',
            password='Qadeerh03',
            host='127.0.0.1',
            database='ecms',
            port=3306
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")

# Load your previously saved key
def load_key():
    return os.getenv('DB_ENCRYPTION_KEY').encode()

# Function to format contact numbers to drop the 0
def format_contact_number(number):
    if number.startswith('0'):
        number = '+353' + number[1:]
    return number

# Function to insert to create new patient profile
def create_patient(name, dob, contact_number, email_address, home_address, next_of_kin_name, emergency_contact_number, next_of_kin_home_address, emergency_email_address):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Format the contact number and the emergency contact number
        formatted_contact_number = format_contact_number(contact_number)
        formatted_emergency_contact_number = format_contact_number(emergency_contact_number)

        # Encrypt all data
        encrypted_name = encrypt_message(name, key)
        encrypted_dob = encrypt_message(dob, key)
        encrypted_contact_number = encrypt_message(formatted_contact_number, key)
        encrypted_email_address = encrypt_message(email_address, key)
        encrypted_home_address = encrypt_message(home_address, key)
        encrypted_next_of_kin_name = encrypt_message(next_of_kin_name, key)
        encrypted_emergency_contact_number = encrypt_message(formatted_emergency_contact_number, key)
        encrypted_next_of_kin_home_address = encrypt_message(next_of_kin_home_address, key)
        encrypted_emergency_email_address = encrypt_message(emergency_email_address, key)

        # SQL query to insert a new record into the patient_profile table
        create_patient_profile = '''
        INSERT INTO patient_profile (Name, DOB, Contact_Number, Email_Address, Home_Address, Next_Of_Kin_Name, Emergency_Contact_Number, Next_Of_Kin_Home_Address, Emergency_Email_Address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(create_patient_profile, (encrypted_name, encrypted_dob , encrypted_contact_number, encrypted_email_address, encrypted_home_address, encrypted_next_of_kin_name, encrypted_emergency_contact_number, encrypted_next_of_kin_home_address, encrypted_emergency_email_address))
        # Commit to the database
        conn.commit()
        print("Patient record created.")
    # If creating the patient fails throw error
    except mysql.connector.Error as e:
        print("Error occurred:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def search_patient(name=None, dob=None):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM patient_profile"
        cursor.execute(query)
        results = cursor.fetchall()

        filtered_results = []
        for record in results:
            match = True

            if name:
                try:
                    decrypted_name = decrypt_message(record[1], key)
                    if name.lower() not in decrypted_name.lower():
                        match = False
                except Exception:
                    match = False

            if dob and match:
                try:
                    decrypted_dob = decrypt_message(record[2], key)
                    if dob != decrypted_dob:
                        match = False
                except Exception:
                    match = False

            if match:
                filtered_results.append(record)

        return filtered_results

    except mysql.connector.Error as e:
        print("Error occurred:", e)
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Display function to handle the search results
def display_patient_info():
    name = input("Enter patient's name (or press enter to skip): ").strip()
    dob = input("Enter patient's date of birth YYYY-MM-DD (or press enter to skip): ").strip()

    patient_data = search_patient(
        name if name else None,
        dob if dob else None
    )

    if not patient_data:
        print("No patients found matching the search criteria.")
        return

    decrypted_patient_data = decrypt_patient_data(patient_data, key)

    print(f"\nFound {len(decrypted_patient_data)} matching patient(s):")
    for i, row in enumerate(decrypted_patient_data, 1):
        print(f"\nPatient {i}:")
        print("Patient ID:", row[0])
        print("Name:", row[1])
        print("DOB:", row[2])
        print("Contact Number:", row[3])
        print("Email Address:", row[4])
        print("Home Address:", row[5])
        print("Next Of Kin Name:", row[6])
        print("Emergency Contact Number:", row[7])
        print("Next Of Kin Home Address:", row[8])
        print("Emergency Email Address:", row[9])
        print("-" * 50)

def menu():
    while True:
        print("\nMenu")
        print("1. Create New Patient")
        print("2. Search for Patient")
        print("3. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            name = input("Enter patient's name: ")
            dob = input("Enter patient's DOB (YYYY-MM-DD): ")
            contact_number = input("Enter patient's contact number: ")
            email_address = input("Enter patient's email address: ")
            home_address = input("Enter patient's home address: ")
            next_of_kin_name = input("Enter next of kin's name: ")
            emergency_contact_number = input("Enter emergency contact number: ")
            next_of_kin_home_address = input("Enter next of kin home address: ")
            emergency_email_address = input("Enter emergency email address: ")
            create_patient(name, dob, contact_number, email_address, home_address, next_of_kin_name, emergency_contact_number, next_of_kin_home_address, emergency_email_address)
        elif choice == '2':
            display_patient_info()
        elif choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please choose again.")

if __name__ == "__main__":
    menu()