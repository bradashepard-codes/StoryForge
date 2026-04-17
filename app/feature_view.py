import streamlit as st
from app.db import list_stories, save_story, delete_story, get_feature
from app.prompts import build_improved_prompt, build_fanout_prompt
from app.llm_client import call_improved, call_fanout, suggest_fanout_context
from app.parser import parse_output, parse_fanout_output


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

        with st.form("fanout_context_form"):
            business_objective = st.text_input("Business Objective *", key="fanout_biz_obj")
            intended_user = st.text_input("Intended End User *", key="fanout_intended_user")
            business_rules = st.text_area("Business Rules or Constraints (optional)", height=70, key="fanout_biz_rules")
            notes = st.text_area("Additional Notes (optional)", height=50, key="fanout_notes")
            generate = st.form_submit_button("🚀 Generate All Stories", use_container_width=True, type="primary")

        if generate:
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
            label = story.get("title") or f"Story {i + 1}"
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
                        result = save_story(feature_id, story, user_id)
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


def render_feature():
    user = st.session_state["user"]
    user_id = user.id
    feature_id = st.session_state["feature_id"]
    project_name = st.session_state.get("project_name", "Project")

    feature = get_feature(feature_id)
    feature_name = feature.get("name") or st.session_state.get("feature_name", "Feature")

    if st.button("← Back", key="back_to_project"):
        st.session_state["view"] = "project"
        for key in [k for k in list(st.session_state.keys()) if k.startswith("fanout_")]:
            st.session_state.pop(key)
        st.rerun()

    st.title(feature_name)
    st.caption(f"Project: {project_name}")
    st.subheader("User Stories")

    stories = list_stories(feature_id)

    if stories:
        for story in stories:
            label = story.get("title") or story.get("user_story", "")[:80] or f"Story — {story['created_at'][:10]}"
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

    st.divider()
    st.markdown("#### Generate New User Story")

    with st.form("generate_story_form", clear_on_submit=True):
        feature_title = st.text_input("Feature Title", value=feature_name)
        feature_description = st.text_area("Feature Description", height=100)
        business_objective = st.text_input("Business Objective")
        intended_user = st.text_input("Intended End User")
        business_rules = st.text_area("Business Rules or Constraints (optional)", height=80)
        notes = st.text_area("Additional Notes (optional)", height=60)
        submitted = st.form_submit_button("Generate Story", use_container_width=True)

    if submitted:
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
                    saved = save_story(feature_id, parsed.model_dump(), user_id)
                    if saved:
                        st.success("Story saved.")
                        st.rerun()
                    else:
                        st.error("Story generated but could not be saved.")
