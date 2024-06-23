import streamlit as st
from Menu import menu

# -----------------------------------------------------------------------------
# SESSION_STATE VARIABLES:
# base_backend_url:         str:        the base URL of the backend
# action_result_data:       [int, str]: the result of the last action (0: success, 1: warning, 2: error), empty if no action was performed
# var_username_or_email:    str:        the username or email of the user, empty if not logged in
# var_password:             str:        the password of the user, empty if not logged in
# logged_in_as:             str:        the username of the logged in user, empty if not logged in
# access_token:             str:        the access token of the logged in user, empty if not logged in
# refresh_token:            str:        the refresh token of the logged in user, empty if not logged in
# -----------------------------------------------------------------------------

st.set_page_config(page_title="Trang chủ", layout="wide")

st.session_state.action_result_data = None

if "logged_in_as" not in st.session_state or "access_token" not in st.session_state or "refresh_token" not in st.session_state:
    st.session_state["logged_in_as"] = ""
    st.session_state["access_token"] = ""
    st.session_state["refresh_token"] = ""

menu()

# st.title("Chatbot Engine! 👋")
# st.subheader("A place to build, test, and deploy chatbots for your specific needs.")

st.title("BotTouristant xin chào! 👋 ")
st.divider()
st.subheader("BotTouristant là một nền tảng hỗ trợ tham khảo các dịch vụ du lịch, cũng như giải đáp thắc mắc của khách du lịch sử dụng chatbot.")
