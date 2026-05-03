import os
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

import streamlit as st
from textblob import TextBlob
import plotly.graph_objects as go
import time

# OPTIONAL VOICE IMPORT (safe)
try:
    import speech_recognition as sr
    from streamlit_mic_recorder import mic_recorder
    from pydub import AudioSegment
    import tempfile
    import io
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

# ---------------- LOGIN ----------------
users = {
    "maam": "1234",
    "demo": "ai2026"
}

st.sidebar.title("🔐 Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if username in users and users[username] == password:
    st.sidebar.success("Access Granted ✅")
else:
    st.sidebar.warning("Login required")
    st.stop()

# ---------------- USER INPUTS (ADDED FIX) ----------------
st.sidebar.title("👤 User Profile")

name = st.sidebar.text_input("Enter Your Name")
interest = st.sidebar.text_input("Field of Interest (AI, Web Dev, Data Science etc.)")

# ---------------- PAGE ----------------
st.set_page_config(page_title="HireSense AI", layout="wide")

# ---------------- UI ----------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(-45deg, #0f172a, #1e1b4b, #0f766e, #020617);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
    color: white;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.hero {
    text-align:center;
    padding:30px;
    border-radius:25px;
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 0 25px rgba(0,255,255,0.2);
    animation: floatCard 4s ease-in-out infinite;
}

@keyframes floatCard {
    0% {transform: translateY(0px);}
    50% {transform: translateY(-8px);}
    100% {transform: translateY(0px);}
}

.stButton>button {
    width: 100%;
    border-radius: 14px;
    background: linear-gradient(90deg,#06b6d4,#8b5cf6,#3b82f6);
    background-size: 200% 200%;
    animation: btnGlow 5s ease infinite;
    color: white;
    font-weight: bold;
    border: none;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(0,255,255,0.4);
}

textarea {
    border-radius: 12px !important;
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(f"""
<div class="hero">
<h1>🎤 HireSense AI</h1>
<p>AI Interview Simulator with Smart Feedback</p>
</div>

### 👋 Welcome {name if name else 'Candidate'}  
🎯 Field of Interest: **{interest if interest else 'Not Provided'}**
""", unsafe_allow_html=True)

# ---------------- ROLE ----------------
role = st.selectbox("🎯 Select Role", [
    "Data Scientist",
    "Software Engineer",
    "Web Developer",
    "AI/ML Engineer",
    "Fresher"
])

questions = {
    "Data Scientist": ["Explain ML project", "What is overfitting?"],
    "Software Engineer": ["What is OOP?", "Time complexity?"],
    "Web Developer": ["What is REST API?", "Frontend vs Backend?"],
    "AI/ML Engineer": ["What is neural network?", "Gradient descent?"],
    "Fresher": ["Tell me about yourself", "Why should we hire you?"]
}

question = st.selectbox("❓ Question", questions[role])
st.info(question)

# ---------------- VOICE INPUT ----------------
st.subheader("🎙 Answer Input")

response = ""

if VOICE_AVAILABLE:
    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop Recording"
    )

    if audio:
        try:
            audio_bytes = audio["bytes"]

            audio_segment = AudioSegment.from_file(
                io.BytesIO(audio_bytes),
                format="webm"
            )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                audio_segment.export(f.name, format="wav")

            r = sr.Recognizer()

            with sr.AudioFile(f.name) as source:
                audio_data = r.record(source)

            response = r.recognize_google(audio_data)
            st.success("Voice captured 🎉")

        except:
            st.error("Voice error (use text input)")

# fallback always
response = st.text_area("✍️ Type Answer", value=response)

# ---------------- ANALYSIS ----------------
def analyze(text):
    blob = TextBlob(text)
    words = len(text.split())

    confidence = min(words * 2, 100)
    clarity = min(words * 1.5, 100)
    relevance = 80
    authenticity = max(100 - words, 40)

    return confidence, clarity, relevance, authenticity

# ---------------- BUTTON ----------------
if st.button("🚀 Analyze"):

    if response.strip():

        confidence, clarity, relevance, authenticity = analyze(response)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Confidence", f"{confidence:.0f}%")
        c2.metric("Clarity", f"{clarity:.0f}%")
        c3.metric("Relevance", f"{relevance:.0f}%")
        c4.metric("Authenticity", f"{authenticity:.0f}%")

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[confidence, clarity, relevance, authenticity],
            theta=["Confidence","Clarity","Relevance","Authenticity"],
            fill='toself'
        ))

        st.plotly_chart(fig, use_container_width=True)

        avg = (confidence + clarity + relevance + authenticity)/4

        st.subheader(f"Overall Score: {avg:.1f}%")
        st.progress(int(avg))

        st.subheader("🧠 Suggestions")

        if confidence < 60:
            st.warning("Improve confidence")
        if clarity < 60:
            st.warning("Structure answers better")
        if len(response.split()) < 20:
            st.warning("Elaborate more")
        else:
            st.success("Good response 🚀")

    else:
        st.warning("Enter answer first")
        