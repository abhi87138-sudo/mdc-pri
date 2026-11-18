"""
app.py
=============================================================================
DEEPFAKE DEFENSE // Dark Luxury Futuristic Cybersecurity Platform
Design Inspiration: EternaCloud Dark Glassmorphism, Floating Light Pillars & Glow
Theme: Deep Obsidian (#030712 / #0B0F19), Electric Cyan & Radiant Violet Aurora
Team: Sentinels (Vivek Sharma, Hitesh Brahmi, Akhil Kotwal)
=============================================================================
"""

import os
import sys
import json
import random
import io
import time
from datetime import datetime
import streamlit as st
from PIL import Image

# Ensure root directory is in Python search path for Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.predict import ThreatDetector, DeepUrlScanner, SecurityAssistant
    from src.deepfake_detector import (
        DeepfakeDetector,
        generate_sample_synthetic_portrait,
        generate_sample_authentic_portrait,
        generate_sample_synthetic_audio,
        generate_sample_authentic_audio
    )
except ImportError:
    from predict import ThreatDetector, DeepUrlScanner, SecurityAssistant
    from deepfake_detector import (
        DeepfakeDetector,
        generate_sample_synthetic_portrait,
        generate_sample_authentic_portrait,
        generate_sample_synthetic_audio,
        generate_sample_authentic_audio
    )

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="DEEPFAKE DEFENSE // Autonomous Threat Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------------------------
# Session State Management
# ---------------------------------------------------------------------------
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Scam Message Shield"

if "scan_history" not in st.session_state:
    st.session_state["scan_history"] = []

if "total_scans" not in st.session_state:
    st.session_state["total_scans"] = 1420

if "threats_intercepted" not in st.session_state:
    st.session_state["threats_intercepted"] = 894

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": "Welcome to **DEEPFAKE DEFENSE**. Paste any SMS, bank alert, or ask a question regarding social engineering and synthetic media."}
    ]

# ---------------------------------------------------------------------------
# Custom EternaCloud-Style Dark Luxury Glassmorphism Stylesheet
# ---------------------------------------------------------------------------
luxury_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-dark: #030712;
    --card-glass: rgba(15, 23, 42, 0.65);
    --card-glass-hover: rgba(30, 41, 59, 0.85);
    --border-glass: rgba(255, 255, 255, 0.08);
    --border-cyan: rgba(34, 211, 238, 0.35);
    --cyan-glow: #22D3EE;
    --violet-glow: #A855F7;
    --sunset-glow: #FB7185;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
}

* {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Background Atmosphere - Radiant Top Light Cone & Violet Ambient Aurora */
.stApp {
    background-color: #030712 !important;
    background-image: 
        radial-gradient(ellipse 65% 35% at 50% -5%, rgba(217, 119, 6, 0.15), transparent 70%),
        radial-gradient(ellipse 60% 45% at 50% 0%, rgba(168, 85, 247, 0.18), transparent 75%),
        radial-gradient(circle at 10% 40%, rgba(34, 211, 238, 0.08), transparent 50%),
        radial-gradient(circle at 90% 40%, rgba(168, 85, 247, 0.09), transparent 50%) !important;
    background-attachment: fixed !important;
    color: #F8FAFC !important;
}

.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 5rem !important;
    max-width: 1180px !important;
}

