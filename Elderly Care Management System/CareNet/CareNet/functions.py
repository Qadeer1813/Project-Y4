import requests
from .config import API_TOKEN, API_ENDPOINTS
from cryptography.fernet import Fernet

# Cache for the encryption key
current_key = None
previous_key = None

def get_headers():
    return {
        "Authorization": f"Bearer {API_TOKEN}"
    }

def get_encryption_key(force_refresh=False):
    global current_key, previous_key

    if force_refresh or current_key is None:
        headers = get_headers()
        response = requests.get(API_ENDPOINTS['current_key'], headers=headers)

        if response.status_code == 200:
            previous_key = current_key
            current_key = response.json()['encryption_key']
            return current_key
        else:
            raise Exception(f"Failed to get encryption key: {response.status_code}")

    return current_key

def refresh_encryption_key():
    global current_key, previous_key

    headers = get_headers()
    rotate_response = requests.post(API_ENDPOINTS['rotate_key'], headers=headers)

    if rotate_response.status_code != 200:
        raise Exception("Failed to rotate key")

    new_key = get_encryption_key(force_refresh=True)

    return new_key

# Encrypt data
def encrypt(data):
    if not data:
        return None

    try:
        key = get_encryption_key().encode()
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data.decode()
    except Exception as e:
        raise Exception(f"Failed to encrypt data: {str(e)}")

# Decrypt the encrypted data
def decrypt(encrypted_data):
    if not encrypted_data:
        return None

    try:
        # First try with current key
        current_encryption_key = get_encryption_key().encode()
        f = Fernet(current_encryption_key)
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception as e:
        # If current key fails, try previous key
        if previous_key:
            try:
                f = Fernet(previous_key.encode())
                decrypted_data = f.decrypt(encrypted_data.encode())
                return decrypted_data.decode()
            except Exception as e:
                print(f"Failed to decrypt with previous key")

        # If both fail, raise the original exception
        raise Exception(f"Failed to decrypt data: {str(e)}")

# Decrypt selected fields of encrypted patient data rows and return them in readable form
def decrypt_patient_data(patient_data):
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
                        decrypted_row.append(decrypt(column))
                    else:
                        decrypted_row.append('')
                except Exception as e:
                    decrypted_row.append("Error decrypting")

        decrypted_patient_data.append(decrypted_row)
    return decrypted_patient_data