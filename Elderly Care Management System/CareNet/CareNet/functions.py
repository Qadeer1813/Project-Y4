import requests
from .config import API_TOKEN, API_ENDPOINTS

def get_headers():
    """Return headers with authentication token"""
    return {
        "Authorization": f"Bearer {API_TOKEN}"
    }

# Encrypt the message by calling the API endpoint
def encrypt_message(message):
    # url = 'http://localhost:8001/encrypt'
    headers = get_headers()
    response = requests.post(API_ENDPOINTS['encrypt'], json={"data": message}, headers=headers)
    if response.status_code == 200:
        return response.json()['encrypted_data']
    elif response.status_code == 401:
        raise Exception("Authentication failed - invalid token")
    else:
        raise Exception("Failed to encrypt message")

# Decrypt the encrypted messages which is the patient data
def decrypt_message(encrypted_message):
    # url = 'http://localhost:8001/decrypt'
    headers = get_headers()
    response = requests.post(API_ENDPOINTS['decrypt'], json={"encrypted_data": encrypted_message}, headers=headers)
    if response.status_code == 200:
        return response.json()['decrypted_data']
    elif response.status_code == 401:
        raise Exception("Authentication failed - invalid token")
    else:
        raise Exception("Failed to decrypt message")

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
                        decrypted_row.append(decrypt_message(column))
                    else:
                        decrypted_row.append('')
                except Exception as e:
                    decrypted_row.append("Error decrypting")

        decrypted_patient_data.append(decrypted_row)
    return decrypted_patient_data