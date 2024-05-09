import requests
import streamlit as st
from streamlit_chat import message
from Menu import menu_with_redirect


def on_new_chat():
    st.session_state.var_messages_TravelAssistant = []
    resp = requests.get("http://localhost:8000/model/legacy/new-id")
    if resp.status_code == 200:
        st.session_state.var_id_TravelAssistant = resp.json()["id"]
    else:
        st.warning("Failed to initialize chat. Please try again.")
        st.session_state.var_id_TravelAssistant = None
        st.stop()


def on_new_message():
    st.session_state["var_messages_TravelAssistant"].append({"content": st.session_state["var_input_TravelAssistant"], "is_user": True})
    bot_response = requests.post("http://localhost:8000/model/legacy/travel-model",
                                 json={"user_id": st.session_state.var_id_TravelAssistant, "question": st.session_state["var_input_TravelAssistant"]})
    if bot_response.status_code == 200:
        st.session_state["var_messages_TravelAssistant"].append({"content": bot_response.json()["response"], "is_user": False})
    else:
        st.session_state["var_messages_TravelAssistant"].append({"content": "Sorry, I'm having trouble. Please try again.", "is_user": False})

    # reset input field
    # st.session_state["var_input_TravelAssistant"] = ""


st.set_page_config(page_title="Travel Assistant", layout="wide")
st.title("💬 Travel Assistant")
menu_with_redirect()

new_chat_button = st.button("New chat", type="primary")
if new_chat_button:
    on_new_chat()

chat_placeholder = st.empty()

# Initialize chat history
if "var_id_TravelAssistant" not in st.session_state or st.session_state.var_id_TravelAssistant is None:
    on_new_chat()

# Display chat messages from history on app rerun
with chat_placeholder.container():
    for i, msg in enumerate(st.session_state.var_messages_TravelAssistant):
        message(msg["content"],
                is_user=msg["is_user"],
                key="msg_" + str(i),
                avatar_style="lorelei" if msg["is_user"] else "bottts")

# Send user message to backend and display response


st.chat_input("Say something", key="var_input_TravelAssistant", on_submit=on_new_message)
