import streamlit as st
from app.db import list_stories, save_story, delete_story, get_feature
from app.prompts import build_improved_prompt, build_fanout_prompt, build_risk_expansion_prompt
from app.llm_client import call_improved, call_fanout, call_risk_expansion, suggest_fanout_context
from app.parser import parse_output, parse_fanout_output, parse_risk_expansion_output

SOURCE_BADGE = {
    "A": "⭐ AI-Generated",
    "M": "✍️ Manual",
    "E": "✏️ Edited",
}

SEVERITY_COLOR = {"high": "red", "medium": "orange", "low": "green"}


def _story_label(story: dict) -> str:
    badge = SOURCE_BADGE.get(story.get("source", "M"), "✍️ Manual")
    title = story.get("title") or story.get("user_story", "")[:60] or "Story"
    return f"{badge} — {title}"


def _render_fanout_section(feature: dict, feature_id: str, user_id: str):
    if not feature.get("is_enhanced", False):
        return

    fanout_stories = st.session_state.get("fanout_stories")

    if fanout_stories is None:
        st.divider()
        st.markdown("#### Generate All Stories")
        st.caption("This feature has an AI-enhanced description. StoryForge can decompose it into a full set of atomic user stories.")

        ctx_key = f"fanout_ctx_{feature_id}"
        if ctx_key not in st.session_state:
            with st.spinner("Inferring context from feature description..."):
                suggestions = suggest_fanout_context(
                    feature.get("name", ""),
                    feature.get("description", ""),
                ) or {}
            st.session_state[ctx_key] = suggestions
            st.session_state.setdefault("fanout_biz_obj", suggestions.get("business_objective", ""))
            st.session_state.setdefault("fanout_intended_user", suggestions.get("intended_user", ""))
            st.session_state.setdefault("fanout_biz_rules", suggestions.get("business_rules", ""))
            st.session_state.setdefault("fanout_notes", suggestions.get("notes", ""))
            st.rerun()

        st.markdown("**Business Objective** *(required)*")
        st.text_area("", key="fanout_biz_obj", height=80, label_visibility="collapsed")

        st.markdown("**Intended End User** *(required)*")
        st.text_input("", key="fanout_intended_user", label_visibility="collapsed")

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

        if st.button("🚀 Generate All Stories", use_container_width=True, type="primary"):
            business_objective = st.session_state.get("fanout_biz_obj", "")
            intended_user = st.session_state.get("fanout_intended_user", "")
            business_rules = st.session_state.get("fanout_biz_rules", "")
            notes = st.session_state.get("fanout_notes", "")
            if not business_objective or not intended_user:
                st.error("Business objective and intended user are required.")
            else:
                feature_input = {
                    "feature_name": feature.get("name", ""),
                    "feature_description": feature.get("description", ""),
                    "business_objective": business_objective,
                    "intended_user": intended_user,
                    "business_rules": business_rules,
                    "notes": notes,
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
    else:
        count = st.session_state.get("fanout_count", len(fanout_stories))
        st.divider()
        st.markdown(f"#### Generated Stories Preview — {count} stories")
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


def _render_risk_expansion_section(feature: dict, feature_id: str):
    risk_key = f"risk_analysis_{feature_id}"
    analysis = st.session_state.get(risk_key)

    st.divider()
    st.markdown("#### Analyze Risks & Requirements")

    if analysis is None:
        st.caption(
            "Surface edge cases, dependencies, ambiguities, and missing requirements "
            "to strengthen readiness before sprint planning."
        )

        with st.form("risk_expansion_form"):
            business_objective = st.text_input("Business Objective (optional)")
            intended_user = st.text_input("Intended End User (optional)")
            business_rules = st.text_area("Business Rules or Constraints (optional)", height=80)
            notes = st.text_area("Additional Notes (optional)", height=60)
            submitted = st.form_submit_button("🔍 Analyze Risks", use_container_width=True)

        if submitted:
            feature_input = {
                "feature_name": feature.get("name", ""),
                "feature_description": feature.get("description", ""),
                "business_objective": business_objective or "Not provided",
                "intended_user": intended_user or "Not provided",
                "business_rules": business_rules or "None provided",
                "notes": notes or "None provided",
            }
            with st.spinner("Analyzing risks and requirements..."):
                system_prompt, user_message = build_risk_expansion_prompt(feature_input)
                raw = call_risk_expansion(system_prompt, user_message)

            if raw is None:
                st.error("Analysis failed. Check your API key and network connection.")
            else:
                result = parse_risk_expansion_output(raw)
                if result is None:
                    st.error("Failed to parse the analysis. Try again.")
                else:
                    st.session_state[risk_key] = result.model_dump()
                    st.rerun()
    else:
        severity = analysis.get("severity_summary", "medium")
        color = SEVERITY_COLOR.get(severity, "orange")
        st.markdown(f"**Overall Risk:** :{color}[{severity.capitalize()}]")

        sections = [
            ("Edge Cases", "edge_cases"),
            ("Dependencies", "dependencies"),
            ("Ambiguities", "ambiguities"),
            ("Missing Requirements", "missing_requirements"),
        ]
        for heading, key in sections:
            items = analysis.get(key, [])
            if items:
                st.markdown(f"**{heading}**")
                for item in items:
                    st.markdown(f"- {item}")

        if st.button("Clear Analysis", key="btn_clear_risk"):
            st.session_state.pop(risk_key, None)
            st.rerun()


@st.dialog("Generate New User Story")
def _story_modal(feature: dict, feature_id: str, user_id: str):
    feature_name = feature.get("name", "")
    feature_title = st.text_input("Feature Title", value=feature_name)
    feature_description = st.text_area("Feature Description", height=100)
    business_objective = st.text_input("Business Objective")
    intended_user = st.text_input("Intended End User")
    business_rules = st.text_area("Business Rules or Constraints (optional)", height=80)
    notes = st.text_area("Additional Notes (optional)", height=60)

    col_generate, col_cancel = st.columns([2, 1])
    with col_generate:
        if st.button("Generate Story", use_container_width=True, type="primary", key="btn_modal_generate"):
            if not feature_description or not business_objective or not intended_user:
                st.error("Feature description, business objective, and intended user are required.")
            else:
                feature_input = {
                    "feature_name": feature_title,
                    "feature_description": feature_description,
                    "business_objective": business_objective,
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
                            st.success("Story saved.")
                            st.rerun()
                        else:
                            st.error("Story generated but could not be saved.")
    with col_cancel:
        if st.button("Cancel", use_container_width=True, key="btn_modal_cancel"):
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
        for key in [k for k in list(st.session_state.keys()) if k.startswith(("fanout_", "risk_"))]:
            st.session_state.pop(key)
        st.rerun()

    st.title(feature_name)
    st.caption(f"Project: {project_name}")
    st.subheader("User Stories")

    stories = list_stories(feature_id)

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

                if st.button("Delete Story", key=f"del_story_{story['id']}"):
                    delete_story(story["id"])
                    st.rerun()
    else:
        st.info("No stories yet. Generate one below.")

    _render_fanout_section(feature, feature_id, user_id)
    _render_risk_expansion_section(feature, feature_id)

    st.divider()
    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.markdown("#### Generate New User Story")
    with col_btn:
        if st.button("+ New Story", key="btn_open_story_modal", use_container_width=True, type="primary"):
            _story_modal(feature, feature_id, user_id)
