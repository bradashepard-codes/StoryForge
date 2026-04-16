import streamlit as st
from app.db import list_projects, create_project, delete_project, get_feature_counts, get_story_counts_by_project

STATUS_OPTIONS = ["Active", "On Hold", "Complete", "Cancelled"]


def render_dashboard():
    user = st.session_state["user"]
    user_id = user.id

    col_title, col_signout = st.columns([8, 1])
    with col_title:
        st.title("StoryForge")
        st.subheader("My Projects")
    with col_signout:
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
                    if st.button("Open", key=f"open_{project['id']}", use_container_width=True):
                        st.session_state["project_id"] = project["id"]
                        st.session_state["project_name"] = project["name"]
                        st.session_state["view"] = "project"
                        st.rerun()
                    if st.button("Delete", key=f"del_proj_{project['id']}", use_container_width=True):
                        delete_project(project["id"])
                        st.rerun()
    else:
        st.info("No projects yet. Add one below.")

    st.divider()
    st.markdown("#### Add New Project")
    with st.form("new_project_form", clear_on_submit=True):
        name = st.text_input("Project Name")
        owner = st.text_input("Project Owner")
        status = st.selectbox("Status", STATUS_OPTIONS)
        submitted = st.form_submit_button("Add Project", use_container_width=True)

    if submitted:
        if not name or not owner:
            st.error("Project name and owner are required.")
        else:
            create_project(name, owner, status, user_id)
            st.rerun()
