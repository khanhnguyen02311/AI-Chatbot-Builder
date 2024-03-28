import streamlit as st
from . import BotEditorController


def logout():
    st.sidebar.success("Logged out successfully!")
    st.session_state["logged_in_as"] = ""
    st.session_state["access_token"] = ""
    st.session_state["refresh_token"] = ""


def save_credentials(username, access_token, refresh_token):
    st.session_state["logged_in_as"] = username
    st.session_state["access_token"] = access_token
    st.session_state["refresh_token"] = refresh_token
    BotEditorController.init_testdata(st.session_state)


def login():
    if st.session_state.var_username_or_email == "admin" and st.session_state.var_password == "admin":
        save_credentials(st.session_state.var_username_or_email, "access_token_temp", "refresh_token_temp")
        st.session_state.action_result_data = [0, "Logged in successfully!"]
        st.switch_page("Home.py")
    else:
        st.sidebar.error("Invalid credentials!")


def signup():
    if st.session_state.var_password != st.session_state.var_password_confirm:
        st.sidebar.error("Passwords do not match!")
        return
    if st.session_state.var_username == "admin" and st.session_state.var_password == "admin":
        save_credentials(st.session_state.var_username, "access_token_temp", "refresh_token_temp")
        st.session_state.action_result_data = [0, "Signed up successfully!"]
        st.switch_page("Home.py")
    else:
        st.sidebar.error("Invalid credentials!")
