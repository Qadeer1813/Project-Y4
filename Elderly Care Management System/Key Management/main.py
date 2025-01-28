from datetime import datetime
import mysql.connector
from cryptography.fernet import Fernet
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Key Management Server")

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            user='root',
            password='Qadeerh03',
            host='localhost',
            database='key_server',
            port=3306
        )
        return conn
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# Pydantic models for request/response
class KeyResponse(BaseModel):
    Key_ID: int
    Is_Valid: bool
    Created_At: datetime

class EncryptRequest(BaseModel):
    data: str

class EncryptResponse(BaseModel):
    encrypted_data: str

class DecryptRequest(BaseModel):
    encrypted_data: str

class DecryptResponse(BaseModel):
    decrypted_data: str

@app.post("/generate-key")
async def generate_key():
    conn = None
    cursor = None
    try:
        # Generate new key using Fernet
        new_key = Fernet.generate_key()

        # Store the raw key bytes encoded as base64
        key_string = new_key.decode()  # Convert bytes to string for storage

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update existing keys
        cursor.execute("UPDATE key_management SET Is_Valid = 0")

        # Insert new key
        cursor.execute(
            "INSERT INTO key_management (Encryption_Key, Is_Valid) VALUES (%s, 1)",
            (key_string,)
        )

        # Commit transaction
        conn.commit()

        return {
            "message": "New key generated successfully",
            "key_id": cursor.lastrowid
        }

    except Exception as e:
        if conn and conn.is_connected():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Key generation failed: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.post("/encrypt", response_model=EncryptResponse)
async def encrypt_data(request: EncryptRequest):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT Encryption_Key FROM key_management WHERE Is_Valid = 1 ORDER BY Created_At DESC LIMIT 1"
        )
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="No valid encryption key found")

        key = result[0].encode()
        f = Fernet(key)
        encrypted_data = f.encrypt(request.data.encode())

        return {"encrypted_data": encrypted_data.decode()}

    finally:
        cursor.close()
        conn.close()


@app.post("/decrypt", response_model=DecryptResponse)
async def decrypt_data(request: DecryptRequest):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT Encryption_Key FROM key_management WHERE Is_Valid = 1 ORDER BY Created_At DESC LIMIT 1"
        )
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="No valid encryption key found")

        try:
            # Attempt decryption
            key = result[0].encode()
            f = Fernet(key)
            decrypted_data = f.decrypt(request.encrypted_data.encode())
            return {"decrypted_data": decrypted_data.decode()}

        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid encrypted data or wrong key")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")

    finally:
        cursor.close()
        conn.close()