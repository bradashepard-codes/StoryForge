import streamlit as st
from app.db import list_features, create_feature, delete_feature
from app.llm_client import enhance_feature_description


def render_project():
    user = st.session_state["user"]
    user_id = user.id
    project_id = st.session_state["project_id"]
    project_name = st.session_state.get("project_name", "Project")

    if st.button("← Back", key="back_to_dashboard"):
        st.session_state["view"] = "dashboard"
        st.rerun()
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

    name = st.text_input("Feature Name", key="new_feat_name")
    description = st.text_area("Description (optional)", height=100, key="new_feat_desc")

    enhanced = st.session_state.get("enhanced_description")

    col_enhance, col_clear = st.columns([2, 1])
    with col_enhance:
        if st.button("✨ Enhance Description", use_container_width=True, disabled=not description):
            with st.spinner("Enhancing..."):
                result = enhance_feature_description(description)
            if result:
                st.session_state["enhanced_description"] = result
                st.session_state["original_description"] = description
                st.rerun()
            else:
                st.error("Enhancement failed. Check your API key.")
    with col_clear:
        if enhanced and st.button("Clear Enhancement", use_container_width=True):
            st.session_state.pop("enhanced_description", None)
            st.session_state.pop("original_description", None)
            st.rerun()

    if enhanced:
        st.markdown("**Choose a description:**")
        col_orig, col_enhanced = st.columns(2)
        with col_orig:
            st.markdown("**Original**")
            st.info(st.session_state.get("original_description", description))
        with col_enhanced:
            st.markdown("**Enhanced**")
            st.success(enhanced)

        choice = st.radio(
            "Use which version?",
            ["Enhanced", "Original"],
            horizontal=True,
            key="desc_choice",
        )
        final_description = enhanced if choice == "Enhanced" else st.session_state.get("original_description", description)
    else:
        final_description = description

    if st.button("Add Feature", use_container_width=True, type="primary"):
        if not name:
            st.error("Feature name is required.")
        else:
            create_feature(project_id, name, final_description, user_id)
            st.session_state.pop("enhanced_description", None)
            st.session_state.pop("original_description", None)
            st.rerun()
