import streamlit as st
from . import BaseController


# var_public_bots
# var_sessions
# var_selected_session

def load_bot_data():
    # load just public bots for now
    if "var_public_bots" not in st.session_state:
        resp = BaseController.create_request("GET", "/public/bots", None, with_validation=False)
        if resp.status_code == 200:
            st.session_state.var_public_bots = resp.json()
        else:
            st.error("Failed to load public bots.")
            st.session_state.var_public_bots = []


def load_session_history():
    if "var_sessions" not in st.session_state:
        resp = BaseController.create_request("GET", "/chat/sessions", None)
        if resp.status_code == 200:
            st.session_state.var_sessions = resp.json()
        else:
            st.error("Failed to load chat history.")
            st.session_state.var_sessions = []


def load_session(session_id: int):
    session_resp = BaseController.create_request("GET", f"/chat/sessions/{session_id}", None)
    if session_resp.status_code == 200:
        st.session_state.var_selected_session = [session_resp.json()["chat_session"], session_resp.json()["bot"]]
    else:
        st.error("Failed to load chat history.")
        st.session_state.var_selected_session = None
        return

    message_resp = BaseController.create_request("GET", f"/chat/sessions/{session_id}/messages", None)
    if message_resp.status_code == 200:
        st.session_state.var_selected_session.append(message_resp.json())
    else:
        st.error("Failed to load chat history.")
        st.session_state.var_selected_session = None
        return

    print(st.session_state.var_selected_session)


def create_new_session(selected_bot_index: int):
    resp = BaseController.create_request("POST", "/chat/sessions", {"id_bot": st.session_state.var_public_bots[selected_bot_index]["id"]})
    if resp.status_code == 200:
        st.session_state.var_sessions.insert(0, resp.json())
    else:
        st.error("Failed to create new session.")


def send_message():
    # read input from st.session_state.var_message_input
    resp = BaseController.create_request("POST", f"/chat/sessions/{st.session_state.var_selected_session[0]['id']}/messages", {
        "type": "user-text",
        "content": st.session_state.var_message_input})
    if resp.status_code == 200:
        st.session_state.var_selected_session[2].append(resp.json()["message"])
        st.session_state.var_selected_session[2].append(resp.json()["response"])
    else:
        st.error("Failed to send message.")
        return
