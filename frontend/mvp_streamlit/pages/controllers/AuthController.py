import requests
import streamlit as st
from . import BaseController


def logout():
    st.sidebar.success("Logged out successfully!")
    st.session_state["logged_in_as"] = ""
    st.session_state["access_token"] = ""
    st.session_state["refresh_token"] = ""


def save_credentials(username, access_token, refresh_token):
    st.session_state["logged_in_as"] = username
    st.session_state["access_token"] = access_token
    st.session_state["refresh_token"] = refresh_token
    # BotEditorController.init_testdata(st.session_state)


@BaseController.with_try_catch
def login():
    # if st.session_state.var_username_or_email == "admin" and st.session_state.var_password == "admin":
    #     save_credentials(st.session_state.var_username_or_email, "access_token_temp", "refresh_token_temp")
    #     st.session_state.action_result_data = [0, "Logged in successfully!"]
    #     st.switch_page("Home.py")
    # else:
    #     st.sidebar.error("Invalid credentials!")

    if st.session_state.var_username_or_email == "" or st.session_state.var_password == "":
        st.sidebar.error("Please fill in all fields!")
        return
    resp = BaseController.create_request("POST", "/auth/login", {
        "username_or_email": st.session_state.var_username_or_email,
        "password": st.session_state.var_password
    }, with_validation=False)

    if resp.status_code == 401:
        st.sidebar.error("Invalid credentials!")
        return
    if resp.status_code != 200:
        st.sidebar.error("Failed to log in. Please try again.")
        return

    save_credentials(st.session_state.var_username_or_email, resp.json()["access_token"], resp.json()["refresh_token"])
    st.session_state.action_result_data = [0, "Logged in successfully!"]
    st.switch_page("Home.py")


@BaseController.with_try_catch
def signup():
    # if st.session_state.var_username == "admin" and st.session_state.var_password == "admin":
    #     save_credentials(st.session_state.var_username, "access_token_temp", "refresh_token_temp")
    #     st.session_state.action_result_data = [0, "Signed up successfully!"]
    #     st.switch_page("Home.py")

    if st.session_state.var_password != st.session_state.var_password_confirm:
        st.sidebar.error("Passwords do not match!")
        return
    if st.session_state.var_username == "" or st.session_state.var_email == "" or st.session_state.var_password == "" or st.session_state.var_password_confirm == "":
        st.sidebar.error("Please fill in all fields!")
        return

    resp = BaseController.create_request("POST", "/auth/signup", {
        "username": st.session_state.var_username,
        "password": st.session_state.var_password,
        "email": st.session_state.var_email}, with_validation=False)

    if resp.status_code == 401:
        st.sidebar.error("Username or email already exists!")
        return
    if resp.status_code == 422:
        st.sidebar.error("Invalid user format!")
        return
    if resp.status_code != 200:
        st.sidebar.error("Failed to sign up. Please try again.")
        return

    st.session_state.action_result_data = [0, "Signed up successfully!"]

    st.switch_page("pages/Login.py")
