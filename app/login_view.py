import streamlit as st
from app.db import sign_in, sign_up


def render_login():
    st.title("StoryForge")
    st.subheader("Sign in to continue")

    tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Email and password are required.")
            else:
                try:
                    result = sign_in(email, password)
                    if result.session:
                        st.session_state["session"] = result.session
                        st.session_state["user"] = result.user
                        st.session_state["view"] = "dashboard"
                        st.rerun()
                    else:
                        st.error("Sign in failed. Check your credentials.")
                except Exception as e:
                    st.error(f"Sign in failed: {e}")

    with tab_signup:
        with st.form("signup_form"):
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
            submitted_signup = st.form_submit_button("Create Account", use_container_width=True)

        if submitted_signup:
            if not new_email or not new_password:
                st.error("Email and password are required.")
            elif new_password != confirm:
                st.error("Passwords do not match.")
            else:
                try:
                    result = sign_up(new_email, new_password)
                    if result.user:
                        st.success("Account created! Check your email to confirm, then sign in.")
                    else:
                        st.error("Sign up failed. Try again.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")
