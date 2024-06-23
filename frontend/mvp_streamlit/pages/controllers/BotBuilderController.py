import streamlit as st
from . import BaseController


@BaseController.with_try_catch
def load_personal_bot_data():
    # load just public bots for now
    resp = BaseController.create_request("GET", "/user/bots", None)
    if resp.status_code == 200:
        st.session_state.var_personal_bots = resp.json()
    else:
        st.error("Failed to load personal bots. Error: " + resp.text)
        st.session_state.var_personal_bots = []

def load_personal_bot_context_data(id_bot):
    resp = BaseController.create_request("GET", f"/user/bots/{id_bot}/contexts", None)
    if resp.status_code == 200:
        st.session_state.var_personal_bot_contexts = resp.json()
    else:
        st.error("Failed to load personal bot contexts. Error: " + resp.text)
        st.session_state.var_personal_bot_contexts = []


@BaseController.with_try_catch
def create_new_bot():
    data = {
        "name": st.session_state.var_bot_builder_name,
        "description": st.session_state.var_bot_builder_description,
        "is_public": st.session_state.var_bot_builder_is_public,
        "conf_instruction": st.session_state.var_bot_builder_conf_instruction,
        "conf_model_temperature": st.session_state.var_bot_builder_conf_model_temperature,
        "conf_model_name": "gpt-3.5-turbo-1106",
    }
    resp = BaseController.create_request("POST", "/user/bots", data, with_validation=True)
    if resp.status_code == 200:
        st.session_state.var_personal_bots.append(resp.json())
        st.session_state.var_selected_personal_bot_index = len(st.session_state.var_personal_bots) - 1
        st.session_state.ui_bot_builder_form_option = "update"
        st.session_state.action_result_data = (0, "Bot created successfully.")
        st.rerun()
    else:
        st.error("Failed to create bot. Error: " + resp.text)


@BaseController.with_try_catch
def update_bot():
    resp = BaseController.create_request("PUT", f"/user/bots/{st.session_state.var_bot_builder_id}", {
        "name": st.session_state.var_bot_builder_name,
        "description": st.session_state.var_bot_builder_description,
        "is_public": st.session_state.var_bot_builder_is_public,
        "conf_instruction": st.session_state.var_bot_builder_conf_instruction,
        "conf_model_temperature": st.session_state.var_bot_builder_conf_model_temperature,
        "conf_model_name": "gpt-3.5-turbo-1106",
    }, with_validation=True)
    if resp.status_code == 200:
        st.session_state.var_personal_bots[st.session_state.var_selected_personal_bot_index] = resp.json()
        st.session_state.action_result_data = (0, "Bot updated successfully.")
        st.rerun()
    else:
        st.error("Failed to update bot. Error: " + resp.text)
        # st.error("Failed to update bot. Error: " + resp.text)


@BaseController.with_try_catch
def delete_bot():
    resp = BaseController.create_request("DELETE", f"/user/bots/{st.session_state.var_bot_builder_id}", None)
    if resp.status_code == 200:
        st.session_state.action_result_data = (0, "Bot deleted successfully.")
        st.session_state.var_personal_bots.pop(st.session_state.var_selected_personal_bot_index)
        st.session_state.var_selected_personal_bot_index = None
        st.session_state.ui_bot_builder_form_option = "create"
        st.rerun()
    else:
        st.error("Failed to delete bot. Error: " + resp.text)


def upload_bot_context(filedata, description):
    resp1 = BaseController.create_request("POST", f"/user/bots/{st.session_state.var_bot_builder_id}/contexts", filedata, data_type="files")
    if resp1.status_code != 200:
        st.error("Failed to upload file. Error: " + resp1.text)
        return
    resp2 = BaseController.create_request("PUT", f"/user/bots/{st.session_state.var_bot_builder_id}/contexts/{resp1.json()["id"]}", {
        "description": description
    })
    if resp2.status_code != 200:
        st.warning("Upload file successfully, but failed to update description. Error: " + resp2.text)
        return
    st.session_state.var_personal_bot_contexts.append(resp2.json())
    st.session_state.action_result_data = (0, "Context uploaded successfully.")
    st.rerun()
    # st.session_state.action_result_data = (0, "Context uploaded successfully.")


@BaseController.with_try_catch
def update_bot_context(bot_context_id: int, new_description: str):
    resp = BaseController.create_request("PUT", f"/user/bots/{st.session_state.var_bot_builder_id}/contexts/{bot_context_id}", {
        "description": new_description
    })
    if resp.status_code != 200:
        st.error("Failed to update context description. Error: " + resp.text)
    for idx, bot_context in enumerate(st.session_state.var_personal_bot_contexts):
        if bot_context["id"] == bot_context_id:
            st.session_state.var_personal_bot_contexts[idx] = resp.json()
            break
    st.session_state.action_result_data = (0, "Context updated successfully.")
    st.rerun()


@BaseController.with_try_catch
def delete_bot_context(bot_context_id: int):
    resp = BaseController.create_request("DELETE", f"/user/bots/{st.session_state.var_bot_builder_id}/contexts/{bot_context_id}", None)
    if resp.status_code != 200:
        st.error("Failed to delete context. Error: " + resp.text)
    for idx, bot_context in enumerate(st.session_state.var_personal_bot_contexts):
        if bot_context["id"] == bot_context_id:
            st.session_state.var_personal_bot_contexts.pop(idx)
            break
    st.session_state.action_result_data = (0, "Context deleted successfully.")
    st.rerun()

@BaseController.with_try_catch
def download_bot_context(bot_context_id: int):
    # resp = BaseController.create_request("GET", f"/user/bots/{st.session_state.var_bot_builder_id}/contexts/{bot_context_id}", None)
    # if resp.status_code != 200:
    #     st.error("Failed to download context. Error: " + resp.text)
    #     return None
    pass