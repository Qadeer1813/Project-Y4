import mysql.connector
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