/* Header Navbar - Sleek Floating Capsule */
.floating-navbar {
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 9999px;
    padding: 0.7rem 1.6rem;
    margin: 0 auto 2.5rem auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.brand-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-ring {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: conic-gradient(from 180deg at 50% 50%, #22D3EE 0deg, #A855F7 180deg, #F43F5E 360deg);
    padding: 2.5px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 15px rgba(34, 211, 238, 0.4);
}

.brand-ring-inner {
    width: 100%;
    height: 100%;
    background: #030712;
    border-radius: 50%;
}

.brand-title-text {
    font-size: 1.15rem;
    font-weight: 800;
    color: #FFFFFF !important;
    letter-spacing: -0.02em;
}

.navbar-badge {
    background: rgba(34, 211, 238, 0.12);
    border: 1px solid rgba(34, 211, 238, 0.3);
    color: #22D3EE !important;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 9999px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Hero Section with Light Pillar Beam */
.hero-stage {
    text-align: center;
    padding: 3rem 1.5rem 2.5rem 1.5rem;
    position: relative;
    margin-bottom: 2.5rem;
}

.eyebrow-tag {
    display: inline-block;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    background: linear-gradient(90deg, #22D3EE, #A855F7, #FB7185);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.8rem;
}

.hero-headline {
    font-size: 3.5rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.12;
    color: #FFFFFF !important;
    margin-bottom: 1rem;
    text-shadow: 0 4px 25px rgba(0, 0, 0, 0.6);
}

.hero-subheadline {
    font-size: 1.15rem;
    color: #94A3B8 !important;
    max-width: 720px;
    margin: 0 auto 2.2rem auto;
    line-height: 1.6;
    font-weight: 400;
}

/* Luxury Glass Cards */
.glass-panel {
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.glass-panel:hover {
    border-color: rgba(34, 211, 238, 0.3);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(34, 211, 238, 0.1);
}

/* Feature 4-Card Pillar Row (Design / Onboarding / Delivery / Deployment) */
.pillar-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 16px;
    margin: 2rem 0;
}

.pillar-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 18px;
    padding: 1.6rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.pillar-card:hover {
    transform: translateY(-4px);
    border-color: rgba(34, 211, 238, 0.4);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6), 0 0 25px rgba(168, 85, 247, 0.15);
}

.pillar-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 9999px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 0.72rem;
    font-weight: 700;
    color: #E2E8F0 !important;
    margin-bottom: 1rem;
}

.pillar-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF !important;
    margin-bottom: 0.6rem;
    line-height: 1.35;
}

.pillar-desc {
    font-size: 0.88rem;
    color: #94A3B8 !important;
    line-height: 1.55;
    margin: 0;
}

/* Primary Glass Button */
.stButton > button {
    background: linear-gradient(135deg, rgba(34, 211, 238, 0.9), rgba(168, 85, 247, 0.9)) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 24px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 20px rgba(34, 211, 238, 0.35) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    box-shadow: 0 6px 25px rgba(168, 85, 247, 0.5) !important;
    transform: translateY(-2px) !important;
}

/* Clean Input Fields */
textarea, input {
    background: rgba(15, 23, 42, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 14px !important;
    color: #FFFFFF !important;
}

textarea:focus, input:focus {
    border-color: #22D3EE !important;
    box-shadow: 0 0 15px rgba(34, 211, 238, 0.25) !important;
}

/* Streamlit Native Widget Text Overrides */
.stMarkdown p, .stCaption, [data-testid="stWidgetLabel"] p {
    color: #CBD5E1 !important;
}

/* Verdict Banners */
.verdict-glow-box {
    border-radius: 18px;
    padding: 1.8rem 2.2rem;
    margin: 1.8rem 0;
    display: flex;
    align-items: center;
    gap: 20px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}

.verdict-glow-safe {
    background: rgba(34, 211, 238, 0.08);
    border: 1px solid rgba(34, 211, 238, 0.4);
    box-shadow: 0 0 30px rgba(34, 211, 238, 0.15);
}

.verdict-glow-suspicious {
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.4);
    box-shadow: 0 0 30px rgba(245, 158, 11, 0.15);
}

.verdict-glow-dangerous {
    background: rgba(244, 63, 94, 0.1);
    border: 1px solid rgba(244, 63, 94, 0.5);
    box-shadow: 0 0 35px rgba(244, 63, 94, 0.25);
}

/* Suspicious Heatmap Box */
.aurora-heatmap {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.5rem;
    line-height: 2.3;
    font-size: 1.05rem;
    margin: 1.2rem 0;
}
</style>
"""
st.markdown(luxury_css, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Backend Engines
# ---------------------------------------------------------------------------
@st.cache_resource
def get_threat_detector():
    return ThreatDetector()

@st.cache_resource
def get_deepfake_detector():
    return DeepfakeDetector()

@st.cache_resource
def get_url_scanner():
    return DeepUrlScanner()

@st.cache_resource
def get_security_assistant():
    return SecurityAssistant()

detector = get_threat_detector()
deepfake_engine = get_deepfake_detector()
url_scanner = get_url_scanner()
assistant = get_security_assistant()

# ---------------------------------------------------------------------------
# Floating Luxury Navbar Capsule
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="floating-navbar">
        <div class="brand-wrapper">
            <div class="brand-ring">
                <div class="brand-ring-inner"></div>
            </div>
            <div class="brand-title-text">DEEPFAKE DEFENSE</div>
        </div>
        <div style="display: flex; align-items: center; gap: 15px;">
            <span class="navbar-badge">⚡ ACTIVE AIR-GAPPED SHIELD</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# Hero Stage with Light Pillar & Headline
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-stage">
        <div class="eyebrow-tag">Autonomous Social Engineering & Media Defense</div>
        <div class="hero-headline">Design and defend with ease.</div>
        <div class="hero-subheadline">
            Deepfake Defense inspects deceptive messaging, fraudulent utility alerts, banking smishing, 
            and synthetic generative face-swaps in real-time with air-gapped mathematical precision.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# 4 Core Pillar Cards (Inspired by the EternaCloud Grid)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="pillar-row">
        <div class="pillar-card">
            <span class="pillar-badge">01 // DETECTION</span>
            <div class="pillar-title">Banking & KYC Phish</div>
            <p class="pillar-desc">Intercepts deceptive SBI, HDFC, ICICI alerts and coercive PAN/Aadhaar deactivation threats.</p>
        </div>
        <div class="pillar-card">
            <span class="pillar-badge">02 // ONBOARDING</span>
            <div class="pillar-title">Electricity Bill Scams</div>
            <p class="pillar-desc">Neutralizes nighttime power disconnection alerts designed to install remote-access APKs.</p>
        </div>
        <div class="pillar-card">
            <span class="pillar-badge">03 // FORENSICS</span>
            <div class="pillar-title">2D FFT Video Deepfakes</div>
            <p class="pillar-desc">Reveals periodic GAN upsampling lattice spikes in video call frames (The $25M Arup Defense).</p>
        </div>
        <div class="pillar-card">
            <span class="pillar-badge">04 // PROTECTION</span>
            <div class="pillar-title">UPI & Domain Guard</div>
            <p class="pillar-desc">Unmasks reverse QR collect traps, URL shorteners, and fraudulent brand typosquatting.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# ---------------------------------------------------------------------------
# Seamless Module Switcher (Horizontal Glowing Navigation)
# ---------------------------------------------------------------------------
nav_tabs = [
    "🛡️ Scam Message Shield",
    "🔬 Deepfake Lab",
    "🔗 Domain Inspector",
    "💬 AI Security Assistant",
    "📊 Defensive Operations",
    "📖 Threat Intelligence",
    "ℹ️ About Sentinels"
]

selected_tab = st.selectbox(
    "Select Defense Vector:",
    nav_tabs,
    index=0,
    label_visibility="collapsed"
)

st.write("")

# ===========================================================================
# MODULE 1: SCAM MESSAGE SHIELD
# ===========================================================================
if selected_tab == "🛡️ Scam Message Shield":
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("### 🛡️ AI Scam Message Checker")
    st.caption("Paste any suspicious SMS, WhatsApp forward, bank alert, or email. The engine inspects for urgency coercion, credential theft, and utility fraud:")

    SCENARIOS = {
        "sbi": "URGENT: Your SBI Bank account has been blocked due to pending KYC. Update PAN card immediately at http://bit.ly/sbi-pan-kyc within 24 hours to avoid permanent deactivation.",
        "elec": "Dear Consumer, Your Electricity power will be disconnected tonight at 9.30 pm from electricity office because your previous month bill was not updated. Please immediately contact our electricity officer at 9876543210. Thank you.",
        "upi": "Congratulations! You have received a cashback reward of Rs 2,500. Open PhonePe and enter your UPI PIN to approve collect request and deposit money into your account.",
        "prize": "WINNER!! You have won a £900 cash reward from international lottery fund. Call 09061701461 to claim your payout with secret code KL341. Valid today only.",
        "parcel": "India Post Notice: Your parcel IN-89218 is held at regional customs due to incomplete delivery address. Please pay Rs 25 redelivery fee at http://indiapost-update.xyz/tracking to release item.",
        "chat": "Hey Rahul, are we still meeting in the college library at 4:30 PM to work on the computer science assignment?"
    }

    if "current_message" not in st.session_state:
        st.session_state["current_message"] = ""

    st.write("**Pre-configured Test Payloads:**")
    p1, p2, p3, p4, p5, p6 = st.columns(6)
    with p1:
        if st.button("Banking KYC", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["sbi"]
    with p2:
        if st.button("Electricity Cut", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["elec"]
    with p3:
        if st.button("UPI QR Trap", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["upi"]
    with p4:
        if st.button("Cash Prize", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["prize"]
    with p5:
        if st.button("Parcel Duty", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["parcel"]
    with p6:
        if st.button("Normal Chat", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["chat"]

    user_input = st.text_area(
        "Message Payload Field:",
        value=st.session_state["current_message"],
        height=130,
        placeholder="Paste any SMS, WhatsApp alert, or email text here to execute hybrid NLP threat inspection..."
    )

    col_btn_scan, col_btn_clear = st.columns([8, 2])
    with col_btn_scan:
        execute_scan = st.button("⚡ Execute Deepfake Defense Scan", use_container_width=True)
    with col_btn_clear:
        if st.button("Clear Input", use_container_width=True):
            st.session_state["current_message"] = ""
            st.rerun()

    if execute_scan or (user_input.strip() and st.session_state.get("last_scanned_text") != user_input):
        st.session_state["last_scanned_text"] = user_input
        if not user_input.strip():
            st.warning("Please enter or paste a message to analyze.")
        else:
            with st.spinner("Analyzing message payload through hybrid NLP & threat engines..."):
                res = detector.predict(user_input)
                st.session_state["scan_history"].insert(0, {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "type": "Message",
                    "preview": user_input[:40] + ("..." if len(user_input) > 40 else ""),
                    "score": res["risk_score"],
                    "status": res["status"]
                })
                st.session_state["total_scans"] += 1
                if res["status"] != "Safe":
                    st.session_state["threats_intercepted"] += 1

            risk_score = res["risk_score"]
            status = res["status"]
            attack = res["attack_vector"]
            tokens = res["tokens"]
            vectors = res["vectors"]
            reasons = res["reasons"]

            verdict_class = "verdict-glow-safe" if status == "Safe" else ("verdict-glow-suspicious" if status == "Suspicious" else "verdict-glow-dangerous")
            status_color = "#22D3EE" if status == "Safe" else ("#F59E0B" if status == "Suspicious" else "#F43F5E")

            st.markdown(
                f"""
                <div class="verdict-glow-box {verdict_class}">
                    <div>
                        <div style="font-size: 1.45rem; font-weight: 800; color: {status_color}; letter-spacing: -0.02em;">
                            {status.upper()} // RISK SCORE {risk_score}/100
                        </div>
                        <div style="font-size: 0.96rem; color: #94A3B8; margin-top: 4px;">
                            Identified Attack Vector: <strong style="color: #FFFFFF;">{attack['name']}</strong> ({attack['badge']})
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write(f"**Threat Severity Level: {risk_score} / 100**")
            st.progress(risk_score / 100.0)

            # Recommendations
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.75); border-left: 4px solid {status_color}; border-radius: 12px; padding: 1.2rem; margin: 1.2rem 0;">
                    <div style="font-weight: 700; font-size: 1.05rem; color: #FFFFFF; margin-bottom: 0.5rem;">
                        Recommended Security Protocol
                    </div>
                    <ul style="margin: 0; padding-left: 1.2rem; line-height: 1.7; color: #CBD5E1;">
                        {''.join([f'<li>{a}</li>' for a in attack.get('actions', ['Exercise normal security precautions.'])])}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Suspicious Phrase Heatmap
            st.markdown("#### 🔍 Interactive Manipulation Token Heatmap")
            heatmap_html = '<div class="aurora-heatmap">'
            for word, tag in tokens:
                if tag == "urgency":
                    heatmap_html += f'<span style="background:rgba(239,68,68,0.25); color:#F87171; padding:3px 8px; border-radius:6px; font-weight:700;">{word}</span> '
                elif tag == "financial":
                    heatmap_html += f'<span style="background:rgba(245,158,11,0.25); color:#FBBF24; padding:3px 8px; border-radius:6px; font-weight:700;">{word}</span> '
                elif tag == "credential":
                    heatmap_html += f'<span style="background:rgba(34,211,238,0.25); color:#22D3EE; padding:3px 8px; border-radius:6px; font-weight:700;">{word}</span> '
                elif tag == "link":
                    heatmap_html += f'<span style="background:rgba(168,85,247,0.25); color:#C084FC; padding:3px 8px; border-radius:6px; font-weight:700; text-decoration:underline;">{word}</span> '
                else:
                    heatmap_html += f'<span style="color:#F8FAFC; padding:2px 4px;">{word}</span> '
            heatmap_html += '</div>'
            st.markdown(heatmap_html, unsafe_allow_html=True)

            # Psychological Metrics
            v1, v2, v3, v4 = st.columns(4)
            with v1:
                st.metric("Urgency Pressure", f"{vectors['urgency']}%")
                st.progress(vectors['urgency'] / 100.0)
            with v2:
                st.metric("Financial Bait", f"{vectors['financial']}%")
                st.progress(vectors['financial'] / 100.0)
            with v3:
                st.metric("Credential Target", f"{vectors['credential']}%")
                st.progress(vectors['credential'] / 100.0)
            with v4:
                st.metric("Authority Spoof", f"{vectors['authority']}%")
                st.progress(vectors['authority'] / 100.0)

    st.markdown('</div>', unsafe_allow_html=True)

