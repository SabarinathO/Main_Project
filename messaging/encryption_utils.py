import base64
import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.conf import settings

# Ensure AES key is 32 bytes (AES-256 requires a 32-byte key)
def get_aes_key():
    """Ensure AES key is 32 bytes"""
    if isinstance(settings.AES_SECRET_KEY, str):  # If it's a string, encode it
        return hashlib.sha256(settings.AES_SECRET_KEY.encode()).digest()
    return hashlib.sha256(settings.AES_SECRET_KEY).digest()  # If already bytes, hash directly

def encrypt_message(message, key):
    """Encrypt a message using AES-CBC."""
    key = get_aes_key()
    iv = os.urandom(16)  # Generate a random IV
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_message = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted_message).decode()

def decrypt_message(encrypted_message, key):
    """Decrypt an AES encrypted message."""
    try:
        key = get_aes_key()
        encrypted_message = base64.b64decode(encrypted_message)  # Decode Base64
        iv = encrypted_message[:16]  # Extract IV
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_message = unpad(cipher.decrypt(encrypted_message[16:]), AES.block_size).decode()
        return decrypted_message
    except Exception as e:
        print(f"Decryption Error: {str(e)}")  # Log error
        return "[Decryption Error]"
