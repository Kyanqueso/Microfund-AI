from data.database import insert_borrower, save_file_to_data, update_borrower_files
from utils.llm_utils import detect_id_authenticity, generate_summary
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
st.subheader("Get pre-assessed for a loan. All in less than a minute!")
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
            if not all([name, location, business_type, business_stage, loan_goal]):
                st.warning("Please fill all non-optional fields")
            else:
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

    # Initialize variables
    label = None 
    confidence = 0.0
    
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

    prompt = f"""
        Role: You are a Loan Manager from BPI (Bank of the Philippine Islands). You are expected to be professional, 
        data-driven, and firm in assessing loan applications, but also compassionate and understanding toward 
        Filipino borrowers.

        Moreover, the following are the responses of a potential loan applicant:

        Name: {data['name']}
        Email: {data['email']}
        Location: {data['location']},
        Business type: {data['business_type']},
        Business stage: {data['business_stage']},
        Loan goal: {data["loan_goal"]}
        Monthly sales: ₱{data['monthly_sales']:,.0f},
        Income frequency: {data["income_frequency"]},
        Has employees: {data["has_employees"]}

        Task:
        Based on the information provided, conduct a preliminary assessment of the applicant’s potential loan eligibility. 
        Consider financial capacity, business maturity, and loan goal. 
        
        Then:
        - Provide a short but realistic pre-assessment of their loan eligibility.
        - Indicate a probability rating (in percentage) of approval based on typical BPI lending criteria.
        - Keep your tone firm but supportive—show you are open to helping them qualify if not immediately eligible.

        Structure your response like this as well:
        1. Concise Preliminary Assessment
        2. Probability
        3. Conclusion
    """
    
    with st.spinner("AI is assessing your answers..."):
        ai_summary = generate_summary(prompt)
        st.markdown(ai_summary)

    st.html("<br>")

    # Step 3
    st.html("<hr>")
    st.subheader("Final Step: Document Upload")

    with st.form("step3_submit"):
        bank_num = st.text_input("Enter BPI bank account number here")
        
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

        business_permit = st.file_uploader(type="PDF", accept_multiple_files=False, 
                                        label="Upload Business Permit here")
        
        bank_statement = st.file_uploader(type="PDF", accept_multiple_files=False,
                                    label="Upload the last 3 months of bank statements here (must be 1 PDF file only)")

        income_tax_file = st.file_uploader(type="PDF", accept_multiple_files=False,
                                           label="Upload most recent income tax return")
        
        collateral = st.text_area("Enter the details of collateral here, can be real property or the equipment to be financed (OPTIONAL)")

        col1, col2, col3= st.columns(3)
        step3_submit = col1.form_submit_button("Submit")
        restart = col3.form_submit_button("🔁 Start Over")

        # Submit handling (only proceed if label is real)
        
        if step3_submit:
            if not all([bank_num, valid_id, business_permit, bank_statement, income_tax_file]):
                st.warning("Please upload all required documents before submitting")
            elif label is None:
                st.error("ID authenticity has not been verified yet.")
            elif label.lower() != "real":
                st.error("Cannot proceed — ID did not pass authenticity check.")
            else:
                st.session_state.borrower_data.update({
                    "bank_num": bank_num,
                    "valid_id": valid_id,
                    "business_permit": business_permit,
                    "bank_statement": bank_statement,
                    "income_tax_file": income_tax_file,
                    "collateral": collateral
                })
                # Insert into Database
                borrower_id = insert_borrower(
                    name=data["name"],
                    email=data.get("email", ""),
                    location=data["location"],
                    business_type=data["business_type"],
                    business_stage=data["business_stage"],
                    loan_goal=data["loan_goal"],
                    sales=data["monthly_sales"],
                    income_freqruency=data["income_frequency"],
                    has_employees=data["has_employees"].lower(),
                    essay=data.get("esg_essay", ""),
                    bank_num = data["bank_num"],
                    collateral=data.get("collateral", "")
                )

                # Save uploaded files to /data folder (might change to just a new folder talaga)
                valid_id_path = save_file_to_data(valid_id, borrower_id)
                business_permit_path = save_file_to_data(business_permit, borrower_id)
                bank_statement_path = save_file_to_data(bank_statement, borrower_id)
                income_tax_file_path = save_file_to_data(income_tax_file, borrower_id)

                update_borrower_files(
                    borrower_id, valid_id_path, business_permit_path, 
                    bank_statement_path, income_tax_file_path
                )

                st.success("All documents are in order. Saving your data...")
                time.sleep(2)
                st.switch_page("pages/3_Thank_you.py")

        if restart:
            st.session_state.borrower_step = 1
            st.session_state.borrower_data = {}