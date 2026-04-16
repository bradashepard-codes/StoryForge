import streamlit as st
from app.db import list_features, create_feature, delete_feature


def render_project():
    user = st.session_state["user"]
    user_id = user.id
    project_id = st.session_state["project_id"]
    project_name = st.session_state.get("project_name", "Project")

    col_back, col_title = st.columns([1, 8])
    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state["view"] = "dashboard"
            st.rerun()
    with col_title:
        st.title(project_name)
        st.subheader("Features")

    features = list_features(project_id)

    if features:
        for feature in features:
            with st.container(border=True):
                col_info, col_actions = st.columns([7, 2])
                with col_info:
                    st.markdown(f"**{feature['name']}**")
                    if feature.get("description"):
                        st.caption(feature["description"])
                with col_actions:
                    if st.button("Open", key=f"open_{feature['id']}", use_container_width=True):
                        st.session_state["feature_id"] = feature["id"]
                        st.session_state["feature_name"] = feature["name"]
                        st.session_state["view"] = "feature"
                        st.rerun()
                    if st.button("Delete", key=f"del_feat_{feature['id']}", use_container_width=True):
                        delete_feature(feature["id"])
                        st.rerun()
    else:
        st.info("No features yet. Add one below.")

    st.divider()
    st.markdown("#### Add New Feature")
    with st.form("new_feature_form", clear_on_submit=True):
        name = st.text_input("Feature Name")
        description = st.text_area("Description (optional)", height=80)
        submitted = st.form_submit_button("Add Feature", use_container_width=True)

    if submitted:
        if not name:
            st.error("Feature name is required.")
        else:
            create_feature(project_id, name, description, user_id)
            st.rerun()
