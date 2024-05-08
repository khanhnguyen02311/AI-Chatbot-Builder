import requests
import streamlit as st
from streamlit_chat import message
from pages.controllers import ChatController
from Menu import menu_with_redirect

if "var_selected_session" not in st.session_state:
    st.session_state.var_selected_session = None  # [session_data, bot_data, message_data]

st.set_page_config(page_title="Chat với Bot", layout="wide")

st.title(f"💬 Session: {st.session_state.var_selected_session[0]['name'] if st.session_state.selected_session is not None else 'None'}")
st.subheader(f"Bot: {st.session_state.var_selected_session[1]['name'] if st.session_state.selected_session is not None else 'None'}")
menu_with_redirect()

ChatController.load_bot_data()
ChatController.load_session_history()

st.sidebar.divider()

# new session form & button
with st.sidebar.form("session_list_form"):
    selected_bot_index = st.selectbox("Chọn Bot cho session mới",
                                      range(len(st.session_state.var_public_bots)),
                                      index=None,
                                      format_func=lambda x: st.session_state.var_public_bots[x]["name"])
    submit = st.form_submit_button("Session Chat mới", type="primary")
    if submit:
        if selected_bot_index is not None:
            ChatController.create_new_session(selected_bot_index)
        else:
            st.error("You need to choose a bot.")

st.sidebar.divider()

st.sidebar.subheader("Lịch sử Chat")

# session history
for session in st.session_state.var_sessions:
    st.sidebar.button(f"{session['name']}", use_container_width=True,
                      on_click=lambda session_id=session["id"]: ChatController.load_session(session_id))

st.sidebar.divider()

chat_placeholder = st.empty()

# Display chat messages from history on app rerun
with chat_placeholder.container():
    for i, msg in enumerate(st.session_state.var_selected_session[2] if st.session_state.var_selected_session is not None else []):
        is_user = msg["type"] in ['user-text', 'user-form']
        message(msg["content"],
                is_user=is_user,
                key="msg_" + str(i),
                avatar_style="lorelei" if is_user else "bottts")

# Send user message to backend and display response
with st.container():
    st.text_input("Hỏi bất kì điều gì", key="var_message_input", on_change=ChatController.send_message)