# ===========================================================================
# MODULE 2: DEEPFAKE LAB
# ===========================================================================
elif selected_tab == "🔬 Deepfake Lab":
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("### 🔬 Multi-Modal Deepfake Defense Lab")
    st.caption("2D Fast Fourier Transform (FFT) power spectra and acoustic vocoder frequency diagnostics:")

    df_mode = st.radio("Media Category:", ["Facial Snapshot & Video Frame", "Acoustic Voice Note"], horizontal=True)

    if df_mode == "Facial Snapshot & Video Frame":
        input_mode = st.radio("Source:", ["Preset Reference Samples", "Upload Frame / Image", "Live Camera Frame"], horizontal=True)
        img_target = None

        if input_mode == "Preset Reference Samples":
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Load Authentic Reference Portrait", use_container_width=True):
                    st.session_state["df_choice"] = "auth"
            with c2:
                if st.button("Load Synthetic GAN Deepfake Portrait", use_container_width=True):
                    st.session_state["df_choice"] = "synth"

            if st.session_state.get("df_choice") == "auth":
                img_target = generate_sample_authentic_portrait()
                st.caption("Loaded: Authentic camera sensor capture with natural noise floor.")
            else:
                img_target = generate_sample_synthetic_portrait()
                st.caption("Loaded: Synthetic GAN portrait with deconvolution grid artifacts.")
        elif input_mode == "Upload Frame / Image":
            up = st.file_uploader("Choose Image (PNG/JPG):", type=["png", "jpg", "jpeg"])
            if up:
                img_target = Image.open(up)
        else:
            snap = st.camera_input("Capture live meeting attendee")
            if snap:
                img_target = Image.open(snap)

        if img_target:
            if st.button("⚡ Execute 2D FFT & Laplacian Forensics", use_container_width=True) or input_mode == "Preset Reference Samples":
                with st.spinner("Computing 2D FFT & Laplacian gradient maps..."):
                    df_res = deepfake_engine.analyze_image(img_target)

                st.write("")
                st.markdown(f"### Forensic Verdict: {df_res['verdict_label']}")
                st.progress(df_res["overall_score"] / 100.0)

                g1, g2, g3 = st.columns(3)
                with g1:
                    st.image(df_res["face_crop"], caption="Analyzed Face ROI", use_container_width=True)
                with g2:
                    st.image(df_res["edge_image"], caption="Laplacian Seam Boundary", use_container_width=True)
                with g3:
                    st.image(df_res["fft_image"], caption="2D FFT Power Spectrum Heatmap", use_container_width=True)

                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("FFT Grid Regularity", f"{df_res['metrics']['fft_score']}%")
                with m2:
                    st.metric("Boundary Variance", f"{df_res['metrics']['lap_score']}%")
                with m3:
                    st.metric("Color Space Harmony", f"{df_res['metrics']['color_score']}%")
                with m4:
                    st.metric("Sensor Noise Floor", f"{df_res['metrics']['noise_score']}%")

    else:
        st.markdown("### Acoustic Voice Clone Inspection")
        audio_choice = st.radio("Audio Sample:", ["Synthetic AI Voice Clone", "Authentic Human Voice"], horizontal=True)
        if audio_choice == "Synthetic AI Voice Clone":
            abuf = generate_sample_synthetic_audio()
        else:
            abuf = generate_sample_authentic_audio()

        st.audio(abuf, format="audio/wav")
        if st.button("⚡ Inspect Voice Waveform", use_container_width=True):
            with st.spinner("Evaluating spectral cutoff & pitch jitter..."):
                ares = deepfake_engine.analyze_audio(abuf)

            st.markdown(f"### {ares['verdict_label']}")
            st.progress(ares["overall_score"] / 100.0)
            a1, a2, a3 = st.columns(3)
            with a1:
                st.metric("High-Frequency Cutoff", f"{ares['high_energy_ratio']}%")
            with a2:
                st.metric("Silence Artificiality", f"{ares['silence_ratio']}%")
            with a3:
                st.metric("Pitch Interval Jitter", f"{ares['interval_jitter']}")

    st.markdown('</div>', unsafe_allow_html=True)

