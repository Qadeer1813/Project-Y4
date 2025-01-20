from cryptography.fernet import Fernet

# Encrypt the message using a key, converting the message and returning the encrypted result.
def encrypt_message(message, key):
    fernet = Fernet(key)
    if isinstance(message, str):
        return fernet.encrypt(message.encode())
    return message

# Decrypt the encrypted messages which is the patient data
def decrypt_message(encrypted_message, key):
    if not encrypted_message:
        return ''
    try:
        fernet = Fernet(key)
        if isinstance(encrypted_message, str):
            # If it's already a string, encode it first
            encrypted_message = encrypted_message.encode()
        decrypted = fernet.decrypt(encrypted_message)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return "Error decrypting"

# Decrypt selected fields of encrypted patient data rows and return them in readable form
def decrypt_patient_data(patient_data, key):
    decrypted_patient_data = []
    for data in patient_data:
        decrypted_row = []
        # Convert data to list
        data = list(data)

        for i, column in enumerate(data):
            if i == 0:
                decrypted_row.append(column)
            else:
                try:
                    if column is not None:
                        decrypted_row.append(decrypt_message(column, key))
                    else:
                        decrypted_row.append('')
                except Exception as e:
                    decrypted_row.append("Error decrypting")

        decrypted_patient_data.append(decrypted_row)
        return decrypted_patient_data