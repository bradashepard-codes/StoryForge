import streamlit as st
from app.db import list_features, create_feature, update_feature, delete_feature, bulk_delete_features
from app.llm_client import enhance_feature


def _render_enhance_section(
    current_desc: str,
    current_biz: str,
    current_iu: str,
    enhanced_key: str,
    choice_key: str,
) -> tuple:
    """
    Renders the Enhance Feature button and side-by-side comparison.
    Returns (final_desc, final_biz, final_iu, enhanced_choice).
    enhanced_choice is True/False if the user made a version choice, None if not yet enhanced.
    """
    # Capture button click before reading session state so the result is available
    # in the same rerun.
    clicked = st.button(
        "✨ Enhance Feature",
        key=f"btn_enhance_{enhanced_key}",
        use_container_width=True,
        disabled=not current_desc,
    )

    if clicked:
        try:
            with st.spinner("Enhancing feature..."):
                result = enhance_feature(current_desc, current_biz, current_iu)
            st.session_state[enhanced_key] = result
            st.session_state[f"{enhanced_key}_orig"] = {
                "description": current_desc,
                "business_objective": current_biz,
                "intended_user": current_iu,
            }
        except Exception as e:
            st.error(f"Enhancement failed: {type(e).__name__}: {e}")

    enhanced = st.session_state.get(enhanced_key)

    if enhanced:
        if st.button("Clear Enhancement", key=f"btn_clear_{enhanced_key}", use_container_width=True):
            st.session_state.pop(enhanced_key, None)
            st.session_state.pop(f"{enhanced_key}_orig", None)
            st.session_state.pop(choice_key, None)
            enhanced = None

    if not enhanced:
        return current_desc, current_biz, current_iu, None

    original = st.session_state.get(f"{enhanced_key}_orig", {})

    st.markdown("**Choose a version:**")
    col_orig, col_enh = st.columns(2)
    with col_orig:
        st.markdown("**Original**")
        with st.container(border=True):
            st.markdown(f"**Description**\n\n{original.get('description', '')}")
            if original.get("business_objective"):
                st.markdown(f"**Business Objective**\n\n{original.get('business_objective')}")
            if original.get("intended_user"):
                st.markdown(f"**Intended User**\n\n{original.get('intended_user')}")
    with col_enh:
        st.markdown("**Enhanced**")
        with st.container(border=True):
            st.markdown(f"**Description**\n\n{enhanced.get('description', '')}")
            if enhanced.get("business_objective"):
                st.markdown(f"**Business Objective**\n\n{enhanced.get('business_objective')}")
            if enhanced.get("intended_user"):
                st.markdown(f"**Intended User**\n\n{enhanced.get('intended_user')}")

    choice = st.radio("Use which version?", ["Enhanced", "Original"], horizontal=True, key=choice_key)

    if choice == "Enhanced":
        return enhanced.get("description", ""), enhanced.get("business_objective", ""), enhanced.get("intended_user", ""), True
    else:
        orig = st.session_state.get(f"{enhanced_key}_orig", {})
        return orig.get("description", ""), orig.get("business_objective", ""), orig.get("intended_user", ""), False


@st.dialog("Add Feature")
def _add_feature_modal(project_id: str, user_id: str):
    name = st.text_input("Feature Name")
    description = st.text_area("Description", height=100)
    biz_obj = st.text_input("Business Objective (optional)")
    intended_user = st.text_input("Intended End User (optional)")

    final_desc, final_biz, final_iu, enhanced_choice = _render_enhance_section(
        description or "", biz_obj or "", intended_user or "",
        enhanced_key="modal_add_enhanced",
        choice_key="modal_add_choice",
    )

    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("Add Feature", use_container_width=True, type="primary"):
            if not name:
                st.error("Feature name is required.")
            elif not final_desc:
                st.error("Description is required.")
            else:
                create_feature(
                    project_id, name, final_desc, user_id,
                    is_enhanced=enhanced_choice is True,
                    business_objective=final_biz,
                    intended_user=final_iu,
                )
                for key in ["modal_add_enhanced", "modal_add_enhanced_orig", "modal_add_choice"]:
                    st.session_state.pop(key, None)
                st.rerun()
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            for key in ["modal_add_enhanced", "modal_add_enhanced_orig", "modal_add_choice"]:
                st.session_state.pop(key, None)
            st.rerun()


@st.dialog("Edit Feature")
def _edit_feature_modal(feature: dict):
    fid = feature["id"]
    new_name = st.text_input("Feature Name", value=feature["name"])
    new_desc = st.text_area("Description", value=feature.get("description", ""), height=100)
    new_biz = st.text_input("Business Objective (optional)", value=feature.get("business_objective", ""))
    new_iu = st.text_input("Intended End User (optional)", value=feature.get("intended_user", ""))

    final_desc, final_biz, final_iu, enhanced_choice = _render_enhance_section(
        new_desc or "", new_biz or "", new_iu or "",
        enhanced_key="modal_edit_enhanced",
        choice_key="modal_edit_choice",
    )

    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("Save", use_container_width=True, type="primary"):
            if not new_name:
                st.error("Feature name is required.")
            elif not final_desc:
                st.error("Description is required.")
            else:
                # Preserve existing is_enhanced if the user didn't make a new choice
                if enhanced_choice is not None:
                    is_enhanced = enhanced_choice
                else:
                    is_enhanced = feature.get("is_enhanced", False)
                update_feature(fid, {
                    "name": new_name,
                    "description": final_desc,
                    "is_enhanced": is_enhanced,
                    "business_objective": final_biz,
                    "intended_user": final_iu,
                })
                for key in ["modal_edit_enhanced", "modal_edit_enhanced_orig", "modal_edit_choice"]:
                    st.session_state.pop(key, None)
                st.rerun()
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            for key in ["modal_edit_enhanced", "modal_edit_enhanced_orig", "modal_edit_choice"]:
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
