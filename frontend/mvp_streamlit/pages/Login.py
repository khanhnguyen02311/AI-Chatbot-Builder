import streamlit as st
from pages.controllers import AuthController
from Menu import menu

menu()

with st.form("login_form"):
    st.markdown("#### Enter your credentials")
    st.text_input("Username or email", key="var_username_or_email")
    st.text_input("Password", type="password", key="var_password")
    submit = st.form_submit_button("Login")
    if submit:
        AuthController.login()