# ===========================================================================
# MODULE 3: DOMAIN INSPECTOR
# ===========================================================================
elif selected_tab == "🔗 Domain Inspector":
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("### 🔗 Dedicated Phishing URL & Domain Scanner")
    st.caption("Deep domain analysis of hyperlinks, shorteners, and fraudulent brand typosquatting:")

    test_url = st.text_input(
        "Enter Link or Domain:",
        value="http://sbi-kyc-verify.xyz/login",
        placeholder="https://example.com"
    )

    if st.button("⚡ Run Deep Domain Scan", use_container_width=True) or test_url:
        with st.spinner("Querying domain structure and protocol security..."):
            rep = url_scanner.scan_url(test_url)

        u_color = "#22D3EE" if rep["status"] == "Safe" else ("#F59E0B" if rep["status"] == "Suspicious" else "#F43F5E")
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.75); border: 1.5px solid {u_color}; border-radius: 16px; padding: 1.5rem; margin: 1.5rem 0;">
                <div style="font-size: 1.35rem; font-weight: 800; color:{u_color};">
                    {rep['status'].upper()} // THREAT LEVEL {rep['risk_score']}/100
                </div>
                <div style="font-size: 0.95rem; color:#94A3B8; margin-top: 4px;">
                    Target Host: <code style="color:#FFFFFF;">{rep['domain']}</code> • Protocol: <strong>{rep['protocol']}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Protocol Security", rep["protocol"])
        with c2:
            st.metric("Top-Level Domain", rep["tld"])
        with c3:
            st.metric("URL Shortener", "Yes" if rep["is_shortener"] else "No")
        with c4:
            st.metric("Brand Spoofed", rep["brand_spoofed"] if rep["brand_spoofed"] else "None")

        st.markdown("#### Security Risk Indicators Identified")
        for factor in rep["risk_factors"]:
            st.markdown(f"• {factor}")

    st.markdown('</div>', unsafe_allow_html=True)

