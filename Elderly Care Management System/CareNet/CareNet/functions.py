import requests
from .config import API_TOKEN, API_ENDPOINTS
from cryptography.fernet import Fernet

# Cache for the encryption key
current_key = None

def get_headers():
    return {
        "Authorization": f"Bearer {API_TOKEN}"
    }

def get_encryption_key():
    global current_key

    # Return cached key if available
    if current_key:
        return current_key

    # Fetch new key from server
    headers = get_headers()
    response = requests.get(API_ENDPOINTS['current_key'], headers=headers)

    if response.status_code == 200:
        _current_key = response.json()['encryption_key']
        return _current_key
    elif response.status_code == 401:
        raise Exception("Authentication failed - invalid token")
    else:
        raise Exception(f"Failed to get encryption key: {response.status_code}")

def refresh_encryption_key():
    global current_key
    current_key = None
    return get_encryption_key()

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
        key = get_encryption_key().encode()
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception as e:
        try:
            key = refresh_encryption_key().encode()
            f = Fernet(key)
            decrypted_data = f.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except:
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