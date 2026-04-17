import streamlit as st
from app.db import list_projects, create_project, update_project, delete_project, get_feature_counts, get_story_counts_by_project

STATUS_OPTIONS = ["Active", "On Hold", "Complete", "Cancelled"]


@st.dialog("Add Project")
def _add_project_modal(user_id: str):
    name = st.text_input("Project Name")
    owner = st.text_input("Project Owner")
    status = st.selectbox("Status", STATUS_OPTIONS)

    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("Add Project", use_container_width=True, type="primary"):
            if not name or not owner:
                st.error("Project name and owner are required.")
            else:
                create_project(name, owner, status, user_id)
                st.rerun()
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Edit Project")
def _edit_project_modal(project: dict):
    new_name = st.text_input("Project Name", value=project["name"])
    new_owner = st.text_input("Project Owner", value=project["owner"])
    current_index = STATUS_OPTIONS.index(project["status"]) if project["status"] in STATUS_OPTIONS else 0
    new_status = st.selectbox("Status", STATUS_OPTIONS, index=current_index)

    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("Save", use_container_width=True, type="primary"):
            if not new_name or not new_owner:
                st.error("Name and owner are required.")
            else:
                update_project(project["id"], {"name": new_name, "owner": new_owner, "status": new_status})
                st.rerun()
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


def render_dashboard():
    user = st.session_state["user"]
    user_id = user.id

    col_title, col_add, col_signout = st.columns([6, 2, 1])
    with col_title:
        st.title("StoryForge")
        st.subheader("My Projects")
    with col_add:
        st.write("")
        st.write("")
        if st.button("+ New Project", use_container_width=True, type="primary"):
            _add_project_modal(user_id)
    with col_signout:
        st.write("")
        st.write("")
        if st.button("Sign Out", use_container_width=True):
            from app.db import sign_out
            sign_out()
            for key in ["session", "user", "view", "project_id", "feature_id"]:
                st.session_state.pop(key, None)
            st.rerun()

    projects = list_projects(user_id)
    feature_counts = get_feature_counts()
    story_counts = get_story_counts_by_project()

    if projects:
        for project in projects:
            pid = project["id"]
            feat_count = feature_counts.get(pid, 0)
            story_count = story_counts.get(pid, 0)

            with st.container(border=True):
                col_info, col_actions = st.columns([7, 2])
                with col_info:
                    st.markdown(f"**{project['name']}**")
                    st.caption(
                        f"Owner: {project['owner']}  |  Status: {project['status']}  |  "
                        f"Features: {feat_count}  |  Stories: {story_count}"
                    )
                with col_actions:
                    if st.button("Open", key=f"open_{pid}", use_container_width=True):
                        st.session_state["project_id"] = pid
                        st.session_state["project_name"] = project["name"]
                        st.session_state["view"] = "project"
                        st.rerun()
                    if st.button("Edit", key=f"edit_{pid}", use_container_width=True):
                        _edit_project_modal(project)
                    if st.button("Delete", key=f"del_proj_{pid}", use_container_width=True):
                        delete_project(pid)
                        st.rerun()
    else:
        st.info("No projects yet. Click '+ New Project' to get started.")
