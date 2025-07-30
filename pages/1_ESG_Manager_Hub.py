# TO DO
# Replace col 2 with esg chart
# Wait for cards html/css/bootstrap

import streamlit as st
from data.database import get_all_submissions, search_name

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
st.set_page_config(page_title="ESG Hub", layout="wide")

st.title("ESG Manager Hub")
st.subheader("Analyze SME ESG lenders, evaluate risk, and generate instant auditable reports.")
st.html("<hr>")

search_field = st.text_input("Search Customer", placeholder="Enter Customer Name here")
search_btn = st.button("Search")
st.html("<hr>")

if search_btn and search_field.strip():
    name_of_the_user = search_field.strip()
    search_results = search_name(name_of_the_user)

    if search_results:
        for i, (id, name, email, location, business_type, business_stage, loan_goal, sales, income_freqruency, has_employees, essay, timestamp) in enumerate(search_results, start=1):
            col1, col2 = st.columns(2)
            col1.markdown(f"""
            Loan Application ID: {id}\n
            *{name}*  
            🏢 *{business_type}* from 📍*{location}*  
            🕒 Submitted: `{timestamp}`
            """)
            if col2.button("View Details", key=f"view_{id}"):
                st.session_state.selected_borrower_id = id
                st.switch_page("pages/4_Borrower_details.py")
            st.html("<hr>")
    else:
        st.info("Name searched does not exists.")

else :
    submissions = get_all_submissions()
    if submissions:
        for i, (id, name, email, location, business_type, business_stage, loan_goal, sales, income_freqruency, has_employees, essay, timestamp) in enumerate(submissions, start=1):
            col1, col2 = st.columns(2)
            col1.markdown(f"""
            Loan Application ID: {id}\n
            *{name}*  
            🏢 *{business_type}* from 📍*{location}*  
            🕒 Submitted: `{timestamp}`
            """)
            if col2.button("View Details", key=f"view_{id}"):
                st.session_state.selected_borrower_id = id
                st.switch_page("pages/4_Borrower_details.py")
            st.html("<hr>")
    else:
        st.info("No borrower submissions yet.")