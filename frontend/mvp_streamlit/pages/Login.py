import streamlit as st
from pages.controllers import AuthController
from Menu import menu

menu()

with st.form("login_form"):
    st.markdown("#### Đăng nhập vào BotTouristant")
    st.text_input("Tên tài khoản hoặc Email", key="var_username_or_email")
    st.text_input("Mật khẩu", type="password", key="var_password")
    submit = st.form_submit_button("Đăng nhập")
    if submit:
        AuthController.login()
