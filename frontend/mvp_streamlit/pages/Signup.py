import streamlit as st
from pages.controllers import AuthController
from Menu import menu

menu()

# st.session_state.var_username = ""
# st.session_state.var_email = ""
# st.session_state.var_password = ""
# st.session_state.var_password_confirm = ""

with st.form("signup_form"):
    st.markdown("#### Tạo tài khoản mới")
    # st.text_input("Your name", key="var_name")
    st.text_input("Tên tài khoản mới", key="var_username")
    st.text_input("Email", key="var_email")
    st.text_input("Mật khẩu", type="password", key="var_password")
    st.text_input("Xác nhận mật khẩu", type="password", key="var_password_confirm")
    submit = st.form_submit_button("Đăng ký")
    if submit:
        AuthController.signup()
