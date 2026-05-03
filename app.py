import streamlit as st
from textblob import TextBlob
import plotly.graph_objects as go
import tempfile
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
import time
from pydub import AudioSegment
import io
# ---------------- LOGIN SYSTEM ----------------
users = {
    "maam": "1234",
    "demo": "ai2026"
}

st.sidebar.title("🔐 Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if username in users and users[username] == password:
    st.sidebar.success("Access Granted ✅")
    access = True
else:
    st.sidebar.warning("Login required")
    access = False

if not access:
    st.stop()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="HireSense AI", page_icon="🎤", layout="wide")

# ---------------- ULTRA UI ----------------
st.markdown("""
<style>

/* BACKGROUND ANIMATION */
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

/* HERO */
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

/* BUTTONS */
.stButton>button {
    width: 100%;
    border-radius: 14px;
    background: linear-gradient(90deg,#06b6d4,#8b5cf6,#3b82f6);
    background-size: 200% 200%;
    animation: btnGlow 5s ease infinite;
    color: white;
    font-weight: bold;
    border: none;
    transition: 0.3s ease;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(0,255,255,0.4);
}

@keyframes btnGlow {
    0% {background-position: 0%;}
    50% {background-position: 100%;}
    100% {background-position: 0%;}
}

/* INPUTS */
textarea, input, select {
    border-radius: 12px !important;
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

/* METRICS */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06);
    border-radius: 15px;
    padding: 10px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(10,10,30,0.6);
    backdrop-filter: blur(10px);
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
<h1>🎤 HireSense AI</h1>
<p>Personalized AI Interview Simulator</p>
</div>
""", unsafe_allow_html=True)

# ---------------- PROFILE ----------------
st.sidebar.title("👤 Candidate Profile")

name = st.sidebar.text_input("Your Name")

role = st.sidebar.selectbox(
    "Target Role",
    ["Data Scientist", "Software Engineer", "Web Developer", "AI/ML Engineer", "Fresher"]
)

experience = st.sidebar.selectbox(
    "Experience Level",
    ["Student", "Intern", "Fresher", "1-2 Years", "3+ Years"]
)

st.markdown(f"""
### 👋 Welcome {name if name else 'Candidate'}  
🎯 Role: **{role}**  
📊 Experience: **{experience}**
""")

# ---------------- QUESTION BANK ----------------
question_bank = {
    "Data Scientist": [
        "Explain a machine learning project you worked on",
        "What is overfitting?",
        "How do you clean data?",
        "Correlation vs causation?"
    ],
    "Software Engineer": [
        "Explain OOP concepts",
        "What is time complexity?",
        "Describe a project",
        "Stack vs Queue?"
    ],
    "Web Developer": [
        "What is REST API?",
        "Frontend vs Backend?",
        "How does browser work?",
        "Explain HTML/CSS/JS"
    ],
    "AI/ML Engineer": [
        "What is neural network?",
        "Explain gradient descent",
        "What are hyperparameters?",
        "How does model training work?"
    ],
    "Fresher": [
        "Tell me about yourself",
        "Why should we hire you?",
        "What are your strengths?",
        "Where do you see yourself?"
    ]
}

questions = question_bank.get(role, [])
question = st.selectbox("🎯 Interview Question", questions)

# ---------------- VOICE INPUT ----------------
st.subheader("🎙 Voice Input")

audio = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording")

response = ""

if audio:
    try:
        audio_bytes = audio["bytes"]

        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wav_path = f.name
            audio_segment.export(wav_path, format="wav")

        recognizer = sr.Recognizer()

        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source)
            data = recognizer.record(source)

        response = recognizer.recognize_google(data, language="en-IN")

        st.success("Voice converted successfully 🎉")
        st.info(response)

    except Exception as e:
        st.error(f"Voice error: {e}")

response = st.text_area("Or type your answer", value=response)

# ---------------- ANALYSIS ----------------
def analyze(text):
    blob = TextBlob(text)

    polarity = blob.sentiment.polarity
    words = len(text.split())

    fillers = ["um", "uh", "like", "actually", "basically"]
    filler_count = sum(text.lower().split().count(w) for w in fillers)

    generic = ["hardworking", "passionate", "team player", "dedicated"]
    generic_count = sum(text.lower().count(w) for w in generic)

    confidence = min(words * 2, 100)
    clarity = min(words * 1.5, 100)
    relevance = min((abs(polarity) + 0.5) * 100, 100)
    authenticity = max(100 - (generic_count * 15) - (filler_count * 5), 0)

    return confidence, clarity, relevance, filler_count, authenticity

# ---------------- ANALYZE BUTTON ----------------
if st.button("🚀 Analyze Performance"):

    if response.strip():

        with st.spinner("AI analyzing..."):
            time.sleep(1.5)

        confidence, clarity, relevance, filler_count, authenticity = analyze(response)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Confidence", f"{confidence:.0f}%")
        c2.metric("Clarity", f"{clarity:.0f}%")
        c3.metric("Relevance", f"{relevance:.0f}%")
        c4.metric("Authenticity", f"{authenticity:.0f}%")

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[confidence, clarity, relevance, authenticity],
            theta=["Confidence", "Clarity", "Relevance", "Authenticity"],
            fill='toself'
        ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        avg = (confidence + clarity + relevance + authenticity) / 4
        st.subheader(f"Overall Score: {avg:.1f}%")
        st.progress(int(avg))

        st.markdown("## 🧠 Suggestions")

        suggestions = []

        if confidence < 50:
            suggestions.append("Improve confidence")

        if clarity < 50:
            suggestions.append("Structure your answer")

        if relevance < 60:
            suggestions.append("Stay relevant")

        if filler_count > 3:
            suggestions.append("Reduce filler words")

        if authenticity < 60:
            suggestions.append("Add real examples")

        if len(response.split()) < 20:
            suggestions.append("Elaborate more")

        if suggestions:
            for s in suggestions:
                st.warning("• " + s)
        else:
            st.success("Excellent response 🚀")

    else:
        st.warning("Please enter or record response")