# TO-DO
# store as pdf the llm_repsonse
# add valid ID Form, (text to image moments na model)

#from utils.llm_utils import query_llm_from_data
from data.database import insert_borrower
from utils.llm_utils import detect_id_authenticity
import streamlit as st
import time

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
st.set_page_config(page_title="Borrower Hub", layout="wide")

st.title("Borrower Hub")
st.subheader("Get pre-assessed for a loan and receive a simple business plan. All in X minutes!")
st.html("<hr>")

# Initialize Session State
if "borrower_step" not in st.session_state:
    st.session_state.borrower_step = 1
if "borrower_data" not in st.session_state:
    st.session_state.borrower_data = {}

# Step 1: Profile Form
if st.session_state.borrower_step == 1:
    st.subheader("Tell us about yourself")

    with st.form("step1_form"):
        name = st.text_input("Enter Full Name")
        email = st.text_input("Enter Email (Optional)")
        location = st.text_input("Enter City")
        business_type = st.selectbox(
            "What type of business are you running or planning?",
            ["Sari-sari store", "Food cart", "Online selling", "Motorcycle transport", "Farming", "Other"]
        )
        business_stage = st.selectbox(
            "How long have you been running this business?",
            ["I haven't started yet", "Less than 1 year", "1–3 years", "More than 3 years"]
        )
        loan_goal = st.text_area("What do you need the loan for?", placeholder="e.g., Buy a second-hand refrigerator for my store")
        step1_submit = st.form_submit_button("Next")

        # Get and Store results
        if step1_submit:
            st.session_state.borrower_data.update({
                "name": name,
                "email": email,
                "location": location,
                "business_type": business_type,
                "business_stage": business_stage,
                "loan_goal": loan_goal
            })
            st.session_state.borrower_step = 2

# Step 2: Operations Form
elif st.session_state.borrower_step == 2:
    st.subheader("Tell us more about your business")

    with st.form("step2_form"):
        sales = st.number_input("What is your average monthly sales? (₱)", min_value=0, step=100)
        income_freq = st.selectbox(
            "How often do you receive income?",
            ["No income", "Daily", "Weekly", "Monthly"]
        )
        has_employees = st.radio("Do you have people helping you?", ["Yes", "No"])
        esg_essay = st.text_area("Describe how your business contributes to your local community and how it protects the environment.")
    
        col1, col2 = st.columns(2)
        step2_submit = col1.form_submit_button("Next")
        restart = col2.form_submit_button("🔁 Start Over")

        # Get and Store results
        if step2_submit:
            st.session_state.borrower_data.update({
                "monthly_sales": sales,
                "income_frequency": income_freq,
                "has_employees": has_employees,
                "esg_essay":esg_essay
            })
            st.session_state.borrower_step = 3
        
        if restart:
            st.session_state.borrower_step = 1
            st.session_state.borrower_data = {}

# AI Section + Step 3
elif st.session_state.borrower_step == 3:
    data = st.session_state.borrower_data
    st.subheader("Your Microloan Preview")
    st.html("<hr>")

    st.markdown(f"""
    **Hello {data['name']} from {data['location']}!**

    Thanks for telling us about your *{data['business_type']}* business. 
    Based on your monthly sales of **₱{data['monthly_sales']:,.0f}**, and your loan goal:

    > *{data['loan_goal']}*

    Here's what our AI recommends:
    """)

    # CHECK SKILLS WORD DOCUMENT FOR CODE

    st.html("<br>")
    st.button("Download as Business Plan")

    # Step 3
    st.html("<hr>")
    st.subheader("Final Step: Document Upload")

    with st.form("step3_submit"):
        valid_id = st.file_uploader(type=["JPG", "PNG"], accept_multiple_files=False, 
                                    label="Please upload a Valid government ID here")

        # Validate the uploaded ID via AI (just to determine if image is deepfake / AI-Generated)
        if valid_id is not None:
            ai_result = detect_id_authenticity(valid_id)

            if "real" in ai_result:
                real_conf = ai_result["real"]
                fake_conf = ai_result["fake"]

                # Initial label based on which confidence is higher
                label = "Real" if real_conf >= fake_conf else "Fake"
                confidence = real_conf if label == "Real" else fake_conf

                # Apply minimum confidence threshold (70%)
                if confidence < 0.70:
                    label = "Fake"  
                    confidence = max(real_conf, fake_conf)

                st.info(f"AI Prediction: **{label}** ({confidence:.2%} confidence)")

                # Warn if fairly confident fake
                if label == "Fake" and fake_conf > 0.80:
                    st.warning("The uploaded ID may be altered or AI-generated. Please try another image.")
                elif label == "Fake":
                    st.warning("The AI model suspects this may be fake — consider uploading a clearer ID photo.")
            else:
                st.error("Unexpected AI response.")

        business_plan = st.file_uploader(type="PDF", accept_multiple_files=False, 
                                        label="Upload Business Plan PDF here. You may use the AI-generated business plan if you don't have one")
        
        esg_file = st.file_uploader(type="CSV", accept_multiple_files=False,
                                    label="Upload ESG data here (Optional but highly encouraged)")

        col1, col2 = st.columns(2)
        step3_submit = col1.form_submit_button("Submit")
        restart = col2.form_submit_button("🔁 Start Over")

        # Submit handling (only proceed if label is real)
        
        if step3_submit:
            if valid_id is None:
                st.warning("Please upload both a valid government ID and a business plan PDF before submitting.")
            elif label.lower() != "real":
                st.error("Cannot proceed — ID did not pass authenticity check.")
            else:
                # Insert into Database
                insert_borrower(
                    name=data["name"],
                    email=data.get("email", ""),
                    location=data["location"],
                    business_type=data["business_type"],
                    business_stage=data["business_stage"],
                    loan_goal=data["loan_goal"],
                    sales=data["monthly_sales"],
                    income_freqruency=data["income_frequency"],
                    has_employees=data["has_employees"].lower(),
                    essay=data.get("esg_essay", "")
                )

                st.success("All documents are in order. Saving your data...")
                time.sleep(2)
                st.switch_page("pages/3_Thank_you.py")

        if restart:
            st.session_state.borrower_step = 1
            st.session_state.borrower_data = {}