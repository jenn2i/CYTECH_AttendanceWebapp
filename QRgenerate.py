import streamlit as st
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
import io

key = b'ThisIsASecretKey'  # AES key (16, 24, or 32 bytes)

def encrypt_data(data: str, key: bytes) -> str:
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(data.encode(), AES.block_size))
    encrypted = base64.b64encode(iv + ciphertext).decode()
    return encrypted

def decrypt_data(encrypted_data: str, key: bytes) -> str:
    decoded_data = base64.b64decode(encrypted_data)
    iv = decoded_data[:16]
    ct = decoded_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ct), AES.block_size)
    return plaintext.decode()

def generate_qr_image(data):
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def app():
    st.title("QR Code Generator")
    student_id = st.text_input("Enter Student ID:")

    if student_id and st.button("Generate QR Code"):
        student_json = json.dumps({"id": student_id})
        encrypted = encrypt_data(student_json, key)
        st.success(f"Encrypted data:\n{encrypted}")

        img_buf = generate_qr_image(encrypted)
        st.image(img_buf, caption=f"QR Code for {student_id}", width=200)

if __name__ == "__main__":
    app()