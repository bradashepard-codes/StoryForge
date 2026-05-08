import streamlit as st
from app.db import list_stories, save_story, update_story, delete_story, get_feature
from app.prompts import build_improved_prompt, build_fanout_prompt, build_risk_signals_prompt
from app.llm_client import call_improved, call_fanout, call_risk_signals, suggest_fanout_context
from app.parser import parse_output, parse_fanout_output, parse_risk_signals_output

SOURCE_BADGE = {
    "A": "⭐ AI-Generated",
    "M": "✍️ Manual",
    "E": "✏️ Edited",
}


def _story_label(story: dict) -> str:
    badge = SOURCE_BADGE.get(story.get("source", "M"), "✍️ Manual")
    title = story.get("title") or story.get("user_story", "")[:60] or "Story"
    return f"{badge} — {title}"


@st.dialog("Generate All Stories")
def _fanout_modal(feature: dict, feature_id: str, user_id: str):
    biz_obj = feature.get("business_objective", "")
    intended_user = feature.get("intended_user", "")
    missing_context = not biz_obj or not intended_user

    ctx_key = f"fanout_ctx_{feature_id}"
    if ctx_key not in st.session_state:
        with st.spinner("Inferring context from feature description..."):
            suggestions = suggest_fanout_context(
                feature.get("name", ""),
                feature.get("description", ""),
            ) or {}
        st.session_state[ctx_key] = suggestions
        st.session_state["fanout_biz_rules"] = suggestions.get("business_rules", "")
        st.session_state["fanout_notes"] = suggestions.get("notes", "")

    if missing_context:
        st.warning("Business Objective and Intended End User are not set on this feature. Fill them in below or update the feature first.")
        biz_obj = st.text_input("Business Objective *(required)*", value=biz_obj)
        intended_user = st.text_input("Intended End User *(required)*", value=intended_user)
    else:
        st.caption(f"Business Objective: {biz_obj}  |  Intended User: {intended_user}")

    st.markdown("**Business Rules or Constraints**")
    tab_rules_preview, tab_rules_edit = st.tabs(["Preview", "Edit"])
    with tab_rules_preview:
        val = st.session_state.get("fanout_biz_rules", "")
        st.markdown(val) if val else st.caption("No business rules provided.")
    with tab_rules_edit:
        st.text_area("", key="fanout_biz_rules", height=120, label_visibility="collapsed")

    st.markdown("**Additional Notes**")
    tab_notes_preview, tab_notes_edit = st.tabs(["Preview", "Edit"])
    with tab_notes_preview:
        val = st.session_state.get("fanout_notes", "")
        st.markdown(val) if val else st.caption("No additional notes provided.")
    with tab_notes_edit:
        st.text_area("", key="fanout_notes", height=80, label_visibility="collapsed")

    col_gen, col_cancel = st.columns([2, 1])
    with col_gen:
        if st.button("🚀 Generate", type="primary", use_container_width=True, key="btn_fanout_modal_generate"):
            if not biz_obj or not intended_user:
                st.error("Business objective and intended user are required.")
            else:
                feature_input = {
                    "feature_name": feature.get("name", ""),
                    "feature_description": feature.get("description", ""),
                    "business_objective": biz_obj,
                    "intended_user": intended_user,
                    "business_rules": st.session_state.get("fanout_biz_rules", ""),
                    "notes": st.session_state.get("fanout_notes", ""),
                }
                with st.spinner("Decomposing feature into stories..."):
                    system_prompt, user_message = build_fanout_prompt(feature_input)
                    raw = call_fanout(system_prompt, user_message)

                if raw is None:
                    st.error("Generation failed. Check your API key and network connection.")
                else:
                    packages = parse_fanout_output(raw)
                    if packages is None:
                        st.error("Failed to parse the generated stories. Try again.")
                    else:
                        count = len(packages)
                        st.session_state["fanout_stories"] = [p.model_dump() for p in packages]
                        st.session_state["fanout_count"] = count
                        for i in range(count):
                            st.session_state[f"fanout_sel_{i}"] = True
                        st.rerun()
    with col_cancel:
        if st.button("Cancel", use_container_width=True, key="btn_fanout_modal_cancel"):
            st.rerun()


