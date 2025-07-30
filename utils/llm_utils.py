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

def generate_summary(prompt):
    client = openai.OpenAI()  # New client object

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