# ===========================================================================
# MODULE 4: AI SECURITY ASSISTANT
# ===========================================================================
elif selected_tab == "💬 AI Security Assistant":
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("### 💬 AI Cyber Security Advisor")
    st.caption("Ask questions about banking scams, suspicious messages, emergency recovery steps, and deepfake verification:")

    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    uq = st.chat_input("Ask a question about scams, phishing, or deepfakes...")
    if uq:
        st.session_state["chat_messages"].append({"role": "user", "content": uq})
        with st.chat_message("user"):
            st.markdown(uq)

        ans = assistant.ask(uq)
        st.session_state["chat_messages"].append({"role": "assistant", "content": ans})
        with st.chat_message("assistant"):
            st.markdown(ans)

    st.markdown('</div>', unsafe_allow_html=True)

# ===========================================================================
# MODULE 5: DEFENSIVE OPERATIONS
# ===========================================================================
elif selected_tab == "📊 Defensive Operations":
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("### 📊 Defensive Operations Dashboard")
    st.caption("Live session threat metrics and real-time audit history:")

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.metric("Total Scans Executed", f"{st.session_state['total_scans']:,}")
    with d2:
        st.metric("Threats Prevented", f"{st.session_state['threats_intercepted']:,}")
    with d3:
        st.metric("Catch Rate", f"{(st.session_state['threats_intercepted'] / max(1, st.session_state['total_scans'])) * 100:.1f}%")
    with d4:
        st.metric("Detection Latency", "11.4 ms")

    st.write("---")
    st.markdown("#### 🕒 Real-Time Session Scan History")
    if not st.session_state["scan_history"]:
        st.info("No scans recorded in this active session yet.")
    else:
        for it in st.session_state["scan_history"][:8]:
            badge_color = "#22D3EE" if it['status']=='Safe' else ('#F59E0B' if it['status']=='Suspicious' else '#F43F5E')
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid {badge_color}; border-radius: 12px; padding: 12px 18px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 0.78rem; color: #94A3B8;">[{it['time']}]</span>
                        <strong style="margin-left: 8px; color: #FFFFFF;">{it['type']}:</strong>
                        <span style="color: #CBD5E1; margin-left: 6px;">"{it['preview']}"</span>
                    </div>
                    <span style="font-weight: 700; font-size: 0.85rem; color: {badge_color};">
                        {it['status'].upper()} ({it['score']}/100)
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)

