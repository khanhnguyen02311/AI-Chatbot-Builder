import requests
import streamlit as st
from pages.controllers import BotBuilderController
from Menu import menu_with_redirect


@st.experimental_dialog("Tải bộ dữ liệu mới")
def ui_new_context_dialog():
    st.write("Chọn file dữ liệu mới để tải lên \n(chỉ hỗ trợ file .txt, .doc, .docx, .pdf)")
    uploaded_file = st.file_uploader("Chọn file", type=["txt", "doc", "docx", "pdf"])
    description = st.text_area("Tổng quan bộ dữ liệu", height=150)
    if st.button("Tải lên"):
        if uploaded_file is None or description == "":
            st.error("Vui lòng chọn file và nhập thông tin tổng quan của bộ dữ liệu.")
        else:
            filedata = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type, {})}
            BotBuilderController.upload_bot_context(filedata, description)


def update_bot_builder_data():
    st.session_state.var_bot_builder_id = st.session_state.ui_bot_builder_id
    st.session_state.var_bot_builder_name = st.session_state.ui_bot_builder_name
    st.session_state.var_bot_builder_description = st.session_state.ui_bot_builder_description
    st.session_state.var_bot_builder_is_public = st.session_state.ui_bot_builder_is_public
    st.session_state.var_bot_builder_conf_instruction = st.session_state.ui_bot_builder_conf_instruction
    st.session_state.var_bot_builder_conf_model_temperature = st.session_state.ui_bot_builder_conf_model_temperature


def update_selected_bot_index():
    st.session_state.var_selected_personal_bot_index = st.session_state.ui_selected_personal_bot_index


st.set_page_config(page_title="Thiết kế Bot", layout="wide")
st.title("Thiết kế Bot")
st.subheader("Tự cấu hình Bot cho nhu cầu cụ thể của bạn.")


menu_with_redirect()
st.sidebar.divider()

if "var_personal_bots" not in st.session_state:
    BotBuilderController.load_personal_bot_data()
if "var_selected_personal_bot_index" not in st.session_state:
    st.session_state.var_selected_personal_bot_index = None

# pre-allocate selected bot index
if "ui_btn_new_bot" in st.session_state and st.session_state.ui_btn_new_bot:
    st.session_state.var_selected_personal_bot_index = None

st.sidebar.selectbox(
    "Chọn Bot có sẵn của bạn",
    range(len(st.session_state.var_personal_bots)),
    key="ui_selected_personal_bot_index",
    index=st.session_state.var_selected_personal_bot_index,
    on_change=update_selected_bot_index,
    format_func=lambda x: st.session_state.var_personal_bots[x]["name"],
)

st.sidebar.divider()
st.sidebar.text("Hoặc")
st.sidebar.button("Tạo bot mới", key="ui_btn_new_bot")

# load data based on options
if st.session_state.var_selected_personal_bot_index is not None:
    st.session_state["ui_bot_builder_form_option"] = "update"
    temp_selected_bot = st.session_state.var_personal_bots[st.session_state.var_selected_personal_bot_index]
    st.session_state.var_bot_builder_id = str(temp_selected_bot["id"])
    st.session_state.var_bot_builder_name = temp_selected_bot["name"]
    st.session_state.var_bot_builder_description = temp_selected_bot["description"]
    st.session_state.var_bot_builder_is_public = temp_selected_bot["is_public"]
    st.session_state.var_bot_builder_conf_instruction = temp_selected_bot["conf_instruction"]
    st.session_state.var_bot_builder_conf_model_temperature = temp_selected_bot["conf_model_temperature"]
    BotBuilderController.load_personal_bot_context_data(temp_selected_bot["id"])
