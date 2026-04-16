import streamlit as st


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
        else:
            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Baseline Output")
                st.info("Baseline generation coming soon.")

            with col2:
                st.markdown("### Improved Output")
                st.info("Improved generation coming soon.")

            st.markdown("---")
            st.markdown("### Definition of Ready Assessment")
            st.info("DoR assessment coming soon.")

            st.markdown("---")
            st.markdown("### Missing Information / Escalation")
            st.info("Missing information and escalation flags coming soon.")
