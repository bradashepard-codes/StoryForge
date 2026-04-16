from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from app.login_view import render_login
from app.dashboard_view import render_dashboard
from app.project_view import render_project
from app.feature_view import render_feature


def main():
    st.set_page_config(page_title="StoryForge", layout="wide")

    if "view" not in st.session_state:
        st.session_state["view"] = "login"

    view = st.session_state["view"]

    if view == "login":
        render_login()
    elif view == "dashboard":
        render_dashboard()
    elif view == "project":
        render_project()
    elif view == "feature":
        render_feature()
    else:
        st.session_state["view"] = "login"
        st.rerun()


main()
