# utils.py
import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
from io import BytesIO
import base64
import time
from langdetect import detect

# ----------------- Session State Init -----------------
def init_session_state():
    if "lang" not in st.session_state:
        st.session_state.lang = "English"

# ----------------- Global CSS -----------------
def apply_custom_css():
    init_session_state()
    st.markdown("""
    <style>
    /* Global */
    .stApp {
        background: url("https://images.unsplash.com/photo-1500595046743-cd271d6942ee?q=80&w=2074&auto.format&fit=crop") no-repeat center center fixed;
        background-size: cover;
        font-family: 'Montserrat', sans-serif;
    }
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(0,100,0,0.5), rgba(0,0,0,0.3));
        z-index: -1;
    }
    h1, h2, h3, h4, p, li, span, div { 
        color: #1B5E20 !important; 
        text-shadow: 0 1px 2px rgba(0,0,0,0.1); 
    }
    [data-testid="stSidebar"] { 
        background-color: rgba(230, 245, 230, 0.8) !important;
        backdrop-filter: blur(5px);
    }
    [data-testid="stChatContainer"] {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
    }
    .stButton>button{
        background:linear-gradient(45deg,#2E7D32,#4CAF50);
        color:white;border:none;border-radius:30px;
        padding:12px 24px;font-weight:600;font-size:16px;
        box-shadow:0 3px 10px rgba(0,0,0,0.2);
    }
    .stButton>button:hover{
        transform:translateY(-3px) scale(1.05);
        box-shadow:0 5px 15px rgba(0,0,0,0.3);
    }
    h1{font-size:3rem;text-align:center;animation:fadeInDown .5s;}
    @keyframes fadeInDown{from{opacity:0;transform:translateY(-20px);}to{opacity:1;transform:translateY(0);}}
    .streamlit-expanderHeader {
        background: linear-gradient(45deg, #2E7D32, #4CAF50) !important;
        color: white !important; border-radius: 15px !important;
        padding: 12px 20px !important; font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    .streamlit-expanderContent {
        background: rgba(255,255,255,0.95) !important;
        border-radius: 0 0 15px 15px !important;
        padding: 20px !important; margin-top: -10px !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------- Global Translator -----------------
@st.cache_data
def t(text, lang="en"):
    if lang == "English": return text
    if lang == "Kannada":
        try: return GoogleTranslator(source='en', target='kn').translate(text)
        except: return text
    return text

# ----------------- Global Language Toggle -----------------
def language_toggle():
    init_session_state()
    lang_options = ["English", "Kannada"]
    current_index = 1 if st.session_state.lang == "Kannada" else 0
    new_lang = st.selectbox(
        label="Language / ಭಾಷೆ", options=lang_options,
        index=current_index, key="lang_select_sidebar"
    )
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

# ----------------- (NEW) Global Audio Byte Generator -----------------
def get_kannada_audio_bytes(text: str):
    """Generates Kannada audio and returns it as bytes."""
    if not text:
        return None
    try:
        tts = gTTS(text=text, lang='kn', slow=False)
        audio_bytes_io = BytesIO()
        tts.write_to_fp(audio_bytes_io)
        audio_bytes_io.seek(0)
        return audio_bytes_io.read()
    except Exception as e:
        print(f"gTTS Error: {e}")
        st.error(f"TTS Error: {e}")
        return None

# ----------------- Translation Helpers -----------------
def translate_to_english(text):
    try:
        lang = detect(text)
        if lang == "en": return text, "en"
        return GoogleTranslator(source=lang, target="en").translate(text), lang
    except:
        return text, "kn" # Assume Kannada if detection fails

def translate_back(text, target_lang):
    try:
        if target_lang == "en": return text
        return GoogleTranslator(source="en", target=target_lang).translate(text)
    except:
        return text