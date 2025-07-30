import streamlit as st

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
st.set_page_config(page_title="Thank you for applying!",layout="centered")

st.success("Your application for a loan is successful!")
st.html("<hr>")
st.markdown("Maraming salamat po! We will be sending the next steps in your email. If you don't have an email, no worries — We will also send it via text or letter.. Tuloy lang po, kaya natin ’to!")
st.markdown("Contact Details: xxx-xxxx")
st.html("<br>")

# Can add images for BPI advertisements i guess para may laman nmn to (placeholder lng muna)

back_to_home = st.button("Back to Home")
if back_to_home:
    st.switch_page("Home.py")