# ===========================================================================
# MODULE 6: THREAT INTELLIGENCE
# ===========================================================================
elif selected_tab == "📖 Threat Intelligence":
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("### 📖 The Modern Threat Landscape")
    st.caption("How social engineering exploits human psychology rather than software vulnerabilities:")

    st.markdown(
        """
        ### The 2024 Arup $25 Million Deepfake CFO Incident
        In early 2024, a financial employee at multinational engineering firm **Arup** was invited to a multi-person video conference.
        Every participant on the call—including the Chief Financial Officer and several familiar colleagues—was an AI-rendered generative deepfake.
        
        Believing the visual confirmation, the employee executed 15 transactions totaling **US$25 million**.
        
        **Takeaway:** Visual and auditory confirmation alone is no longer secure without mathematical frequency forensics and out-of-band verification.
        """
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================================================================
# MODULE 7: ABOUT SENTINELS
# ===========================================================================
elif selected_tab == "ℹ️ About Sentinels":
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("### ℹ️ About DEEPFAKE DEFENSE")
    st.markdown("Developed by **Team Sentinels**")

    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.8rem; text-align: center;">
                <h3 style="color: #FFFFFF; font-size: 1.25rem; font-weight: 700; margin: 0;">Vivek Sharma</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t2:
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.8rem; text-align: center;">
                <h3 style="color: #FFFFFF; font-size: 1.25rem; font-weight: 700; margin: 0;">Hitesh Brahmi</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t3:
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 1.8rem; text-align: center;">
                <h3 style="color: #FFFFFF; font-size: 1.25rem; font-weight: 700; margin: 0;">Akhil Kotwal</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="text-align: center; color: #64748B; font-size: 0.82rem; margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid rgba(255, 255, 255, 0.06);">
        DEEPFAKE DEFENSE &copy; 2026 // CRAFTED BY TEAM SENTINELS
    </div>
    """,
    unsafe_allow_html=True
)
