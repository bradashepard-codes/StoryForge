import streamlit as st
from app.prompts import build_baseline_prompt, build_improved_prompt
from app.llm_client import call_baseline, call_improved
from app.parser import parse_output, parse_baseline_output


def render_ui():
    st.set_page_config(page_title="StoryForge", layout="wide")

    st.title("StoryForge")
    st.subheader("Definition-of-Ready User Story Generator")
    st.markdown("---")

    # --- Input Form ---
    with st.form("feature_input_form"):
        st.markdown("### Feature Input")

        feature_name = st.text_input(
            "Feature Name *",
            placeholder="e.g. Broker Policy Change Submission"
        )

        feature_description = st.text_area(
            "Feature Description *",
            placeholder="Describe the feature in as much detail as you have.",
            height=120
        )

        business_objective = st.text_area(
            "Business Objective *",
            placeholder="What business problem does this feature solve?",
            height=80
        )

        intended_user = st.text_input(
            "Intended End User *",
            placeholder="e.g. Broker, Underwriter, Claims Adjuster"
        )

        business_rules = st.text_area(
            "Business Rules or Constraints",
            placeholder="Any known rules, constraints, or dependencies (optional).",
            height=80
        )

        assumptions = st.text_area(
            "Notes or Assumptions",
            placeholder="Any assumptions or additional context (optional).",
            height=80
        )

        submitted = st.form_submit_button("Generate", use_container_width=True)

    # --- Output Sections ---
    if submitted:
        required_fields = [feature_name, feature_description, business_objective, intended_user]
        if not all(required_fields):
            st.error("Please complete all required fields marked with *")
            return

        feature_input = {
            "feature_name": feature_name,
            "feature_description": feature_description,
            "business_objective": business_objective,
            "intended_user": intended_user,
            "business_rules": business_rules,
            "assumptions": assumptions
        }

        st.markdown("---")

        with st.spinner("Generating story package..."):
            baseline_raw = call_baseline(build_baseline_prompt(feature_input))
            system_prompt, user_message = build_improved_prompt(feature_input)
            improved_raw = call_improved(system_prompt, user_message)

        baseline_text = parse_baseline_output(baseline_raw)
        improved = parse_output(improved_raw)

        # --- Baseline vs Improved ---
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Baseline Output")
            st.text_area("", value=baseline_text, height=300, disabled=True, label_visibility="collapsed")

        with col2:
            st.markdown("### Improved Output")
            if improved:
                st.markdown("**User Story**")
                st.info(improved.user_story)
                st.markdown("**Acceptance Criteria**")
                for criterion in improved.acceptance_criteria:
                    st.markdown(f"- {criterion}")
            else:
                st.warning("Could not parse structured output. Raw response:")
                st.text_area("", value=improved_raw, height=300, disabled=True, label_visibility="collapsed")

        # --- DoR Assessment ---
        st.markdown("---")
        st.markdown("### Definition of Ready Assessment")

        if improved:
            dor = improved.definition_of_ready
            status = "Ready" if dor.is_ready else "Not Ready"
            color = "green" if dor.is_ready else "red"
            st.markdown(f"**Status:** :{color}[{status}]")

            col3, col4 = st.columns(2)
            with col3:
                st.markdown("**Criteria Met**")
                for c in dor.criteria_met:
                    st.markdown(f"- {c}")
            with col4:
                st.markdown("**Criteria Missing**")
                if dor.criteria_missing:
                    for c in dor.criteria_missing:
                        st.markdown(f"- {c}")
                else:
                    st.markdown("_None_")
        else:
            st.info("DoR assessment unavailable — structured output could not be parsed.")

        # --- Missing Information / Escalation ---
        st.markdown("---")
        st.markdown("### Missing Information / Escalation")

        if improved:
            col5, col6 = st.columns(2)
            with col5:
                st.markdown(f"**Confidence:** {improved.confidence.capitalize()}")
                if improved.escalation_flag:
                    st.error("Escalation Required — this feature is not ready for sprint entry.")
                else:
                    st.success("No escalation required.")

                st.markdown("**Missing Information**")
                if improved.missing_information:
                    for item in improved.missing_information:
                        st.markdown(f"- {item}")
                else:
                    st.markdown("_None identified._")

            with col6:
                st.markdown("**Assumptions Made**")
                if improved.assumptions:
                    for item in improved.assumptions:
                        st.markdown(f"- {item}")
                else:
                    st.markdown("_None._")
        else:
            st.info("Escalation data unavailable — structured output could not be parsed.")
