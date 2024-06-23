import os
import requests
import streamlit as st


def with_try_catch(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.sidebar.error(f"System error: {e}")
            return None
    return wrapper


def _create_request(method: str, path: str, data_type: str, data, headers):
    if os.environ.get("BACKEND_BASE_URL") is None:
        st.session_state.base_url = "http://localhost:8000"
    else:
        st.session_state.base_url = "http://" + os.environ.get("BACKEND_BASE_URL") + ":" + os.environ.get("BACKEND_PORT")
    if data_type not in ["json", "files"]:
        raise ValueError("Invalid request data type.")
    data_body = {data_type: data}
    method = method.upper()
    if method == "GET":
        resp = requests.get(st.session_state.base_url + path, headers=headers)
    elif method == "POST":
        resp = requests.post(st.session_state.base_url + path, headers=headers, **data_body)
    elif method == "PUT":
        resp = requests.put(st.session_state.base_url + path, headers=headers, **data_body)
    elif method == "DELETE":
        resp = requests.delete(st.session_state.base_url + path, headers=headers, **data_body)
    else:
        return None
    return resp


def create_request(method: str, path: str, dict_data, data_type: str = "json", with_validation=True):
    if with_validation:
        if not st.session_state.logged_in_as or st.session_state.logged_in_as == "":
            st.session_state.action_result_data = [2, "You need to be logged in to perform this action."]
            st.switch_page("Home.py")
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    else:  # without validation
        headers = {}

    resp = _create_request(method, path, data_type, dict_data, headers)
    if resp is None:
        st.sidebar.error("Invalid request method.")
        return None

    if with_validation and resp.status_code == 401:  # expired token
        renew_resp = _create_request("PUT", "/auth/renew-token", "json", {}, {"Authorization": f"Bearer {st.session_state.refresh_token}"})
        if renew_resp.status_code == 200:
            # redo the operation
            st.session_state.access_token = renew_resp.json()["access_token"]
            resp = _create_request(method, path, "json", dict_data, {"Authorization": f"Bearer {st.session_state.access_token}"})
        else:
            st.session_state.action_result_data = [2, "Expired log in session. Please log in again."]
            st.switch_page("Home.py")

    return resp


