# from streamlit_extras.switch_page_button import switch_page
import streamlit as st
from pages.controllers import AuthController


def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("Home.py", label="Home")
    # st.sidebar.page_link("pages/BotViewer.py", label="Bot Viewer")
    # st.sidebar.page_link("pages/BotEditor.py", label="Bot Editor")
    st.sidebar.page_link("pages/BotTravelViewer.py", label="Travel Assistant")

    st.sidebar.markdown(f"### Logged in as {st.session_state['logged_in_as']}")
    st.sidebar.button("Logout", on_click=AuthController.logout)

    # if st.session_state.role in ["admin", "super-admin"]:
    #     st.sidebar.page_link("pages/admin.py", label="Manage users")
    #     st.sidebar.page_link(
    #         "pages/super-admin.py",
    #         label="Manage admin access",
    #         disabled=st.session_state.role != "super-admin",
    #     )


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("Home.py", label="Home")
    # st.sidebar.page_link("pages/Login.py", label="Login")
    # st.sidebar.page_link("pages/Signup.py", label="Signup")
    login_button = st.sidebar.button("Login", use_container_width=True)
    signup_button = st.sidebar.button("Signup", use_container_width=True, type="primary")
    if login_button:
        st.switch_page("pages/Login.py")
    if signup_button:
        st.switch_page("pages/Signup.py")


def menu():
    # Check if there is an action result to display notifications
    if "action_result_data" in st.session_state and st.session_state.action_result_data is not None:
        if st.session_state.action_result_data[0] == 0:
            st.sidebar.success(st.session_state.action_result_data[1])
        elif st.session_state.action_result_data[0] == 1:
            st.sidebar.warning(st.session_state.action_result_data[1])
        else:
            st.sidebar.error(st.session_state.action_result_data[1])
        st.session_state.action_result_data = None
    # Determine if a user is logged in or not, then show the correct navigation menu
    if "logged_in_as" not in st.session_state or st.session_state["logged_in_as"] == "":
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to render the navigation menu
    if "logged_in_as" not in st.session_state or st.session_state["logged_in_as"] == "":
        st.warning("You are not logged in! Please log in to use this feature.")
        back_button = st.button("Back to Homepage")
        if back_button:
            st.switch_page("Home.py")
        st.stop()
    menu()
