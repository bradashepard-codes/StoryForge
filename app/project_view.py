import streamlit as st
from app.db import list_features, create_feature, update_feature, delete_feature, bulk_delete_features
from app.llm_client import enhance_feature_description


def _render_enhance_controls(description: str | None, enhanced_key: str, original_key: str, choice_key: str):
    """Shared enhance/clear controls and side-by-side comparison. Returns the chosen description."""
    description = description or ""
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
            else:
                st.error("Enhancement failed. Check your API key.")
    with col_clear:
        if enhanced and st.button("Clear", key=f"btn_clear_{enhanced_key}", use_container_width=True):
            st.session_state.pop(enhanced_key, None)
            st.session_state.pop(original_key, None)

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


@st.dialog("Add Feature")
def _add_feature_modal(project_id: str, user_id: str):
    name = st.text_input("Feature Name")
    description = st.text_area("Description (optional)", height=100, key="modal_feat_desc")

    final_description = _render_enhance_controls(
        description=description,
        enhanced_key="modal_enhanced_description",
        original_key="modal_original_description",
        choice_key="modal_desc_choice",
    )

    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("Add Feature", use_container_width=True, type="primary"):
            if not name:
                st.error("Feature name is required.")
            else:
                is_enhanced = st.session_state.get("modal_desc_choice") == "Enhanced"
                create_feature(project_id, name, final_description or "", user_id, is_enhanced=is_enhanced)
                for key in ["modal_enhanced_description", "modal_original_description", "modal_desc_choice"]:
                    st.session_state.pop(key, None)
                st.rerun()
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            for key in ["modal_enhanced_description", "modal_original_description", "modal_desc_choice"]:
                st.session_state.pop(key, None)
            st.rerun()


@st.dialog("Edit Feature")
def _edit_feature_modal(feature: dict):
    fid = feature["id"]
    new_name = st.text_input("Feature Name", value=feature["name"])
    current_desc = feature.get("description", "")
    new_desc = st.text_area("Description", value=current_desc, height=100, key=f"modal_edit_desc_{fid}")

    final_desc = _render_enhance_controls(
        description=new_desc,
        enhanced_key="modal_edit_enhanced",
        original_key="modal_edit_original",
        choice_key="modal_edit_choice",
    )

    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("Save", use_container_width=True, type="primary"):
            if not new_name:
                st.error("Feature name is required.")
            else:
                is_enhanced = st.session_state.get("modal_edit_choice") == "Enhanced"
                update_feature(fid, {"name": new_name, "description": final_desc, "is_enhanced": is_enhanced})
                for key in ["modal_edit_enhanced", "modal_edit_original", "modal_edit_choice"]:
                    st.session_state.pop(key, None)
                st.rerun()
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            for key in ["modal_edit_enhanced", "modal_edit_original", "modal_edit_choice"]:
                st.session_state.pop(key, None)
            st.rerun()


@st.dialog("Bulk Delete Features")
def _bulk_delete_modal(features: list):
    st.caption("Select the features you want to permanently delete. This cannot be undone.")

    selected_ids = []
    for feature in features:
        if st.checkbox(feature["name"], key=f"bulk_del_{feature['id']}"):
            selected_ids.append(feature["id"])

    st.divider()
    col_delete, col_cancel = st.columns(2)
    with col_delete:
        label = f"Delete ({len(selected_ids)} selected)" if selected_ids else "Delete"
        if st.button(label, use_container_width=True, type="primary", disabled=not selected_ids):
            bulk_delete_features(selected_ids)
            st.rerun()
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


def render_project():
    user = st.session_state["user"]
    user_id = user.id
    project_id = st.session_state["project_id"]
    project_name = st.session_state.get("project_name", "Project")

    if st.button("← Back", key="back_to_dashboard"):
        st.session_state["view"] = "dashboard"
        st.rerun()

    col_title, col_add, col_bulk = st.columns([5, 2, 2])
    with col_title:
        st.title(project_name)
        st.subheader("Features")
    with col_add:
        st.write("")
        st.write("")
        if st.button("+ Add Feature", use_container_width=True, type="primary"):
            _add_feature_modal(project_id, user_id)
    with col_bulk:
        st.write("")
        st.write("")
        features = list_features(project_id)
        if st.button("🗑 Bulk Delete", use_container_width=True, disabled=not features):
            _bulk_delete_modal(features)

    if not features:
        features = list_features(project_id)

    if features:
        for feature in features:
            fid = feature["id"]
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
                    if st.button("Edit", key=f"edit_{fid}", use_container_width=True):
                        _edit_feature_modal(feature)
                    if st.button("Delete", key=f"del_feat_{fid}", use_container_width=True):
                        delete_feature(fid)
                        st.rerun()
    else:
        st.info("No features yet. Click '+ Add Feature' to get started.")
