import streamlit as st
from app.db import list_features, create_feature, update_feature, delete_feature
from app.llm_client import enhance_feature_description


def _render_enhance_controls(description: str, enhanced_key: str, original_key: str, choice_key: str):
    """Shared enhance/clear controls and side-by-side comparison. Returns the chosen description."""
    enhanced = st.session_state.get(enhanced_key)

    col_enhance, col_clear = st.columns([2, 1])
    with col_enhance:
        if st.button("✨ Enhance Description", key=f"btn_enhance_{enhanced_key}",
                     use_container_width=True, disabled=not description):
            with st.spinner("Enhancing..."):
                result = enhance_feature_description(description)
            if result:
                st.session_state[enhanced_key] = result
                st.session_state[original_key] = description
                st.rerun()
            else:
                st.error("Enhancement failed. Check your API key.")
    with col_clear:
        if enhanced and st.button("Clear", key=f"btn_clear_{enhanced_key}", use_container_width=True):
            st.session_state.pop(enhanced_key, None)
            st.session_state.pop(original_key, None)
            st.rerun()

    if enhanced:
        st.markdown("**Choose a description:**")
        col_orig, col_enh = st.columns(2)
        with col_orig:
            st.markdown("**Original**")
            st.info(st.session_state.get(original_key, description))
        with col_enh:
            st.markdown("**Enhanced**")
            st.success(enhanced)
        choice = st.radio("Use which version?", ["Enhanced", "Original"],
                          horizontal=True, key=choice_key)
        return enhanced if choice == "Enhanced" else st.session_state.get(original_key, description)

    return description


def render_project():
    user = st.session_state["user"]
    user_id = user.id
    project_id = st.session_state["project_id"]
    project_name = st.session_state.get("project_name", "Project")

    if st.button("← Back", key="back_to_dashboard"):
        st.session_state["view"] = "dashboard"
        for key in ["editing_feature_id", "edit_enhanced_description",
                    "edit_original_description", "enhanced_description", "original_description"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.title(project_name)
    st.subheader("Features")

    features = list_features(project_id)

    if features:
        for feature in features:
            fid = feature["id"]
            is_editing = st.session_state.get("editing_feature_id") == fid

            with st.container(border=True):
                col_info, col_actions = st.columns([7, 2])
                with col_info:
                    st.markdown(f"**{feature['name']}**")
                    if feature.get("description"):
                        st.caption(feature["description"])
                with col_actions:
                    if st.button("Open", key=f"open_{fid}", use_container_width=True):
                        st.session_state["feature_id"] = fid
                        st.session_state["feature_name"] = feature["name"]
                        st.session_state["view"] = "feature"
                        st.rerun()
                    edit_label = "Cancel" if is_editing else "Edit"
                    if st.button(edit_label, key=f"edit_{fid}", use_container_width=True):
                        if is_editing:
                            st.session_state.pop("editing_feature_id", None)
                            st.session_state.pop("edit_enhanced_description", None)
                            st.session_state.pop("edit_original_description", None)
                        else:
                            st.session_state["editing_feature_id"] = fid
                            st.session_state.pop("edit_enhanced_description", None)
                            st.session_state.pop("edit_original_description", None)
                        st.rerun()
                    if st.button("Delete", key=f"del_feat_{fid}", use_container_width=True):
                        delete_feature(fid)
                        st.session_state.pop("editing_feature_id", None)
                        st.rerun()

                if is_editing:
                    st.divider()
                    new_name = st.text_input("Feature Name", value=feature["name"],
                                             key=f"edit_name_{fid}")
                    current_desc = st.session_state.get(
                        "edit_original_description", feature.get("description", "")
                    )
                    new_desc = st.text_area("Description", value=current_desc,
                                            height=100, key=f"edit_desc_{fid}")

                    final_desc = _render_enhance_controls(
                        description=new_desc,
                        enhanced_key="edit_enhanced_description",
                        original_key="edit_original_description",
                        choice_key="edit_desc_choice",
                    )

                    if st.button("Save", key=f"save_{fid}", use_container_width=True, type="primary"):
                        if not new_name:
                            st.error("Feature name is required.")
                        else:
                            is_enhanced = st.session_state.get("edit_desc_choice") == "Enhanced"
                            update_feature(fid, {"name": new_name, "description": final_desc, "is_enhanced": is_enhanced})
                            st.session_state.pop("editing_feature_id", None)
                            st.session_state.pop("edit_enhanced_description", None)
                            st.session_state.pop("edit_original_description", None)
                            st.rerun()
    else:
        st.info("No features yet. Add one below.")

    st.divider()
    st.markdown("#### Add New Feature")

    name = st.text_input("Feature Name", key="new_feat_name")
    description = st.text_area("Description (optional)", height=100, key="new_feat_desc")

    final_description = _render_enhance_controls(
        description=description,
        enhanced_key="enhanced_description",
        original_key="original_description",
        choice_key="desc_choice",
    )

    if st.button("Add Feature", use_container_width=True, type="primary"):
        if not name:
            st.error("Feature name is required.")
        else:
            is_enhanced = st.session_state.get("desc_choice") == "Enhanced"
            create_feature(project_id, name, final_description, user_id, is_enhanced=is_enhanced)
            st.session_state.pop("enhanced_description", None)
            st.session_state.pop("original_description", None)
            st.rerun()
