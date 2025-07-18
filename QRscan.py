import streamlit as st
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import csv
import os
from datetime import datetime, timedelta
import pandas as pd
from PIL import Image

key = b'ThisIsASecretKey'

def record_attendance(student_id, output_file="attendance.csv"):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    if not os.path.exists(output_file):
        with open(output_file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["student_id", "date", "time"])

    with open(output_file, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["student_id"] == student_id and row["date"] == date_str:
                st.warning(f"[!] Student {student_id} has already checked in today.")
                return False

    with open(output_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([student_id, date_str, time_str])
        st.success(f"[✓] Attendance recorded: {student_id} ({date_str} {time_str})")
        return True

def decrypt_qr_data(encoded_data, key):
    try:
        decoded_data = base64.b64decode(encoded_data)
        iv = decoded_data[:16]
        ct = decoded_data[16:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ct), AES.block_size)

        student_info = json.loads(plaintext.decode())
        return student_info.get("id")
    except Exception as e:
        st.error(f"[!] Decryption error: {e}")
        return None

def app():
    qr_image_path = "app.jpg"
    app_url = "https://cosmic-amount-5255.glide.page/dl/f6b5a1"

    st.markdown("### How would you like to scan your QR code?", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🖥️ Using your **web browser**")
        if "last_seen" not in st.session_state:
            st.session_state.last_seen = {}
        if st.button("📷 Scan your QR Code"):
            st.markdown("Please show the QR code to the camera.")
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()

            if not ret:
                st.error("Failed to capture webcam frame.")
            else:
                decoded_objs = decode(frame)
                if not decoded_objs:
                    st.warning("No QR code detected.")
                for obj in decoded_objs:
                    encrypted = obj.data.decode("utf-8")
                    student_id = decrypt_qr_data(encrypted, key)

                    now = datetime.now()
                    cooldown = timedelta(seconds=10)
                    if student_id:
                        if student_id not in st.session_state.last_seen or now - st.session_state.last_seen[student_id] > cooldown:
                            record_attendance(student_id)
                            st.session_state.last_seen[student_id] = now
                        else:
                            st.info(f"Student {student_id} recently scanned, skipping duplicate.")
                    else:
                        st.error("Invalid QR code detected!")

                    # Show frame with bounding box
                    points = obj.polygon
                    if len(points) > 4:
                        hull = cv2.convexHull(np.array([(p.x, p.y) for p in points], dtype=np.float32))
                        hull = list(map(tuple, np.squeeze(hull)))
                    else:
                        hull = [(p.x, p.y) for p in points]

                    for j in range(len(hull)):
                        cv2.line(frame, hull[j], hull[(j + 1) % len(hull)], (0, 255, 0), 2)

                    label = (encrypted[:20] + "...") if encrypted else "Invalid QR"
                    cv2.putText(frame, label, (obj.rect.left, obj.rect.top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame)

    with col2:
        st.markdown("#### 📱 Using your **mobile app**")
        st.image(Image.open(qr_image_path), caption="Scan with your mobile app", width=200)
        st.markdown(
            f"<a href='{app_url}' target='_blank'>👉 Click here to open the app</a>",
            unsafe_allow_html=True
        )

    if st.button("📄 View Attendance Records"):
        if os.path.exists("attendance.csv"):
            df = pd.read_csv("attendance.csv")
            st.dataframe(df)
        else:
            st.warning("No attendance record file found.")
