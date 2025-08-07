# Home Page
import streamlit as st
from PIL import Image
import time
from data.database import init_db

# Initialize the database
init_db()

# Hide Sidebar
hide_sidebar_style = """
    <style>
        /* Hide sidebar completely */
        [data-testid="stSidebar"] {
            display: none;
        }

        /* Hide the top-right hamburger and fullscreen buttons */
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)
st.set_page_config(page_title="Microfund AI", layout="centered")

st.title("Welcome to Microfund AI")
st.subheader("Making lending easy for everyone")
st.html("<hr>")

st.markdown("### Who are you?")
role = st.radio(
    "Select your Role:",
    ["ESG Manager / Evaluator", "Entrepreneur / Borrower"],
    index=None,
    key="user_role"
)

# Each user redirect after select role
if role:
    st.success(f"Redirecting you to the {role.split (' / ')[1]} interface...")

    with st.spinner("Loading Interface..."):
        time.sleep(5)

        if "ESG Manager" in role:
            st.switch_page("pages/1_ESG_Manager_Hub.py")
        elif "Entrepreneur" in role:
            st.switch_page("pages/2_Borrower_Hub.py")