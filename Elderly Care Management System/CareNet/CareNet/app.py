import base64
import json
import mysql.connector
import requests
from .functions import *
from .config import *

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")

# Function to format contact numbers to drop the 0
def format_contact_number(number):
    if number and number.startswith('0'):
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
        encrypted_name = encrypt(name)
        encrypted_dob = encrypt(dob)
        encrypted_contact_number = encrypt(formatted_contact_number)
        encrypted_email_address = encrypt(email_address)
        encrypted_home_address = encrypt(home_address)
        encrypted_next_of_kin_name = encrypt(next_of_kin_name)
        encrypted_emergency_contact_number = encrypt(formatted_emergency_contact_number)
        encrypted_next_of_kin_home_address = encrypt(next_of_kin_home_address)
        encrypted_emergency_email_address = encrypt(emergency_email_address)

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

# Search for patient profile
def search_patient(name=None, dob=None, key= None):
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
                    decrypted_name = decrypt(record[1], key)
                    if name.lower() not in decrypted_name.lower():
                        match = False
                except Exception:
                    match = False

            if dob and match:
                try:
                    decrypted_dob = decrypt(record[2], key)
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

# Update patient profile
def update_patient(Patient_ID, name, dob, contact_number, email_address, home_address,
                  next_of_kin_name, emergency_contact_number, next_of_kin_home_address,
                  emergency_email_address):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Format contact numbers
        formatted_contact_number = format_contact_number(contact_number)
        formatted_emergency_contact_number = format_contact_number(emergency_contact_number)

        # Encrypt all data
        encrypted_name = encrypt(name)
        encrypted_dob = encrypt(dob)
        encrypted_contact_number = encrypt(formatted_contact_number)
        encrypted_email_address = encrypt(email_address)
        encrypted_home_address = encrypt(home_address)
        encrypted_next_of_kin_name = encrypt(next_of_kin_name)
        encrypted_emergency_contact_number = encrypt(formatted_emergency_contact_number)
        encrypted_next_of_kin_home_address = encrypt(next_of_kin_home_address)
        encrypted_emergency_email_address = encrypt(emergency_email_address)

        update_query = '''
        UPDATE patient_profile 
        SET Name=%s, DOB=%s, Contact_Number=%s, Email_Address=%s, 
            Home_Address=%s, Next_Of_Kin_Name=%s, Emergency_Contact_Number=%s, 
            Next_Of_Kin_Home_Address=%s, Emergency_Email_Address=%s
        WHERE Patient_ID=%s
        '''
        cursor.execute(update_query, (encrypted_name, encrypted_dob, encrypted_contact_number,
                                    encrypted_email_address, encrypted_home_address,
                                    encrypted_next_of_kin_name, encrypted_emergency_contact_number,
                                    encrypted_next_of_kin_home_address, encrypted_emergency_email_address,
                                    Patient_ID))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print("Error updating patient:", e)
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Delete Patient Profile
def delete_patient(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        delete_query = "DELETE FROM patient_profile WHERE Patient_ID = %s"
        cursor.execute(delete_query, (patient_id,))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print("Error deleting patient:", e)
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def patient_medical_info(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT COUNT(*) FROM medical_dashboard WHERE Patient_ID = %s"
        cursor.execute(query, (patient_id,))
        count = cursor.fetchone()[0]
        return count > 0

    except mysql.connector.Error as e:
        print(f"Error checking medical data: {e}")
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def add_patient_medical_info(patient_id, names, dosages, history, medical_files, medical_filenames, allergies):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        medications = [{"name": name, "dosage": dosage} for name, dosage in zip(names, dosages)]
        medication_json = json.dumps(medications)

        encrypted_medications = encrypt(medication_json)
        encrypted_history = encrypt(history)
        encrypted_allergies = encrypt(allergies)

        dashboard_query = '''
            INSERT INTO medical_dashboard 
            (Patient_ID, Medications, Medical_History, Allergies)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(dashboard_query, (
            patient_id,
            encrypted_medications,
            encrypted_history,
            encrypted_allergies
        ))
        conn.commit()

        dashboard_id = cursor.lastrowid

        if medical_files:
            for file_data, filename in zip(medical_files, medical_filenames):
                file_insert = '''
                    INSERT INTO medical_files (Patient_Medical_Dashboard_ID, File_Name, File_Data)
                    VALUES (%s, %s, %s)
                '''
                cursor.execute(file_insert, (dashboard_id, filename, file_data))

        conn.commit()
        return True

    except mysql.connector.Error as e:
        print("Error occurred:", e)
        return False

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def patient_medical_dashboard_info(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT Patient_Medical_Dashboard_ID, Medications, Medical_History, Allergies 
            FROM medical_dashboard 
            WHERE Patient_ID = %s
        """, (patient_id,))
        result = cursor.fetchone()
        if not result:
            return None

        dashboard_id, medical_data, history_data, allergy_data = result
        key = get_encryption_key()

        medications = json.loads(decrypt(medical_data, key))
        history = decrypt(history_data, key)
        allergies = decrypt(allergy_data, key)

        cursor.execute("""
            SELECT Medical_Files_ID, File_Name, File_Data FROM medical_files 
            WHERE Patient_Medical_Dashboard_ID = %s
        """, (dashboard_id,))
        files = [{"id": row[0], "filename": row[1], "data": row[2]} for row in cursor.fetchall()]

        return {
            "medications": medications,
            "history": history,
            "files": files,
            "allergies": allergies
        }

    except mysql.connector.Error as e:
        print("Error fetching dashboard:", e)
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def update_patient_medical_info(patient_id, names, dosages, history, new_files, new_file_names, allergies, delete_flags):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT Patient_Medical_Dashboard_ID FROM medical_dashboard WHERE Patient_ID = %s", (patient_id,))
        result = cursor.fetchone()
        if not result:
            print("No dashboard found for patient.")
            return False

        dashboard_id = result[0]

        delete_meds = delete_flags.getlist("delete_medication[]")
        medications = [
            {"name": n, "dosage": d}
            for n, d, flag in zip(names, dosages, delete_meds)
            if flag != "1"
        ]
        encrypted_medications = encrypt(json.dumps(medications))
        encrypted_history = encrypt(history)
        encrypted_allergies = encrypt(allergies)

        cursor.execute("""
            UPDATE medical_dashboard
            SET Medications = %s, Medical_History = %s, Allergies = %s
            WHERE Patient_ID = %s
        """, (encrypted_medications, encrypted_history, encrypted_allergies, patient_id))

        cursor.execute("""
            SELECT Medical_Files_ID FROM medical_files
            WHERE Patient_Medical_Dashboard_ID = %s
        """, (dashboard_id,))
        file_ids = cursor.fetchall()

        for (file_id,) in file_ids:
            flag_key = f"delete_file_{file_id}"
            if flag_key in delete_flags and delete_flags[flag_key] == "1":
                cursor.execute("DELETE FROM medical_files WHERE Medical_Files_ID = %s", (file_id,))

        for file_data, file_name in zip(new_files, new_file_names):
            cursor.execute("""
                INSERT INTO medical_files (Patient_Medical_Dashboard_ID, File_Name, File_Data)
                VALUES (%s, %s, %s)
            """, (dashboard_id, file_name, file_data))

        conn.commit()
        return True

    except mysql.connector.Error as e:
        print("Error updating medical details:", e)
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def reencryption():
    print("Starting re-encryption process...")

    try:
        old_key = get_encryption_key()

        refreshed_key, refreshed_timestamp = get_encryption_key_with_metadata()

        if old_key == refreshed_key:
            print("No manual key rotation detected.")
            return

        else:
            print(f"Manual key rotation detected (key created at {refreshed_timestamp}).")
            new_key = refreshed_key

        if new_key == old_key:
            raise Exception("Re-encryption failed: key did not rotate.")

        fernet_old = Fernet(old_key.encode())
        fernet_new = Fernet(new_key.encode())

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patient_profile")
        patients = cursor.fetchall()
        cursor.close()
        conn.close()

        conn = get_db_connection()
        cursor = conn.cursor()
        failed_records = []

        for patient in patients:
            patient_id = patient[0]
            encrypted_fields = patient[1:]
            decrypted_fields = []

            for field in encrypted_fields:
                if field is not None:
                    try:
                        decrypted_field = fernet_old.decrypt(field.encode()).decode()
                        re_encrypted_field = fernet_new.encrypt(decrypted_field.encode()).decode()
                        decrypted_fields.append(re_encrypted_field)
                    except Exception as e:
                        print(f"Error processing patient {patient_id}: {e}")
                        failed_records.append(patient_id)
                        decrypted_fields.append(None)
                else:
                    decrypted_fields.append(None)

            update_query = '''
                UPDATE patient_profile 
                SET Name=%s, DOB=%s, Contact_Number=%s, Email_Address=%s, 
                    Home_Address=%s, Next_Of_Kin_Name=%s, Emergency_Contact_Number=%s, 
                    Next_Of_Kin_Home_Address=%s, Emergency_Email_Address=%s
                WHERE Patient_ID=%s
            '''
            cursor.execute(update_query, (*decrypted_fields, patient_id))

        cursor.execute("SELECT Patient_ID, Medications, Medical_History, Allergies FROM medical_dashboard")
        dashboards = cursor.fetchall()

        for patient_id, medication, history, allergies in dashboards:
            try:
                medication = fernet_new.encrypt(fernet_old.decrypt(medication.encode())).decode()
                history = fernet_new.encrypt(fernet_old.decrypt(history.encode())).decode()
                allergies = fernet_new.encrypt(fernet_old.decrypt(allergies.encode())).decode()

                cursor.execute("""
                            UPDATE medical_dashboard
                            SET Medications=%s, Medical_History=%s, Allergies=%s
                            WHERE Patient_ID=%s
                        """, (medication, history, allergies, patient_id))
            except Exception as e:
                print(f"Error processing medical_dashboard for Patient_ID={patient_id}: {e}")
                failed_records.append(patient_id)
        conn.commit()
        cursor.close()
        conn.close()

        if failed_records:
            print(f"Warning: Failed to re-encrypt records for patients: {failed_records}")
        else:
            print("Re-encryption complete.")

    except Exception as e:
        print(f"Critical error during re-encryption: {e}")
        raise