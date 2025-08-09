import streamlit as st
import pandas as pd
import time
from data.database import get_id, delete_user
from utils.scoring_utils import train_model, predict_esg_label, get_top_shap_keywords
from utils.llm_utils import generate_summary, classify_img
from dotenv import load_dotenv
from PIL import Image

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
id, name, email, location, business_type, business_stage, loan_goal, sales, income_freqruency, has_employees, essay, timestamp, bank_num, valid_id, business_permit, bank_statement, income_tax_file, collateral = borrower

with st.spinner("Analyzing borrower profile..."):
    model_pipeline, accuracy = train_model()
    top_keywords = get_top_shap_keywords(model_pipeline)

    combined_essay = f"{essay}"
    esg_score = predict_esg_label(model_pipeline, combined_essay)

st.header(f"Details of {name}")
st.html("<hr>")
st.subheader("Table of Information")

features = [
    "ID", "Name", "Email", "Location", "Business Type",
    "Business Stage", "Loan Goal", "Sales", "Income Frequency",
    "Has Employees", "Essay", "Timestamp","Bank Account Number", "Valid ID", 
    "Business Permit", "Bank Statements", "Income Tax Files", "Collateral Description"
]

# Display in table
df = pd.DataFrame({
    "Feature": features,
    "Value": borrower
})
st.dataframe(df)
st.markdown("For uploaded files check ID of user and data folder")

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
    Collateral : {collateral}

    Your machine learning model predicts: **{esg_score}**

    Based on this, do you agree this borrower is ESG-aligned and fundable?
    Explain in plain language for the bank manager to understand quickly. 
    Limit to 2 paragraphs.
    """

image_obj = Image.open(valid_id) # Open id image for processing
valid_id_summary = classify_img(image_obj)
summary_prompt2 = f"""
    Also here are the results of the uploaded valid ID: {str(valid_id_summary)}
    If none, it either means the photo is unrelated or the user did not upload.
    Finally, do not offer assistance, just purely state the results of the uploaded
    valid ID in a maximum of 3 sentences.
    """

st.subheader(f"Machine Learning model prediction: {esg_score}")

with st.spinner("Generating ESG analysis..."):
    summary_output = generate_summary(summary_prompt)
    summary_output2 = generate_summary(summary_prompt2)

st.markdown(summary_output)

st.html("<hr>")
st.subheader("Valid ID Scan Result:")
st.markdown(summary_output2)

# Prompt Section
st.html("<hr>")
st.subheader("Ask AI")
user_prompt = st.text_area("Ask AI regarding this lender")
prompt_btn = st.button("Prompt")

if prompt_btn:
    with st.spinner("AI is generating an appropriate answer..."):
        # Chain prompt moments sheeeesh
        ai_ans = generate_summary(summary_prompt + summary_output + user_prompt + 
                "Moreover, if user_prompt is empty, inform user that it is empty and prompt user again for input.")
        st.html("<hr>")
        st.subheader("Answer of AI:")
        st.markdown(ai_ans)


st.html("<hr>")

col1, col2, col3= st.columns(3)
accept = col1.button("Accept")
flagged = col2.button("Flag for More Checking")
reject = col3.button("Reject")

# if accept will show message and for others as well
if accept:
    st.success("Loan Approved!")
    time.sleep(3)
    download_report = st.button("Download as report (PDF)")
    # Let GPT make the report moments

elif flagged:
    st.warning("Loan placed into more reviewing")
    time.sleep(3)
    st.switch_page("pages/1_ESG_Manager_Hub.py")

elif reject:
    st.error("Loan Rejected, Removed from system")
    time.sleep(3)
    delete_user(id)
    st.switch_page("pages/1_ESG_Manager_Hub.py")