import streamlit as st
from . import BotEditorController


def logout():
    st.sidebar.success("Logged out successfully!")
    st.session_state["logged_in_as"] = ""
    st.session_state["access_token"] = ""
    st.session_state["refresh_token"] = ""


def login():
    if st.session_state.var_username_or_email == "admin" and st.session_state.var_password == "admin":
        st.sidebar.success("Logged in successfully!")
        st.session_state["logged_in_as"] = st.session_state.var_username_or_email
        st.session_state["access_token"] = "access_token_temp"
        st.session_state["refresh_token"] = "refresh_token_temp"
        BotEditorController.init_testdata(st.session_state)
    else:
        st.sidebar.error("Invalid credentials!")


def signup():
    if st.session_state.var_password != st.session_state.var_password_confirm:
        st.sidebar.error("Passwords do not match!")
        return
    if st.session_state.var_username == "admin" and st.session_state.var_password == "admin":
        st.sidebar.success("Logged in successfully!")
        st.session_state["logged_in_as"] = st.session_state.var_username
        st.session_state["access_token"] = "access_token_temp"
        st.session_state["refresh_token"] = "refresh_token_temp"
        BotEditorController.init_testdata(st.session_state)
    else:
        st.sidebar.error("Invalid credentials!")
