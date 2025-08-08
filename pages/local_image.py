import streamlit as st
import easyocr
from PIL import Image
import numpy as np

# Page setup
st.set_page_config(page_title="🧠 OCR - Image to Text", layout="centered")
st.title("🧠 OCR - Image to Text")

# Upload
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    with st.spinner("🔍 Running OCR..."):
        reader = easyocr.Reader(['en'], gpu=False)
        result = reader.readtext(np.array(image), detail=0)
        extracted_text = "\n".join(result)

    if extracted_text.strip():
        st.success("✅ Extracted Text:")
        st.text_area("Text Output", extracted_text, height=300)
    else:
        st.warning("⚠️ No text detected.")
