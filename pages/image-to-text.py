import streamlit as st
import base64
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path


# --- Configuration ---
# Explicit absolute path
env_path = Path("C:/Users/admin/Desktop/VS CODE PROJECTS/Microfund-AI/.env")
load_dotenv(dotenv_path=env_path)

# Option 2: Load from current directory (simpler)
load_dotenv()  # Looks for .env in current directory

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Please check:")
    st.error("1. You have a .env file in your project root")
    st.error("2. It contains: OPENAI_API_KEY=your_key_here")
    st.error(f"Current working directory: {os.getcwd()}")
    st.stop()

client = OpenAI(api_key=api_key)

# --- Streamlit App ---
st.set_page_config(page_title="OCR with OpenAI", layout="centered")
st.title("🧠 OCR with OpenAI GPT-4o")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

def encode_image(image_file):
    image_file.seek(0)  # Rewind the file
    return base64.b64encode(image_file.read()).decode("utf-8")

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Extracting text..."):
        try:
            base64_img = encode_image(uploaded_file)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all visible text from the image with exact formatting, including numbers, tables, special characters, "
                            "and structured data such as ESG metrics, financial figures, business KPIs, charts, and labels; if graphs or dashboards are present, interpret "
                            "and summarize key business insights, ESG indicators, and financial or operational risks for audit and reporting; if no text exists, describe "
                            "the layout, document type, visual elements, and any business context or branding relevant to SME ESG lender analysis and automated due diligence."},
                            {"type": "image_url", "image_url": {"url": f"data:image/{uploaded_file.type.split('/')[-1]};base64,{base64_img}"}}
                        ]
                    }
                ],
                temperature=0,
                max_tokens=1024,
            )

            result = response.choices[0].message.content
            st.success("✅ Text extracted successfully!")
            st.text_area("Extracted Text", result, height=300)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.error("Please try again or check your API key quota")