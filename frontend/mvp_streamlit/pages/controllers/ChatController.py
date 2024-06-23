import streamlit as st
from . import BaseController


# var_public_bots
# var_sessions
# var_selected_session

@BaseController.with_try_catch
def load_bot_data():
    # load just public bots for now
    resp = BaseController.create_request("GET", "/public/bots", None, with_validation=False)
    if resp.status_code == 200:
        st.session_state.var_public_bots = resp.json()
    else:
        st.error("Failed to load public bots.")
        st.session_state.var_public_bots = []


@BaseController.with_try_catch
def load_session_history():
    resp = BaseController.create_request("GET", "/chat/sessions", None)
    if resp.status_code == 200:
        st.session_state.var_sessions = resp.json()
    else:
        st.error("Failed to load chat history.")
        st.session_state.var_sessions = []


@BaseController.with_try_catch
def load_session(session_id: int):
    session_resp = BaseController.create_request("GET", f"/chat/sessions/{session_id}", None)
    if session_resp.status_code != 200:
        st.error("Failed to load chat history.")
        st.session_state.var_selected_session = None
        return
    message_resp = BaseController.create_request("GET", f"/chat/sessions/{session_id}/messages", None)
    if message_resp.status_code != 200:
        st.error("Failed to load chat history.")
        st.session_state.var_selected_session = None
        return
    st.session_state.var_selected_session = [session_resp.json()["chat_session"], session_resp.json()["bot"], message_resp.json()]


@BaseController.with_try_catch
def create_new_session(selected_bot_index: int):
    resp = BaseController.create_request("POST", "/chat/sessions", {"id_bot": st.session_state.var_public_bots[selected_bot_index]["id"]})
    if resp.status_code == 200:
        st.session_state.var_sessions.insert(0, resp.json())
        load_session(resp.json()["id"])
    else:
        st.error("Failed to create new session.")


@BaseController.with_try_catch
def send_message():
    # read input from st.session_state.var_message_input
    if not st.session_state.var_selected_session or len(st.session_state.var_selected_session) < 3:
        st.warning("No session selected. Create a new session or choose an existing one.")
        return
    resp = BaseController.create_request("POST", f"/chat/sessions/{st.session_state.var_selected_session[0]['id']}/messages", {
        "type": "user-text",
        "content": st.session_state.var_message_input})
    if resp.status_code == 200:
        st.session_state.var_selected_session[2].append(resp.json()["message"])
        st.session_state.var_selected_session[2].append(resp.json()["response"])
    else:
        st.error("Failed to send message.")
        return
