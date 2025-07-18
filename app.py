import streamlit as st
import importlib

st.set_page_config(page_title="QR Attendance System", layout="centered")
st.image("logo.png", width=150)
st.title("QR Attendance System")

# 상단에 두 개 버튼 배치
col1, col2 = st.columns(2)

with col1:
    st.markdown("If you don't have your own QR Code:")
    if st.button("QR Code Generator"):
        st.session_state.page = "generate"

with col2:
    st.markdown("If you have your own QR Code:")
    if st.button("QR Code Scanner"):
        st.session_state.page = "scan"

st.markdown("----------------------------------------------")

# 페이지별로 모듈 호출
if st.session_state.page == "generate":
    qr_generate = importlib.import_module("QRgenerate")
    qr_generate.app()

elif st.session_state.page == "scan":
    qr_scan = importlib.import_module("QRscan")
    qr_scan.app()