import streamlit as st
from pages.controllers import _AuthController

is_logging_in = False
is_signing_up = False
submit = False

if "logged_in_as" not in st.session_state or "access_token" not in st.session_state or "refresh_token" not in st.session_state:
    st.session_state["logged_in_as"] = ""
    st.session_state["access_token"] = ""
    st.session_state["refresh_token"] = ""

if st.session_state["logged_in_as"] != "":
    st.sidebar.markdown(f"### Logged in as {st.session_state['logged_in_as']}")
    st.sidebar.button("Logout", on_click=_AuthController.logout)
else:
    is_logging_in = st.sidebar.button("Login", use_container_width=True)
    is_signing_up = st.sidebar.button("Signup", use_container_width=True, type="primary")

if is_logging_in:
    with st.form("login_form"):
        st.markdown("#### Enter your credentials")
        st.text_input("Username or email", key="var_username_or_email")
        st.text_input("Password", type="password", key="var_password")
        submit = st.form_submit_button("Login", on_click=_AuthController.login)

elif is_signing_up:
    with st.form("signup_form"):
        st.markdown("#### Enter your credentials")
        st.text_input("Your name", key="var_name")
        st.text_input("Username", key="var_username")
        st.text_input("Email", key="var_email")
        st.text_input("Password", type="password", key="var_password")
        st.text_input("Confirm your password", type="password", key="var_password_confirm")
        submit = st.form_submit_button("Signup", on_click=_AuthController.signup)

else:
    st.title("Chatbot Engine! 👋")
    st.subheader("A place to build, test, and deploy chatbots for your specific needs.")
