import io
import torch
import openai
import os
import base64
import streamlit as st
from io import BytesIO
from transformers import SiglipForImageClassification, AutoImageProcessor
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# No files prompt (and also just general use as well)
def generate_summary(prompt):
    client = openai.OpenAI() 

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a helpful loan analyst AI assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=1024
    )
    return response.choices[0].message.content

# With uploaded files prompt
def generate_summary2(prompt, valid_id_desc, business_permit_path, bank_statement_path, income_tax_file_path):
    client2 = openai.OpenAI()

    combined_prompt = ()
    response2 = client2.chat.completions.create(
        model="gpt-4.1",
        messages = [
            {"role":"system", "content": "You are a helpful loan analyst AI assistant."},
            {"role":"user", "content": combined_prompt}
        ],
        temperature=0.7, # Since must be more rational
        max_tokens = 500
    )

# ========================================
# Detect if Image is Fake AI Model Section

MODEL_ID2 = "prithivMLmods/deepfake-detector-model-v1"
image_model = SiglipForImageClassification.from_pretrained(MODEL_ID2)
processor = AutoImageProcessor.from_pretrained(MODEL_ID2)

id2label = {"0": "fake", "1": "real"}

def detect_id_authenticity(uploaded_file):
    image = Image.open(io.BytesIO(uploaded_file.read())).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = image_model(**inputs)
        logits = outputs.logits.squeeze()
        probs = torch.softmax(logits, dim=0).tolist()

    return {id2label[str(i)]: probs[i] for i in range(len(probs))}

# ========================================
# Image to Text (for Valid ID)

def classify_img(image_path):
    client = openai.OpenAI() 
    try:
        classify_prompt = """
        Task: Determine whether the provided image is likely a valid government-issued identification 
        document (e.g., passport, driver’s license, national ID card) with greater than 95% confidence.

        Instructions:

        - Do not read, extract, or transcribe any text from the image.
        - Do not attempt OCR or store personal information.
        - Focus only on visual and structural cues common to ID documents, such as:
        - Portrait photo placement and framing
        - Presence of security holograms, seals, watermarks, microprint patterns
        - Typical layout of data fields (name, DOB, signature area — without reading them)
        - Barcodes, MRZ (machine-readable zone), or chip contact pads
        - Standard background designs used in official IDs

        Classify the image into one of:

        Likely Valid ID (≥95% confidence)

        Possibly an ID but <95% confidence

        Not an ID

        Finally, provide a brief explanation of your classification based purely on non-PII visual features.
        """

        buffered = io.BytesIO()
        image_path.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()

        img_64 = base64.b64encode(img_bytes).decode("utf-8")
        img_url = f"data:image/jpg;base64,{img_64}"
        
        response3 = client.chat.completions.create(
            model ="gpt-4o",
            messages=[
                {"role": "user",
                 "content": [
                    {"type": "text", "text": classify_prompt},
                    {"type": "image_url", "image_url": {"url": img_url}}
                    ]
                }
            ],
            temperature = 0,
            max_tokens = 1024
        )
        return response3.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error: {type(e).__name__} - {str(e)}"
        #return "Something went wrong :("