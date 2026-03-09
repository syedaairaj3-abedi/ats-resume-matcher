import streamlit as st
import streamlit.components.v1 as components

from parser import extract_text_from_pdf
from scorer import overall_score

st.set_page_config(page_title="ATS Resume Matcher", page_icon="✨", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    color: #2b2b2b !important;
}

p, span, div, label, li {
    color: #2b2b2b !important;
}

h1, h2, h3, h4 {
    color: #1f1f1f !important;
}

.stApp {
    background: linear-gradient(180deg, #ffeef6 0%, #fff4f9 45%, #fff9fc 100%) !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1150px;
    position: relative;
    z-index: 2;
}

.title-box {
    text-align: center;
    padding: 2rem 1.2rem;
    border-radius: 28px;
    background: rgba(255, 255, 255, 0.82);
    box-shadow: 0 12px 40px rgba(255, 182, 193, 0.22);
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 210, 225, 0.95);
    backdrop-filter: blur(12px);
}

.title-box h1 {
    font-size: 3rem;
    margin-bottom: 0.4rem;
    color: #2d2d2d !important;
}

.title-box p {
    font-size: 1.08rem;
    color: #6a5963 !important;
}

.result-card {
    background: rgba(255, 255, 255, 0.92);
    padding: 1.2rem 1.3rem;
    border-radius: 24px;
    box-shadow: 0 10px 28px rgba(255, 182, 193, 0.18);
    margin-bottom: 1rem;
    border: 1px solid rgba(255, 214, 230, 0.95);
    backdrop-filter: blur(10px);
}

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.78);
    border-radius: 22px;
    padding: 0.6rem;
    box-shadow: 0 8px 24px rgba(255, 182, 193, 0.14);
    border: 1px solid rgba(255, 214, 230, 0.9);
}

[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.86) !important;
    color: #2b2b2b !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255, 214, 230, 0.95) !important;
    box-shadow: 0 8px 24px rgba(255, 182, 193, 0.12) !important;
}

div.stButton > button {
    background: linear-gradient(90deg, #ffb7d5, #ffd86f);
    color: #2f2227 !important;
    border: none;
    border-radius: 18px;
    padding: 0.82rem 1.9rem;
    font-size: 1.05rem;
    font-weight: 700;
    box-shadow: 0 8px 22px rgba(255, 182, 193, 0.28);
}

div.stButton > button:hover {
    transform: scale(1.04);
    transition: 0.2s ease-in-out;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.90);
    border: 1px solid rgba(255, 214, 230, 0.92);
    padding: 0.9rem;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(255, 182, 193, 0.14);
}

[data-testid="stMetricLabel"] {
    color: #4a4a4a !important;
}

[data-testid="stMetricValue"] {
    color: #222 !important;
}

.floating {
    position: fixed;
    z-index: 1;
    pointer-events: none;
    opacity: 0.88;
    animation-name: floaty;
    animation-timing-function: ease-in-out;
    animation-iteration-count: infinite;
}

@keyframes floaty {
    0%   { transform: translateY(0px) translateX(0px) rotate(0deg) scale(1); }
    25%  { transform: translateY(-18px) translateX(10px) rotate(8deg) scale(1.05); }
    50%  { transform: translateY(-32px) translateX(-8px) rotate(-8deg) scale(1.1); }
    75%  { transform: translateY(-16px) translateX(12px) rotate(6deg) scale(1.03); }
    100% { transform: translateY(0px) translateX(0px) rotate(0deg) scale(1); }
}

.sep-line {
    width: 100%;
    height: 28px;
    border: 1.5px solid #f6c7d7;
    border-radius: 30px;
    margin: 18px 0 10px 0;
    background: rgba(255,255,255,0.25);
}
</style>
""", unsafe_allow_html=True)

floating_html = """
<div class="floating" style="left:2%;top:10%;font-size:24px;animation-duration:8s;">🌸</div>
<div class="floating" style="left:6%;top:24%;font-size:26px;animation-duration:11s;">✨</div>
<div class="floating" style="left:4%;top:48%;font-size:20px;animation-duration:9s;">💫</div>
<div class="floating" style="left:8%;top:72%;font-size:28px;animation-duration:10s;">🌷</div>
<div class="floating" style="left:10%;top:88%;font-size:22px;animation-duration:12s;">⭐</div>

