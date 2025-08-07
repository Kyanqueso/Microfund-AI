import io
import torch
import streamlit as st
from transformers import SiglipForImageClassification, AutoImageProcessor
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# No files prompt
def generate_summary(prompt):
    client = openai.OpenAI() 

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a helpful loan analyst AI assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=500
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