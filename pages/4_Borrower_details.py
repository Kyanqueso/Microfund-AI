import streamlit as st
import pandas as pd
import time
from data.database import get_id, delete_user
from utils.scoring_utils import train_model, predict_esg_label, get_top_shap_keywords
from utils.llm_utils import generate_summary
from dotenv import load_dotenv

load_dotenv()

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
st.set_page_config(page_title="Borrower Details", layout="wide")

# Check if ID was passed via session_state
if 'selected_borrower_id' not in st.session_state:
    st.error("No borrower selected.")
    st.stop()

borrower_id = st.session_state.selected_borrower_id
borrower = get_id(borrower_id)

# Unpacking the borrower tuple 
id, name, email, location, business_type, business_stage, loan_goal, sales, income_freqruency, has_employees, essay, timestamp = borrower

with st.spinner("Analyzing borrower profile..."):
    model_pipeline, accuracy = train_model()
    top_keywords = get_top_shap_keywords(model_pipeline)

    combined_essay = f"{essay}"
    esg_score = predict_esg_label(model_pipeline, combined_essay)

st.header(f"Details of {name}")
st.html("<hr>")
st.subheader("Information and Business Plan")

features = [
    "ID", "Name", "Email", "Location", "Business Type",
    "Business Stage", "Loan Goal", "Sales", "Income Frequency",
    "Has Employees", "Essay", "Timestamp"
]

# Display in table
df = pd.DataFrame({
    "Feature": features,
    "Value": borrower
})
st.dataframe(df)

# Display PDF file (optional)

# Summary of User + ESG Score
st.html("<hr>")
st.subheader("Summary")
summary_prompt = f"""
    You are a loan analyst in a bank in the Philippines (BPI). You've studied 1000 SME applications.
    From analysis, ESG-aligned businesses often mention: {top_keywords}.

    This borrower has submitted the following:
    Business Type: {business_type}
    Location: {location}
    Loan Goal: {loan_goal}
    Sales: {sales}
    Has Employees: {has_employees}
    Essay: {essay}

    Your machine learning model predicts: **{esg_score}**

    Based on this, do you agree this borrower is ESG-aligned and fundable?
    Explain in plain language. Limit to 2 paragraphs.
    """

with st.spinner("Generating ESG analysis..."):
    summary_output = generate_summary(summary_prompt)

st.markdown(summary_output)
# Machine learning montage mometns here + SHAP to rate ESG Score

st.html("<hr>")
st.subheader("Ask AI")
user_prompt = st.text_area("Ask AI regarding this lender")
st.button("Prompt")

# AI Prompt (GPT 4.1) here

st.html("<hr>")

col1, col2, col3= st.columns(3)
accept = col1.button("Accept")
flagged = col2.button("Flag for More Checking")
reject = col3.button("Reject")

# if accept will show message and for others as well
if accept:
    st.success("Loan Approved!")
    time.sleep(3)
    st.switch_page("pages/1_ESG_Manager_Hub.py")

elif flagged:
    st.warning("Loan placed into more reviewing")
    time.sleep(3)
    st.switch_page("pages/1_ESG_Manager_Hub.py")

elif reject:
    st.error("Loan Rejected, Removed from system")
    time.sleep(3)
    delete_user(id)
    st.switch_page("pages/1_ESG_Manager_Hub.py")