<div class="floating" style="left:16%;top:8%;font-size:20px;animation-duration:7s;">❀</div>
<div class="floating" style="left:18%;top:32%;font-size:24px;animation-duration:10s;">🌼</div>
<div class="floating" style="left:20%;top:58%;font-size:21px;animation-duration:8s;">🩷</div>
<div class="floating" style="left:22%;top:82%;font-size:26px;animation-duration:11s;">✨</div>

<div class="floating" style="left:28%;top:12%;font-size:24px;animation-duration:9s;">🌸</div>
<div class="floating" style="left:30%;top:26%;font-size:19px;animation-duration:7s;">⋆</div>
<div class="floating" style="left:32%;top:46%;font-size:22px;animation-duration:10s;">💫</div>
<div class="floating" style="left:34%;top:70%;font-size:26px;animation-duration:8s;">🌷</div>
<div class="floating" style="left:36%;top:90%;font-size:18px;animation-duration:12s;">✿</div>

<div class="floating" style="left:42%;top:10%;font-size:20px;animation-duration:8s;">⭐</div>
<div class="floating" style="left:44%;top:30%;font-size:28px;animation-duration:11s;">🌼</div>
<div class="floating" style="left:46%;top:54%;font-size:20px;animation-duration:9s;">✨</div>
<div class="floating" style="left:48%;top:76%;font-size:22px;animation-duration:7s;">🩷</div>

<div class="floating" style="left:54%;top:8%;font-size:24px;animation-duration:10s;">🌸</div>
<div class="floating" style="left:56%;top:24%;font-size:18px;animation-duration:8s;">❀</div>
<div class="floating" style="left:58%;top:42%;font-size:24px;animation-duration:12s;">💫</div>
<div class="floating" style="left:60%;top:64%;font-size:30px;animation-duration:9s;">🌷</div>
<div class="floating" style="left:62%;top:88%;font-size:20px;animation-duration:11s;">⭐</div>

<div class="floating" style="left:68%;top:12%;font-size:22px;animation-duration:10s;">✨</div>
<div class="floating" style="left:70%;top:34%;font-size:24px;animation-duration:7s;">🌼</div>
<div class="floating" style="left:72%;top:56%;font-size:18px;animation-duration:9s;">✿</div>
<div class="floating" style="left:74%;top:80%;font-size:26px;animation-duration:12s;">🩷</div>

<div class="floating" style="left:80%;top:10%;font-size:24px;animation-duration:8s;">🌸</div>
<div class="floating" style="left:82%;top:28%;font-size:30px;animation-duration:11s;">💫</div>
<div class="floating" style="left:84%;top:48%;font-size:20px;animation-duration:9s;">✨</div>
<div class="floating" style="left:86%;top:70%;font-size:24px;animation-duration:10s;">🌷</div>
<div class="floating" style="left:88%;top:90%;font-size:18px;animation-duration:7s;">⋆</div>

<div class="floating" style="left:92%;top:16%;font-size:24px;animation-duration:12s;">⭐</div>
<div class="floating" style="left:94%;top:40%;font-size:22px;animation-duration:8s;">🌼</div>
<div class="floating" style="left:96%;top:76%;font-size:26px;animation-duration:10s;">🌸</div>
"""
st.markdown(floating_html, unsafe_allow_html=True)

components.html(
    """
    <script>
    const sparkleSymbols = ["✨","💫","⭐","🌸","🩷","🌷","🌼","❀","⋆","✿"];
    let lastSparkleTime = 0;

    window.addEventListener("mousemove", function(e) {
        const now = Date.now();
        if (now - lastSparkleTime < 20) return;
        lastSparkleTime = now;

        for (let i = 0; i < 10; i++) {
            const sparkle = document.createElement("div");
            sparkle.textContent = sparkleSymbols[Math.floor(Math.random() * sparkleSymbols.length)];
            sparkle.style.position = "fixed";
            sparkle.style.left = e.clientX + "px";
            sparkle.style.top = e.clientY + "px";
            sparkle.style.pointerEvents = "none";
            sparkle.style.zIndex = "999999";
            sparkle.style.fontSize = (10 + Math.random() * 12) + "px";
            sparkle.style.opacity = "1";
            sparkle.style.transition = "all 0.8s ease-out";
            document.body.appendChild(sparkle);

            const dx = (Math.random() - 0.5) * 80;
            const dy = (Math.random() - 0.5) * 80;

            requestAnimationFrame(() => {
                sparkle.style.transform = `translate(${dx}px, ${dy}px) scale(1.3)`;
                sparkle.style.opacity = "0";
            });

            setTimeout(() => sparkle.remove(), 800);
        }
    });
    </script>
    """,
    height=0,
    width=0,
)

st.markdown("""
<div class="title-box">
    <h1>✨ ATS Resume Matcher ✨</h1>
    <p>Upload your resume, paste the job description, and click scan to see your ATS-style match score.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

