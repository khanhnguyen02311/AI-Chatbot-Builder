import requests
import streamlit as st


def _create_request(method: str, path: str, json_data, headers):
    st.session_state.base_url = "http://localhost:8000"
    method = method.upper()
    if method == "GET":
        resp = requests.get(st.session_state.base_url + path, headers=headers)
    elif method == "POST":
        resp = requests.post(st.session_state.base_url + path, json=json_data, headers=headers)
    elif method == "PUT":
        resp = requests.put(st.session_state.base_url + path, json=json_data, headers=headers)
    elif method == "DELETE":
        resp = requests.delete(st.session_state.base_url + path, headers=headers)
    else:
        return None
    return resp


def create_request(method, path, json_data, with_validation=True):
    if with_validation:
        if not st.session_state.logged_in_as or st.session_state.logged_in_as == "":
            st.session_state.action_result_data = [2, "You need to be logged in to perform this action."]
            st.switch_page("Home.py")
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    else:  # without validation
        headers = {}

    resp = _create_request(method, path, json_data, headers)
    if resp is None:
        st.error("Invalid request method.")
        return None

    if with_validation and resp.status_code == 401:  # expired token
        renew_resp = _create_request("PUT", "/auth/renew-token", {}, {"Authorization": f"Bearer {st.session_state.refresh_token}"})
        if renew_resp.status_code == 200:
            # redo the operation
            st.session_state.access_token = renew_resp.json()["access_token"]
            resp = _create_request(method, path, json_data, {"Authorization": f"Bearer {st.session_state.access_token}"})
        else:
            st.session_state.action_result_data = [2, "Expired log in session. Please log in again."]
            st.switch_page("Home.py")

    return resp