else:
    st.session_state["ui_bot_builder_form_option"] = "create"
    st.session_state.var_bot_builder_id = ""
    st.session_state.var_bot_builder_name = ""
    st.session_state.var_bot_builder_description = ""
    st.session_state.var_bot_builder_is_public = False
    st.session_state.var_bot_builder_conf_instruction = ""
    st.session_state.var_bot_builder_conf_model_temperature = 0.5
    st.session_state.var_personal_bot_contexts = []

with st.form("ui_bot_builder_form"):
    if st.session_state.ui_bot_builder_form_option == "create":
        st.markdown("#### Tạo Bot mới")
    else:
        st.markdown("#### Cập nhật thông tin Bot")

    st.text_input("ID", key="ui_bot_builder_id", disabled=True, value=st.session_state.var_bot_builder_id)
    st.text_input("Tên Bot", key="ui_bot_builder_name", value=st.session_state.var_bot_builder_name)
    st.text_area("Thông tin tổng quan", key="ui_bot_builder_description", value=st.session_state.var_bot_builder_description)
    # st.text_input("Model AI sử dụng")
    st.checkbox("Chế độ công khai", key="ui_bot_builder_is_public", value=st.session_state.var_bot_builder_is_public)
    st.text_area(
        "Chỉ dẫn hành động (prompt)",
        key="ui_bot_builder_conf_instruction",
        value=st.session_state.var_bot_builder_conf_instruction,
        height=200,
    )
    st.slider(
        "Độ sáng tạo (temperature)",
        key="ui_bot_builder_conf_model_temperature",
        value=st.session_state.var_bot_builder_conf_model_temperature,
        min_value=0.0,
        max_value=1.0,
        step=0.05,
    )

    col1, col2, col3 = st.columns([1.5, 1.5, 8])
    with col1:
        submit = st.form_submit_button("Xác nhận thông tin", type="primary", use_container_width=True)
    with col2:
        submit_delete = None
        if st.session_state.ui_bot_builder_form_option == "update":
            submit_delete = st.form_submit_button("Xóa Bot", type="secondary", use_container_width=True)

    if submit:
        update_bot_builder_data()
        if st.session_state.ui_bot_builder_form_option == "create":
            BotBuilderController.create_new_bot()
        else:
            BotBuilderController.update_bot()

    if submit_delete:
        update_bot_builder_data()
        BotBuilderController.delete_bot()

if st.session_state.var_selected_personal_bot_index is not None:
    st.subheader("Danh sách các bộ dữ liệu bổ sung")
    if st.button("Thêm bộ dữ liệu mới"):
        ui_new_context_dialog()

for context_item in st.session_state.var_personal_bot_contexts:
    with st.form("ui_bot_context_form_" + str(context_item["id"])):
        col1, col2 = st.columns([7, 3], vertical_alignment="bottom", gap="medium")
        with col1:
            st.markdown(f"#### {context_item['filename']}")
            new_description = st.text_input("Tổng quan bộ dữ liệu", value=context_item["description"])
        with col2:
            col3, col4, col5 = st.columns([2, 1, 1])
            with col3:
                submit_update_context = st.form_submit_button("Cập nhật thông tin", type="primary", use_container_width=True)
            with col4:
                submit_delete_context = st.form_submit_button("Xoá", type="secondary", use_container_width=True)
            with col5:
                submit_download_context = st.form_submit_button("Tải về", type="secondary", use_container_width=True)

        if submit_update_context:
            BotBuilderController.update_bot_context(context_item["id"], new_description)
        if submit_delete_context:
            BotBuilderController.delete_bot_context(context_item["id"])
        if submit_download_context:
            pass
            # BotBuilderController.download_bot_context(context_item["id"])


# if st.session_state.var_selected_personal_bot_index is not None:
#     bot = st.session_state.var_personal_bots[st.session_state.var_selected_personal_bot_index]

#     st.write(bot)
#     st.write(bot["name"])
#     st.write(bot["description"])
#     st.write(bot["is_public"])
#     st.write(bot["instruction"])
#     st.write(bot["temperature"])
#     st.write(bot["model"])