with col2:
    job_description = st.text_area("Paste Job Description", height=260)

scan_clicked = st.button("Scan Resume")

if scan_clicked:
    if not uploaded_resume or not job_description.strip():
        st.warning("Please upload a resume and paste a job description first.")
    else:
        with st.spinner("Scanning your resume..."):
            resume_text = extract_text_from_pdf(uploaded_resume)
            results = overall_score(resume_text, job_description)

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.subheader("Overall Match")
        st.metric("ATS-Style Match Score", f"{results['overall_score']:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Exact Match", f"{results['exact_score']:.2f}%")
        c2.metric("Semantic", f"{results['semantic_score']:.2f}%")
        c3.metric("TF-IDF", f"{results['tfidf_score']:.2f}%")
        c4.metric("Requirements", f"{results['required_score']:.2f}%")
        c5.metric("Parsing", f"{results['parse_score']:.2f}%")

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.subheader("What These Scores Mean")
        st.write("• **Exact Match** = direct phrase match between your resume and the job description.")
        st.write("• **Semantic** = meaning similarity, even if the exact wording is different.")
        st.write("• **TF-IDF** = statistical text overlap strength between important terms.")
        st.write("• **Requirements** = how much of the job’s required qualifications your resume covers.")
        st.write("• **Parsing** = how ATS-friendly your resume structure and formatting appear.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.subheader("Smart Resume Feedback")
        for item in results["feedback"]:
            st.write(f"• {item}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sep-line"></div>', unsafe_allow_html=True)

        st.subheader("Matched Keywords and Phrases")
        for kw in results["matched_keywords"]:
            st.write(f"• {kw}")

        st.markdown('<div class="sep-line"></div>', unsafe_allow_html=True)

        st.subheader("Most Important Missing Keywords and Phrases")
        for kw in results["missing_keywords"]:
            st.write(f"• {kw}")

        st.markdown('<div class="sep-line"></div>', unsafe_allow_html=True)

        st.subheader("Technical Skills Missing")
        if results["technical_missing"]:
            for kw in results["technical_missing"]:
                st.write(f"• {kw}")
        else:
            st.write("• No major technical skill gaps detected.")

        st.subheader("Business / Role Language Missing")
        if results["business_missing"]:
            for kw in results["business_missing"]:
                st.write(f"• {kw}")
        else:
            st.write("• No major business language gaps detected.")

        st.subheader("Soft Skills Missing")
        if results["soft_missing"]:
            for kw in results["soft_missing"]:
                st.write(f"• {kw}")
        else:
            st.write("• No major soft-skill gaps detected.")

        st.markdown('<div class="sep-line"></div>', unsafe_allow_html=True)

        st.subheader("Covered Qualification Phrases")
        if results["covered_requirements"]:
            for item in results["covered_requirements"]:
                st.write(f"• {item}")
        else:
            st.write("• No strong coverage detected yet.")

        st.markdown('<div class="sep-line"></div>', unsafe_allow_html=True)

        st.subheader("Parsing / Structure Warnings")
        if results["warnings"]:
            for warning in results["warnings"]:
                st.write(f"• {warning}")
        else:
            st.write("• No major parsing warnings detected.")

        st.markdown('<div class="sep-line"></div>', unsafe_allow_html=True)

        st.subheader("How to Improve")
        for item in results["specific_improvements"]:
            st.write(f"• {item}")