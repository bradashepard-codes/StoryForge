import streamlit as st
from app.db import list_stories, save_story, delete_story
from app.prompts import build_improved_prompt
from app.llm_client import call_improved
from app.parser import parse_output


def render_feature():
    user = st.session_state["user"]
    user_id = user.id
    feature_id = st.session_state["feature_id"]
    feature_name = st.session_state.get("feature_name", "Feature")
    project_name = st.session_state.get("project_name", "Project")

    col_back, col_title = st.columns([1, 8])
    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state["view"] = "project"
            st.rerun()
    with col_title:
        st.title(feature_name)
        st.caption(f"Project: {project_name}")
        st.subheader("User Stories")

    stories = list_stories(feature_id)

    if stories:
        for story in stories:
            with st.expander(f"Story — {story['created_at'][:10]}", expanded=False):
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

    st.divider()
    st.markdown("#### Generate New User Story")

    with st.form("generate_story_form"):
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
                "feature_title": feature_title,
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
