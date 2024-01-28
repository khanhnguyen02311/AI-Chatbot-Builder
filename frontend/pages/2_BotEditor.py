import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from pages.controllers import _AuthController, BotEditorController

st.set_page_config(page_title="Bot Viewer")
st.title("🤖 Bot Editor")
BotEditorController.init_testdata(st.session_state)

# check user credentials
if "logged_in_as" not in st.session_state or st.session_state["logged_in_as"] == "":
    st.warning("You are not logged in! Please log in to use this feature.")
    back_button = st.button("Back to Homepage")
    if back_button:
        switch_page("Home")
    st.stop()

bot_list = BotEditorController.get_bot_list(st.session_state) + tuple(["Create new bot..."])
business_field_list = BotEditorController.get_business_field_list()

selected_bot = st.selectbox("Select a bot", bot_list)
if selected_bot != "Create new bot...":
    bot_data = BotEditorController.get_bot_info(st.session_state, selected_bot)
    st.session_state["var_bot_description"] = bot_data["description"]
    st.session_state["var_bot_business_fields"] = bot_data["business_fields"]
    st.session_state["var_bot_business_information"] = bot_data["business_information"]
    st.session_state["var_bot_response_attitude"] = bot_data["response_attitude"]
    st.session_state["var_bot_name"] = selected_bot
    st.session_state["var_bot_existed"] = True
else:
    st.session_state["var_bot_description"] = ""
    st.session_state["var_bot_business_fields"] = []
    st.session_state["var_bot_business_information"] = ""
    st.session_state["var_bot_response_attitude"] = ""
    st.session_state["var_bot_name"] = ""
    st.session_state["var_bot_existed"] = False

chatbot_form = st.form("bot-info")
col1, col2 = chatbot_form.columns([1, 1])

with col1:
    # st.write("""<style>[data="stHorizontalBlock"] {align-items: end;} </style>""", unsafe_allow_html=True)
    st.form_submit_button("Delete bot", use_container_width=True, on_click=BotEditorController.delete_bot, args=(st.session_state, selected_bot))
with col2:
    # st.write("""<style>[data="stHorizontalBlock"] {align-items: end;} </style>""", unsafe_allow_html=True)
    st.form_submit_button("Save", use_container_width=True, type="primary", on_click=BotEditorController.set_bot_info, args=(st.session_state, selected_bot))

chatbot_form.markdown("#### Business Information")
chatbot_form.multiselect("Business Fields", business_field_list, key="var_bot_business_fields")
chatbot_form.text_area("Business Information", key="var_bot_business_information",
                       help="Provide information about your business, such as what it does, what it sells, etc.")

chatbot_form.markdown("#### Chatbot Information")
chatbot_form.text_input("Name", key="var_bot_name", disabled=st.session_state["var_bot_existed"])
chatbot_form.text_area("Description", key="var_bot_description", help="Provide a short description of your chatbot.")
chatbot_form.text_area("Response Attitude", key="var_bot_response_attitude", help="How should your chatbot respond?")

st.sidebar.markdown(f"### Logged in as {st.session_state['logged_in_as']}")
st.sidebar.button("Logout", on_click=_AuthController.logout)