def _render_fanout_preview(feature_id: str, user_id: str):
    fanout_stories = st.session_state.get("fanout_stories")
    if fanout_stories is None:
        return

    count = st.session_state.get("fanout_count", len(fanout_stories))
    st.divider()
    st.markdown(f"#### Generated Stories — {count} stories")
    st.caption("Deselect any stories you don't want to save, then click Save Selected.")

    for i, story in enumerate(fanout_stories):
        label = f"⭐ AI-Generated — {story.get('title') or f'Story {i + 1}'}"
        with st.container(border=True):
            keep = st.checkbox(f"Include Story {i + 1}", value=st.session_state.get(f"fanout_sel_{i}", True), key=f"fanout_sel_{i}")
            if keep:
                st.markdown(f"**{label}**")
                ac = story.get("acceptance_criteria") or []
                if ac:
                    st.markdown("**Acceptance Criteria**")
                    for criterion in ac:
                        st.markdown(f"- {criterion}")
                confidence = story.get("confidence")
                escalation = story.get("escalation_flag", False)
                if confidence:
                    st.markdown(f"**Confidence:** {confidence.capitalize()}")
                if escalation:
                    st.warning("Escalation recommended — review before sprint entry.")
            else:
                st.markdown(f"~~{label}~~ *(excluded)*")

    col_save, col_discard = st.columns([2, 1])
    with col_save:
        if st.button("Save Selected", key="btn_fanout_save", use_container_width=True, type="primary"):
            saved, failed = 0, 0
            for i, story in enumerate(fanout_stories):
                if st.session_state.get(f"fanout_sel_{i}", True):
                    result = save_story(feature_id, story, user_id, source="A")
                    if result:
                        saved += 1
                    else:
                        failed += 1
            for i in range(count):
                st.session_state.pop(f"fanout_sel_{i}", None)
            st.session_state.pop("fanout_stories", None)
            st.session_state.pop("fanout_count", None)
            if failed == 0:
                st.success(f"{saved} stories saved.")
            else:
                st.warning(f"{saved} saved, {failed} failed.")
            st.rerun()
    with col_discard:
        if st.button("Discard All", key="btn_fanout_discard", use_container_width=True):
            for i in range(count):
                st.session_state.pop(f"fanout_sel_{i}", None)
            st.session_state.pop("fanout_stories", None)
            st.session_state.pop("fanout_count", None)
            st.rerun()


@st.dialog("New User Story")
def _story_modal(feature: dict, feature_id: str, user_id: str):
    biz_obj = feature.get("business_objective", "")
    intended_user = feature.get("intended_user", "")
    missing_context = not biz_obj or not intended_user

    feature_name = feature.get("name", "")
    feature_description = feature.get("description", "")

    feature_title = st.text_input("Feature Title", value=feature_name)
    story_description = st.text_area("Feature Description", value=feature_description, height=100)

    if missing_context:
        st.warning("Business Objective and Intended End User are not set on this feature. Fill them in below or update the feature first.")
        biz_obj = st.text_input("Business Objective *(required)*", value=biz_obj)
        intended_user = st.text_input("Intended End User *(required)*", value=intended_user)
    else:
        st.caption(f"Business Objective: {biz_obj}  |  Intended User: {intended_user}")

    business_rules = st.text_area("Business Rules or Constraints (optional)", height=80)
    notes = st.text_area("Additional Notes (optional)", height=60)

    col_generate, col_cancel = st.columns([2, 1])
    with col_generate:
        if st.button("Generate Story", use_container_width=True, type="primary", key="btn_modal_generate"):
            if not story_description or not biz_obj or not intended_user:
                st.error("Feature description, business objective, and intended user are required.")
            else:
                feature_input = {
                    "feature_name": feature_title,
                    "feature_description": story_description,
                    "business_objective": biz_obj,
                    "intended_user": intended_user,
                    "business_rules": business_rules,
                    "notes": notes,
                }
                with st.spinner("Generating story..."):
                    system_prompt, user_message = build_improved_prompt(feature_input)
                    raw = call_improved(system_prompt, user_message)

                if raw is None:
                    st.error("Generation failed. Check your API key and network connection.")
                else:
                    parsed = parse_output(raw)
                    if parsed is None:
                        st.error("Failed to parse the generated output. Try again.")
                    else:
                        saved = save_story(feature_id, parsed.model_dump(), user_id, source="A")
                        if saved:
                            st.rerun()
                        else:
                            st.error("Story generated but could not be saved.")
    with col_cancel:
        if st.button("Cancel", use_container_width=True, key="btn_modal_cancel"):
            st.rerun()


