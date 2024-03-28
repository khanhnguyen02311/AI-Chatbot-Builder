import streamlit as st
from pages.controllers import AuthController
from Menu import menu

menu()

with st.form("signup_form"):
    st.markdown("#### Enter your credentials")
    st.text_input("Your name", key="var_name")
    st.text_input("Username", key="var_username")
    st.text_input("Email", key="var_email")
    st.text_input("Password", type="password", key="var_password")
    st.text_input("Confirm your password", type="password", key="var_password_confirm")
    submit = st.form_submit_button("Signup")
    if submit:
        AuthController.signup()
