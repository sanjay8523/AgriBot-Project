# pages/2_Disease_Detector.py
import streamlit as st
import numpy as np
import tensorflow as tf
from PIL import Image
import requests
from dotenv import load_dotenv
import os
from groq import Groq
import io

# --- Import shared functions ---
from utils import apply_custom_css, t, language_toggle, get_kannada_audio_bytes
from project_bot import render_project_bot # (NEW) Import floating bot

# --- Apply CSS and Language Toggle ---
apply_custom_css()
with st.sidebar:
    language_toggle()

# Get current language
lang = st.session_state.lang

# ----------------- Load .env -----------------
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ----------------- Initialize Groq Client -----------------
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ----------------- Load Model -----------------
@st.cache_resource
def load_model():
    model_path = "FinalTest_inceptionv3.h5" 
    if not os.path.exists(model_path):
        st.error(f"Model file not found at {model_path}. Please place it in the root directory.")
        return None
    custom_objects = {"mse": tf.keras.losses.MeanSquaredError()}
    return tf.keras.models.load_model(model_path, custom_objects=custom_objects)

model = load_model()

# ----------------- Labels -----------------
class_labels = {0: "Brown Spot", 1: "Healthy Plant", 2: "Leaf Blast", 3: "Sheath Blight"}

# ----------------- Weather API -----------------
@st.cache_data(ttl=300)
def get_weather(city="Bangalore"):
    if not OPENWEATHER_API_KEY: return None
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10); data = response.json()
        if data.get("cod") == 200:
            temp = round(data["main"]["temp"]); icon = data["weather"][0]["icon"]
            desc = data["weather"][0]["description"].title(); icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
            return temp, icon_url, desc
    except: pass
    return None

# ----------------- LLM Treatment (GROQ) -----------------
def get_treatment_from_llm(disease: str, lang: str):
    if not client: return t("LLM not available.", lang), None
    prompt = f"4 short, practical cure & prevention steps for paddy {disease}. Bullets only."
    if lang == "Kannada": prompt += " Answer in Kannada. Use • for bullets."
    try:
        chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.3, max_tokens=250)
        response = chat.choices[0].message.content.strip()
        lines = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith(('•', '-', '*')):
                line = line.lstrip('•-* ').strip()
                if line: lines.append(f"• {line}")
        clean_text = "<br>".join(lines[:4])
        audio_text = " ".join([l.replace('•', '').strip() for l in lines[:4]])
        return clean_text, audio_text
    except Exception as e: return t(f"Error: {e}", lang), None

# ----------------- Image Preprocessing & Prediction -----------------
def preprocess_image(img):
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_image(model, img):
    try:
        img_array = preprocess_image(img)
        predictions = model.predict(img_array)
        
        class_probs = predictions[0]
        severity_output = predictions[1]
        
        disease_idx = np.argmax(class_probs)
        disease = class_labels.get(disease_idx, "Unknown")
        scale = float(severity_output[0][0])
        
        if disease == "Healthy Plant":
            scale = 0.0
            
        return disease, round(scale, 2)
        
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return "Unknown", 0.0

# ----------------- Weather -----------------
weather = get_weather("Bangalore")
if weather:
    temp, icon_url, desc = weather; _, col_w = st.columns([1, 6])
    with col_w:
        c1, c2 = st.columns([2, 1])
        with c1: st.markdown(f"**{temp}°C**<br><small>{t(desc, lang)}</small>", unsafe_allow_html=True)
        with c2: st.image(icon_url, width=50)

# ----------------- Main UI -----------------
st.markdown(f"<h1 style='text-align:center;'>{t('AgroScan - Paddy Disease Detector', lang)}</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(t("Upload Paddy Leaf Image", lang), type=["jpg", "jpeg", "png"])

if uploaded_file and model:
    # (FIX) Convert 4-channel PNGs (with transparency) to 3-channel RGB
    img = Image.open(uploaded_file).convert("RGB") 
    
    st.image(img, caption=t("Preview", lang), width=250)

    with st.spinner(t("Analyzing...", lang)):
        disease, scale = predict_image(model, img)

    # Display results
    col1, col2 = st.columns(2)
    with col1:
        bg_color = "#2e7d32, #4caf50" if disease == "Healthy Plant" else "#e65100, #ff8a65"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {bg_color}); color:white; padding:25px; border-radius:20px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.4); margin:10px; height: 180px;">
            <h3 style="margin:0; color:white; font-size:1.8rem;">{t('Disease Detected', lang)}</h3>
            <p style="font-size:32px; font-weight:700; margin:15px 0; color:white;">{t(disease, lang)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e7e34, #28a745); color:white; padding:25px; border-radius:20px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.4); margin:10px; height: 180px;">
            <h3 style="margin:0; color:white; font-size:1.8rem;">{t('Severity Level', lang)}</h3>
            <p style="font-size:32px; font-weight:700; margin:15px 0; color:white;">{scale}/9</p>
        </div>
        """, unsafe_allow_html=True)

    # Display treatment
    st.markdown(f"### {t('Treatment & Prevention', lang)}")
    if disease == "Healthy Plant":
        st.balloons()
        st.success(t("Your plant is healthy! No treatment needed.", lang))
    elif disease in ["Brown Spot", "Leaf Blast", "Sheath Blight"]:
        with st.spinner(t("Getting cure advice...", lang)):
            treatment_html, audio_text = get_treatment_from_llm(disease, lang)
        
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.95); padding:20px; border-radius:15px; color:#1B5E20; margin:15px 0;'>
            <p style='line-height:1.9; font-size:16px; margin:0;'>{treatment_html}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if lang == "Kannada" and audio_text:
            audio_bytes = get_kannada_audio_bytes(audio_text)
            if audio_bytes: st.audio(audio_bytes, autoplay=True, format="audio/mp3")
    else:
        st.error(t("An error occurred during prediction. Please try another image.", lang))
        
elif not model:
    st.error(t("Model not loaded. Please check file path.", lang))

# (NEW) Render the floating bot at the end
render_project_bot()