@st.dialog("Edit Story")
def _edit_story_modal(story: dict):
    story_id = story["id"]

    title = st.text_input("Title", value=story.get("title", ""))
    user_story_text = st.text_area("User Story", value=story.get("user_story", ""), height=100)

    ac = story.get("acceptance_criteria") or []
    ac_text = st.text_area(
        "Acceptance Criteria (one per line)",
        value="\n".join(ac),
        height=120,
    )

    missing_info = story.get("missing_information") or []
    missing_text = st.text_area(
        "Missing Information (one per line)",
        value="\n".join(missing_info),
        height=80,
    )

    assumptions = story.get("assumptions") or []
    assumptions_text = st.text_area(
        "Assumptions (one per line)",
        value="\n".join(assumptions),
        height=80,
    )

    confidence = st.selectbox(
        "Confidence",
        options=["low", "medium", "high"],
        index=["low", "medium", "high"].index(story.get("confidence") or "medium"),
    )
    escalation_flag = st.checkbox("Escalation Flag", value=story.get("escalation_flag", False))

    col_save, col_cancel = st.columns([2, 1])
    with col_save:
        if st.button("Save Changes", use_container_width=True, type="primary", key="btn_edit_save"):
            updates = {
                "title": title,
                "user_story": user_story_text,
                "acceptance_criteria": [line.strip() for line in ac_text.splitlines() if line.strip()],
                "missing_information": [line.strip() for line in missing_text.splitlines() if line.strip()],
                "assumptions": [line.strip() for line in assumptions_text.splitlines() if line.strip()],
                "confidence": confidence,
                "escalation_flag": escalation_flag,
                "source": "E",
            }
            result = update_story(story_id, updates)
            if result:
                st.rerun()
            else:
                st.error("Failed to save. Try again.")
    with col_cancel:
        if st.button("Cancel", use_container_width=True, key="btn_edit_cancel"):
            st.rerun()


