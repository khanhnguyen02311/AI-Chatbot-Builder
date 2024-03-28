import streamlit as st
from streamlit_chat import message
from pages.controllers import BotEditorController, AuthController
from Menu import menu_with_redirect


def on_new_msg():
    st.session_state["var_messages_" + selected_bot].append({"content": st.session_state["var_input_" + selected_bot], "is_user": True})
    st.session_state["var_input_" + selected_bot] = ""
    st.session_state["var_messages_" + selected_bot].append({"content": "Hello! I'm a chatbot.", "is_user": False})


st.set_page_config(page_title="Bot Viewer")
st.title("💬 Bot Viewer")
menu_with_redirect()

selected_bot = st.sidebar.selectbox("Select a bot", BotEditorController.get_bot_list(st.session_state))
if selected_bot != "":
    st.session_state["var_selected_bot"] = selected_bot

# Initialize chat history
if "var_messages_" + st.session_state["var_selected_bot"] not in st.session_state:
    st.session_state["var_messages_" + st.session_state["var_selected_bot"]] = []

# Display chat messages from history on app rerun
with st.container() as chat_container:
    for i, msg in enumerate(st.session_state["var_messages_" + st.session_state["var_selected_bot"]]):
        message(msg["content"],
                is_user=msg["is_user"],
                key="msg_" + str(i),
                avatar_style="lorelei" if msg["is_user"] else "bottts")

with st.container():
    st.text_input("Say something", key="var_input_" + st.session_state["var_selected_bot"], on_change=on_new_msg)
#
# if prompt := st.chat_input("Say something"):
#     with st.chat_message("user"):
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         st.markdown(prompt)
#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         st.session_state.messages.append({"role": "assistant", "content": "Hello! I'm a chatbot."})
#         message_placeholder.markdown("Hello! I'm a chatbot.")