def render_feature():
    user = st.session_state["user"]
    user_id = user.id
    feature_id = st.session_state["feature_id"]
    project_name = st.session_state.get("project_name", "Project")

    feature = get_feature(feature_id)
    feature_name = feature.get("name") or st.session_state.get("feature_name", "Feature")

    if st.button("← Back", key="back_to_project"):
        st.session_state["view"] = "project"
        for key in [k for k in list(st.session_state.keys()) if k.startswith(("fanout_", "risk_", "run_risk_"))]:
            st.session_state.pop(key)
        st.rerun()

    col_title, col_gen, col_add, col_sweep = st.columns([3, 2, 2, 2])
    with col_title:
        st.title(feature_name)
        st.caption(f"Project: {project_name}")
    with col_gen:
        if feature.get("is_enhanced", False) and st.session_state.get("fanout_stories") is None:
            st.write("")
            if st.button("🚀 Generate All Stories", use_container_width=True, type="primary", key="btn_fanout_open"):
                _fanout_modal(feature, feature_id, user_id)
    with col_add:
        st.write("")
        if st.button("✍️ Add Story Manually", use_container_width=True, key="btn_add_manual"):
            _story_modal(feature, feature_id, user_id)
    with col_sweep:
        st.write("")
        if st.button("🕵️ Risk Sweep", use_container_width=True, key="btn_risk_sweep"):
            st.session_state["run_risk_sweep"] = True

    st.subheader("User Stories")

    stories = list_stories(feature_id)

    if st.session_state.pop("run_risk_sweep", False) and stories:
        with st.spinner("Running risk sweep across all stories..."):
            for story in stories:
                sid = story["id"]
                if f"risk_signals_{sid}" not in st.session_state:
                    sp, um = build_risk_signals_prompt(
                        story, feature.get("name", ""), feature.get("description", "")
                    )
                    raw = call_risk_signals(sp, um)
                    if raw:
                        result = parse_risk_signals_output(raw)
                        if result:
                            st.session_state[f"risk_signals_{sid}"] = result.model_dump()
        st.rerun()

    if stories:
        for story in stories:
            label = _story_label(story)
            with st.expander(label, expanded=False):
                st.markdown(f"**User Story**\n\n{story['user_story']}")

                ac = story.get("acceptance_criteria") or []
                if ac:
                    st.markdown("**Acceptance Criteria**")
                    for criterion in ac:
                        st.markdown(f"- {criterion}")

                dor = story.get("definition_of_ready") or {}
                if dor:
                    is_ready = dor.get("is_ready", False)
                    status_label = "Ready" if is_ready else "Not Ready"
                    color = "green" if is_ready else "red"
                    st.markdown(f"**DoR Status:** :{color}[{status_label}]")
                    met = dor.get("criteria_met") or []
                    missing = dor.get("criteria_missing") or []
                    if met:
                        st.markdown("**Criteria Met:** " + ", ".join(met))
                    if missing:
                        st.markdown("**Criteria Missing:** " + ", ".join(missing))

                missing_info = story.get("missing_information") or []
                if missing_info:
                    st.markdown("**Missing Information**")
                    for item in missing_info:
                        st.markdown(f"- {item}")

                assumptions = story.get("assumptions") or []
                if assumptions:
                    st.markdown("**Assumptions**")
                    for item in assumptions:
                        st.markdown(f"- {item}")

                confidence = story.get("confidence")
                escalation = story.get("escalation_flag", False)
                if confidence:
                    st.markdown(f"**Confidence:** {confidence.capitalize()}")
                if escalation:
                    st.warning("Escalation recommended — review before sprint entry.")

                signals = st.session_state.get(f"risk_signals_{story['id']}")
                if signals:
                    st.divider()
                    st.markdown("**Risk Signals**")
                    edge_cases = signals.get("edge_cases", [])
                    dependencies = signals.get("dependencies", [])
                    if edge_cases:
                        st.markdown("**Edge Cases**")
                        for item in edge_cases:
                            st.markdown(f"- {item}")
                    if dependencies:
                        st.markdown("**Dependencies**")
                        for item in dependencies:
                            st.markdown(f"- {item}")
                    if st.button("Clear Signals", key=f"clear_signals_{story['id']}"):
                        st.session_state.pop(f"risk_signals_{story['id']}", None)
                        st.rerun()

                col_edit, col_risk, col_delete = st.columns([1, 1, 1])
                with col_edit:
                    if st.button("Edit Story", key=f"edit_story_{story['id']}"):
                        _edit_story_modal(story)
                with col_risk:
                    if st.button("🔬 Risk Signals", key=f"risk_btn_{story['id']}"):
                        with st.spinner("Analyzing..."):
                            sp, um = build_risk_signals_prompt(
                                story, feature.get("name", ""), feature.get("description", "")
                            )
                            raw = call_risk_signals(sp, um)
                        if raw:
                            result = parse_risk_signals_output(raw)
                            if result:
                                st.session_state[f"risk_signals_{story['id']}"] = result.model_dump()
                        st.rerun()
                with col_delete:
                    if st.button("Delete Story", key=f"del_story_{story['id']}"):
                        delete_story(story["id"])
                        st.rerun()
    else:
        st.info("No stories yet. Use the buttons above to get started.")

    _render_fanout_preview(feature_id, user_id)
