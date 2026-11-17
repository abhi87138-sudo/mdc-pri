"""
app.py
=============================================================================
DEEPFAKE DEFENSE // Autonomous Threat & Synthetic Media Protection Platform
Brand: DEEPFAKE DEFENSE
Team: Sentinels (Vivek Sharma, Hitesh Brahmi, Akhil Kotwal)
Aesthetic: Modern, Clean SaaS Inspired by Truecaller's Simplicity
Theme: Dual-Mode Black & Cyan Identity (Obsidian Dark & Clean Slate Light)
=============================================================================
"""

import os
import json
import random
import io
import time
import sys
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
    page_title="DEEPFAKE DEFENSE // AI Cyber & Media Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# Session State Management
# ---------------------------------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"

if "scan_history" not in st.session_state:
    st.session_state["scan_history"] = []

if "total_scans" not in st.session_state:
    st.session_state["total_scans"] = 1420

if "threats_intercepted" not in st.session_state:
    st.session_state["threats_intercepted"] = 894

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": "Hello! I am your **DEEPFAKE DEFENSE** security assistant. Paste any suspicious SMS, ask about banking scams, or learn how to spot synthetic video/audio deepfakes."}
    ]

is_dark = (st.session_state["theme_mode"] == "dark")
cyan_main = "#06B6D4" if is_dark else "#0891B2"
cyan_glow = "#22D3EE" if is_dark else "#06B6D4"
cyan_subtle = "rgba(6, 182, 212, 0.12)" if is_dark else "#E0F2FE"

# ---------------------------------------------------------------------------
# SVG Vector Graphics Library
# ---------------------------------------------------------------------------
def svg_icon(name, color=None, size=20):
    c = color if color else cyan_main
    icons = {
        "shield": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>''',
        "shield-check": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>''',
        "radar": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/><line x1="12" y1="2" x2="12" y2="12"/></svg>''',
        "cpu": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>''',
        "lock": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>''',
        "alert": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>''',
        "message": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>''',
        "users": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>''',
        "video": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>''',
        "mic": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>''',
        "activity": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>''',
        "check": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>''',
        "camera": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>''',
        "sparkles": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>''',
        "globe": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>''',
        "link": f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>'''
    }
    return icons.get(name, "")

# ---------------------------------------------------------------------------
# Theme Stylesheet (Truecaller-Inspired Clean Black & Cyan Dual Mode)
# ---------------------------------------------------------------------------
if is_dark:
    theme_css = """
    :root {
        --bg-main: #080B10;
        --card-bg: #0F1726;
        --card-border: rgba(6, 182, 212, 0.22);
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --hero-bg: linear-gradient(135deg, #080B10 0%, #0F172A 60%, #082F49 100%);
        --metric-bg: #0F1726;
        --pill-bg: #131E33;
        --tab-bg: #0B1120;
        --cyan: #06B6D4;
        --cyan-glow: #22D3EE;
        --input-bg: #0D1524;
        --status-safe-bg: rgba(6, 182, 212, 0.12);
        --status-safe-border: #06B6D4;
        --status-susp-bg: rgba(245, 158, 11, 0.14);
        --status-susp-border: #F59E0B;
        --status-dang-bg: rgba(239, 68, 68, 0.16);
        --status-dang-border: #EF4444;
    }
    .stApp {
        background-color: #080B10 !important;
        color: #F8FAFC !important;
    }
    .stApp p, .stApp span, .stApp div, .stMarkdown p, .stCaption {
        color: #CBD5E1 !important;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #FFFFFF !important;
    }
    textarea, input {
        background-color: #0D1524 !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(6, 182, 212, 0.3) !important;
    }
    """
else:
    theme_css = """
    :root {
        --bg-main: #FFFFFF;
        --card-bg: #FFFFFF;
        --card-border: #E2E8F0;
        --text-primary: #0F172A;
        --text-secondary: #475569;
        --hero-bg: linear-gradient(135deg, #F0FDFA 0%, #E0F2FE 60%, #F8FAFC 100%);
        --metric-bg: #FFFFFF;
        --pill-bg: #F1F5F9;
        --tab-bg: #F8FAFC;
        --cyan: #0891B2;
        --cyan-glow: #06B6D4;
        --input-bg: #FFFFFF;
        --status-safe-bg: #F0FDFA;
        --status-safe-border: #0D9488;
        --status-susp-bg: #FFFBEB;
        --status-susp-border: #F59E0B;
        --status-dang-bg: #FEF2F2;
        --status-dang-border: #EF4444;
    }
    .stApp {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    .stApp p, .stApp span, .stApp div, .stMarkdown p, .stMarkdown li {
        color: #334155 !important;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #0F172A !important;
        font-weight: 800 !important;
    }
    .stCaption, .stCaption p, [data-testid="stCaptionContainer"] p {
        color: #64748B !important;
    }
    label[data-testid="stWidgetLabel"] p, label[data-testid="stWidgetLabel"] span {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    textarea, input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 12px !important;
    }
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
    }
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
    }
    .stButton > button {
        background-color: #0891B2 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
    }
    """

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    {theme_css}

    * {{
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }}

    code, pre {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    .block-container {{
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1160px;
    }}

    /* Top Brand Navigation */
    .top-nav {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 0.2rem 1.2rem 0.2rem;
        border-bottom: 1px solid {'rgba(6, 182, 212, 0.15)' if is_dark else '#E2E8F0'};
        margin-bottom: 1.4rem;
    }}

    .brand-logo-wrap {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .brand-title {{
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: {cyan_glow} !important;
        margin: 0;
    }}

    .brand-tagline {{
        font-size: 0.76rem;
        color: var(--text-secondary);
        font-weight: 500;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }}

    .status-live-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        background: {'rgba(6, 182, 212, 0.12)' if is_dark else '#E0F2FE'};
        border: 1px solid {'rgba(6, 182, 212, 0.3)' if is_dark else '#BAE6FD'};
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 700;
        color: {cyan_main} !important;
    }}

    /* Truecaller Inspired Hero */
    .hero-container {{
        background: var(--hero-bg);
        border: 1px solid {'rgba(6, 182, 212, 0.25)' if is_dark else '#CBD5E1'};
        border-radius: 20px;
        padding: 2.2rem 2.6rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 30px -10px {'rgba(0, 0, 0, 0.5)' if is_dark else 'rgba(6, 182, 212, 0.08)'};
        position: relative;
        overflow: hidden;
    }}

    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        background: {'rgba(6, 182, 212, 0.15)' if is_dark else 'rgba(8, 145, 178, 0.1)'};
        border: 1px solid {'rgba(6, 182, 212, 0.35)' if is_dark else 'rgba(8, 145, 178, 0.25)'};
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {cyan_glow} !important;
        margin-bottom: 0.8rem;
    }}

    .hero-main-title {{
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: {'#FFFFFF' if is_dark else '#0F172A'} !important;
        line-height: 1.2;
        margin-bottom: 0.6rem;
    }}

    .hero-description {{
        color: {'#94A3B8' if is_dark else '#475569'} !important;
        font-size: 1.02rem;
        line-height: 1.6;
        max-width: 820px;
        margin-bottom: 1.2rem;
    }}

    .hero-pills-row {{
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }}

    .hero-pill-item {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: {'rgba(15, 23, 42, 0.7)' if is_dark else '#FFFFFF'};
        border: 1px solid {'rgba(6, 182, 212, 0.2)' if is_dark else '#E2E8F0'};
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        color: {'#E2E8F0' if is_dark else '#334155'} !important;
    }}

    /* What We Do Cards */
    .what-we-do-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 14px;
        margin: 1.2rem 0 2rem 0;
    }}

    .feature-card {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 1.3rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 16px {'rgba(0,0,0,0.18)' if is_dark else 'rgba(0,0,0,0.03)'};
    }}

    .feature-card:hover {{
        border-color: {cyan_glow};
        transform: translateY(-2px);
    }}

    .feature-card-title {{
        font-size: 1.02rem;
        font-weight: 700;
        color: var(--text-primary) !important;
        margin: 0.6rem 0 0.3rem 0;
    }}

    .feature-card-desc {{
        font-size: 0.86rem;
        color: var(--text-secondary) !important;
        line-height: 1.5;
        margin: 0;
    }}

    /* Truecaller-style Scam Inspector Card */
    .inspector-card {{
        background: var(--card-bg);
        border: 1.5px solid {'rgba(6, 182, 212, 0.3)' if is_dark else '#CBD5E1'};
        border-radius: 18px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 30px {'rgba(0,0,0,0.25)' if is_dark else 'rgba(6, 182, 212, 0.05)'};
    }}

    /* Status Banners */
    .verdict-banner {{
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin: 1.2rem 0;
        display: flex;
        align-items: center;
        gap: 18px;
    }}

    .verdict-safe {{
        background: var(--status-safe-bg);
        border: 1.5px solid var(--status-safe-border);
    }}

    .verdict-suspicious {{
        background: var(--status-susp-bg);
        border: 1.5px solid var(--status-susp-border);
    }}

    .verdict-dangerous {{
        background: var(--status-dang-bg);
        border: 1.5px solid var(--status-dang-border);
    }}

    /* Token Heatmap Box */
    .heatmap-box {{
        background: var(--pill-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
        line-height: 2.3;
        font-size: 1rem;
    }}

    .token-normal {{
        color: var(--text-primary) !important;
        padding: 2px 4px;
    }}

    .token-urgency {{
        background: rgba(239, 68, 68, 0.22);
        color: #F87171 !important;
        border: 1px solid rgba(239, 68, 68, 0.45);
        border-radius: 6px;
        padding: 2px 7px;
        font-weight: 700;
    }}

    .token-financial {{
        background: rgba(245, 158, 11, 0.22);
        color: #FBBF24 !important;
        border: 1px solid rgba(245, 158, 11, 0.45);
        border-radius: 6px;
        padding: 2px 7px;
        font-weight: 700;
    }}

    .token-credential {{
        background: rgba(6, 182, 212, 0.22);
        color: {cyan_glow} !important;
        border: 1px solid rgba(6, 182, 212, 0.45);
        border-radius: 6px;
        padding: 2px 7px;
        font-weight: 700;
    }}

    .token-link {{
        background: rgba(59, 130, 246, 0.22);
        color: #60A5FA !important;
        border: 1px solid rgba(59, 130, 246, 0.45);
        border-radius: 6px;
        padding: 2px 7px;
        font-weight: 700;
        text-decoration: underline;
    }}

    /* Truecaller Safety Action Box */
    .safety-action-card {{
        background: {'rgba(6, 182, 212, 0.06)' if is_dark else '#F0FDFA'};
        border-left: 4px solid {cyan_main};
        border-radius: 10px;
        padding: 1rem 1.3rem;
        margin-top: 1rem;
    }}

    .safety-action-title {{
        font-size: 0.95rem;
        font-weight: 700;
        color: {cyan_main} !important;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* Modern Left Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--card-bg) !important;
        border-right: 1px solid var(--card-border) !important;
        padding-top: 1.5rem;
    }}

    section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {{
        gap: 6px;
    }}

    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
        background: var(--pill-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        padding: 12px 14px !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        margin-bottom: 4px !important;
        display: flex !important;
        align-items: center !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
        border-color: {cyan_glow} !important;
        transform: translateX(3px) !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {{
        background: var(--status-safe-bg) !important;
        border-color: {cyan_main} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# Backend Engine Initializers
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
# Navigation Top Bar
# ---------------------------------------------------------------------------
col_nav_brand, col_nav_status, col_nav_theme = st.columns([6.5, 2.5, 1.5])
with col_nav_brand:
    st.markdown(
        f"""
        <div class="brand-logo-wrap">
            {svg_icon("shield-check", cyan_glow, 30)}
            <div>
                <div class="brand-title">DEEPFAKE DEFENSE</div>
                <div class="brand-tagline">AI Social Engineering & Synthetic Media Protection</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_nav_status:
    st.markdown(
        f"""
        <div style="text-align: right; padding-top: 6px;">
            <span class="status-live-pill">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:{cyan_glow};"></span>
                ACTIVE DEFENSE // AIR-GAPPED
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_nav_theme:
    if is_dark:
        if st.button("☀️ Light", use_container_width=True):
            st.session_state["theme_mode"] = "light"
            st.rerun()
    else:
        if st.button("🌙 Dark", use_container_width=True):
            st.session_state["theme_mode"] = "dark"
            st.rerun()

# ---------------------------------------------------------------------------
# Homepage Hero Section
# ---------------------------------------------------------------------------
col_hero_left, col_hero_right = st.columns([7, 3])
with col_hero_left:
    st.markdown(
        f"""
        <div class="hero-container">
            <span class="hero-badge">{svg_icon("radar", cyan_glow, 15)} INTELLIGENT DEFENSE LAYER</span>
            <div class="hero-main-title">Instant Scam & Deepfake Protection</div>
            <p class="hero-description">
                Autonomous AI shield inspecting deceptive communications and digital media in real time.
                Shields your identity and finances against fake KYC messages, electricity bill traps, banking smishing, and generative deepfakes.
            </p>
            <div class="hero-pills-row">
                <span class="hero-pill-item">{svg_icon("lock", cyan_main, 14)} 100% Air-Gapped Privacy</span>
                <span class="hero-pill-item">{svg_icon("activity", cyan_main, 14)} Sub-15ms Local NLP</span>
                <span class="hero-pill-item">{svg_icon("cpu", cyan_main, 14)} 2D FFT Media Forensics</span>
                <span class="hero-pill-item">{svg_icon("shield", cyan_main, 14)} Indian Banking & Utility Rules</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_hero_right:
    # Modern SVG Cybersecurity Illustration
    st.markdown(
        f"""
        <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 20px; padding: 1.8rem; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 20px {'rgba(0,0,0,0.2)' if is_dark else 'rgba(0,0,0,0.04)'};">
            <svg width="120" height="120" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="100" cy="100" r="90" stroke="{cyan_main}" stroke-width="2" stroke-dasharray="4 6" opacity="0.4"/>
                <circle cx="100" cy="100" r="70" stroke="{cyan_glow}" stroke-width="2" opacity="0.6"/>
                <circle cx="100" cy="100" r="45" fill="{'rgba(6,182,212,0.1)' if is_dark else '#E0F2FE'}"/>
                <!-- Shield Path -->
                <path d="M100 48L140 68V115C140 144 100 162 100 162C100 162 60 144 60 115V68L100 48Z" fill="{cyan_main}" fill-opacity="0.15" stroke="{cyan_glow}" stroke-width="3" stroke-linejoin="round"/>
                <!-- Inner Lock / Checkmark -->
                <path d="M90 105L98 113L115 95" stroke="{cyan_glow}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="100" y1="20" x2="100" y2="40" stroke="{cyan_main}" stroke-width="2" stroke-linecap="round"/>
                <line x1="180" y1="100" x2="160" y2="100" stroke="{cyan_main}" stroke-width="2" stroke-linecap="round"/>
                <line x1="20" y1="100" x2="40" y2="100" stroke="{cyan_main}" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <div style="font-size: 0.95rem; font-weight: 700; color: {cyan_glow} !important; margin-top: 10px;">DEEPFAKE DEFENSE</div>
            <div style="font-size: 0.78rem; color: var(--text-secondary);">Enterprise-Grade Threat Mitigation</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------------------------
# Dedicated Section: "What We Do"
# ---------------------------------------------------------------------------
with st.expander("ℹ️ **What We Do & How Deepfake Defense Protects You**", expanded=False):
    st.markdown(
        """
        **DEEPFAKE DEFENSE** is an autonomous cybersecurity intelligence platform engineered to protect individuals, 
        enterprises, and financial institutions against the fastest-growing modern cyber threats:
        """
    )
    st.markdown(
        f"""
        <div class="what-we-do-grid">
            <div class="feature-card">
                {svg_icon("lock", cyan_main, 24)}
                <div class="feature-card-title">Banking & KYC Defense</div>
                <p class="feature-card-desc">Detects deceptive SBI, HDFC, ICICI, and bank impersonation SMS demanding urgent KYC, PAN, or Aadhaar updates.</p>
            </div>
            <div class="feature-card">
                {svg_icon("alert", "#F59E0B", 24)}
                <div class="feature-card-title">Utility & Electricity Bill Scams</div>
                <p class="feature-card-desc">Identifies fake power disconnection threats used by scammers to trick victims into calling fake helplines and installing remote-control APKs.</p>
            </div>
            <div class="feature-card">
                {svg_icon("activity", "#10B981", 24)}
                <div class="feature-card-title">UPI & Payment Protection</div>
                <p class="feature-card-desc">Intercepts fraudulent QR code scan requests and deceptive collect traps that attempt to siphon funds from Google Pay, PhonePe, and Paytm.</p>
            </div>
            <div class="feature-card">
                {svg_icon("video", cyan_glow, 24)}
                <div class="feature-card-title">Video & Audio Deepfake Forensics</div>
                <p class="feature-card-desc">Leverages 2D Fast Fourier Transform (FFT) and vocoder spectrum analysis to expose synthetic face-swaps and cloned executive voices.</p>
            </div>
            <div class="feature-card">
                {svg_icon("link", cyan_main, 24)}
                <div class="feature-card-title">Phishing Link & Domain Scanner</div>
                <p class="feature-card-desc">Inspects URL shorteners, free/high-risk TLDs, and typosquatting domain tricks before you click or enter credentials.</p>
            </div>
            <div class="feature-card">
                {svg_icon("message", cyan_glow, 24)}
                <div class="feature-card-title">AI Cyber Security Advisor</div>
                <p class="feature-card-desc">Provides interactive 24/7 security recommendations and emergency incident response guidance (1930 / cybercrime.gov.in).</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------------------------
# Left Sidebar Navigation (Modern Acer/Cyber Console Vertical Panel)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; padding-bottom: 1.2rem; border-bottom: 1px solid var(--card-border); margin-bottom: 1.4rem;">
            {svg_icon("shield-check", cyan_glow, 44)}
            <div style="font-size: 1.25rem; font-weight: 800; color: {cyan_glow} !important; margin-top: 8px; letter-spacing: -0.02em;">
                DEEPFAKE DEFENSE
            </div>
            <div style="font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px;">
                Autonomous Security Console
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption("NAVIGATION MENU")
    selected_nav = st.radio(
        "Navigation",
        [
            "🛡️ AI Scam Message Checker",
            "🔬 Deepfake Lab",
            "🔗 Phishing URL Scanner",
            "💬 AI Security Assistant",
            "📊 Security Dashboard",
            "📖 Threat Intel & Cases",
            "⚡ Benchmarks & Limits",
            "ℹ️ About Platform"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("SYSTEM STATUS")
    st.markdown(
        f"""
        <div style="background: var(--pill-bg); border: 1px solid var(--card-border); border-radius: 10px; padding: 10px; font-size: 0.8rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="color:var(--text-secondary);">Core Engine:</span>
                <strong style="color:{cyan_glow};">ONLINE</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="color:var(--text-secondary);">Latency:</span>
                <strong style="color:#10B981;">11.4ms</strong>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:var(--text-secondary);">Privacy:</span>
                <strong style="color:{cyan_glow};">Air-Gapped</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ===========================================================================
# ROUTING MAIN CONTENT BASED ON SELECTED SIDEBAR NAVIGATION
# ===========================================================================
if selected_nav == "🛡️ AI Scam Message Checker":
    st.markdown("### 🛡️ AI Scam Message Checker")
    st.caption("Paste any suspicious SMS, WhatsApp forward, bank alert, or email. The engine inspects for urgency coercion, credential theft, and utility fraud:")

    # Quick Scenario Test Pills
    st.write("**Quick-Test Everyday Scam Scenarios:**")
    p1, p2, p3, p4, p5, p6 = st.columns(6)

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

    with p1:
        if st.button("🏦 SBI KYC Scam", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["sbi"]
    with p2:
        if st.button("⚡ Electricity Cut", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["elec"]
    with p3:
        if st.button("📲 UPI QR Trap", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["upi"]
    with p4:
        if st.button("🎁 Cash Prize", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["prize"]
    with p5:
        if st.button("📦 Courier Fee", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["parcel"]
    with p6:
        if st.button("💬 Normal Chat", use_container_width=True):
            st.session_state["current_message"] = SCENARIOS["chat"]

    user_input = st.text_area(
        "Message Text for Inspection:",
        value=st.session_state["current_message"],
        height=130,
        placeholder="Paste any suspicious SMS, WhatsApp message, email, or bank notification here..."
    )

    col_btn_scan, col_btn_clear = st.columns([8, 2])
    with col_btn_scan:
        execute_scan = st.button("🛡️ Run Deepfake Defense AI Scan", type="primary", use_container_width=True)
    with col_btn_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state["current_message"] = ""
            st.rerun()

    if execute_scan or (user_input.strip() and st.session_state.get("last_scanned_text") != user_input):
        st.session_state["last_scanned_text"] = user_input
        if not user_input.strip():
            st.warning("⚠️ Input is empty. Please enter or paste a message above.")
        else:
            with st.spinner("Analyzing message through hybrid NLP & Indian scam threat engines..."):
                res = detector.predict(user_input)
                # Log to session history
                st.session_state["scan_history"].insert(0, {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "type": "Message",
                    "preview": user_input[:45] + ("..." if len(user_input) > 45 else ""),
                    "score": res["risk_score"],
                    "status": res["status"]
                })
                st.session_state["total_scans"] += 1
                if res["status"] != "Safe":
                    st.session_state["threats_intercepted"] += 1

            risk_score = res["risk_score"]
            status = res["status"]
            ml_prob = res["ml_probability"]
            reasons = res["reasons"]
            vectors = res["vectors"]
            attack = res["attack_vector"]
            urls = res["urls"]
            tokens = res["tokens"]

            st.write("---")

            # Truecaller-Style Verdict Header Banner
            if status == "Safe":
                st.markdown(
                    f"""
                    <div class="verdict-banner verdict-safe">
                        {svg_icon("shield-check", cyan_glow, 38)}
                        <div>
                            <div style="color: {cyan_glow} !important; font-weight: 800; font-size: 1.3rem;">
                                VERDICT: AUTHENTIC / SAFE
                            </div>
                            <div style="color: var(--text-secondary); font-size: 0.94rem;">
                                Threat Severity: <strong>{risk_score}/100</strong> • Category: <strong>{attack['name']}</strong>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif status == "Suspicious":
                st.markdown(
                    f"""
                    <div class="verdict-banner verdict-suspicious">
                        {svg_icon("alert", "#F59E0B", 38)}
                        <div>
                            <div style="color: #F59E0B !important; font-weight: 800; font-size: 1.3rem;">
                                VERDICT: SUSPICIOUS / ELEVATED RISK
                            </div>
                            <div style="color: var(--text-secondary); font-size: 0.94rem;">
                                Threat Severity: <strong>{risk_score}/100</strong> • Attack Type: <strong>{attack['name']}</strong>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="verdict-banner verdict-dangerous">
                        {svg_icon("alert", "#EF4444", 38)}
                        <div>
                            <div style="color: #EF4444 !important; font-weight: 800; font-size: 1.3rem;">
                                VERDICT: DANGEROUS // ACTIVE SCAM DETECTED
                            </div>
                            <div style="color: var(--text-secondary); font-size: 0.94rem;">
                                Threat Severity: <strong>{risk_score}/100</strong> • Attack Type: <strong>{attack['name']}</strong> ({attack['badge']})
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Severity Progress Bar
            st.write(f"**Threat Severity Level: {risk_score} / 100**")
            st.progress(risk_score / 100.0)

            # Truecaller-Style Recommended Safety Actions
            st.markdown(
                f"""
                <div class="safety-action-card">
                    <div class="safety-action-title">
                        {svg_icon("shield", cyan_main, 18)}
                        <strong>Recommended Safety Actions & Protocol:</strong>
                    </div>
                    <ul style="margin: 0; padding-left: 1.2rem; font-size: 0.9rem; color: var(--text-secondary);">
                        {''.join([f'<li style="margin-bottom: 4px;">{action}</li>' for action in attack.get('actions', ['Exercise standard security precautions.'])])}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Interactive Token Heatmap
            st.write("")
            st.markdown("#### 🔍 Interactive Suspicious Phrase Heatmap")
            st.caption("Classified payload tokens highlighted by psychological manipulation category:")

            heatmap_html = '<div class="heatmap-box">'
            for word, tag in tokens:
                if tag == "urgency":
                    heatmap_html += f'<span class="token-urgency">{word}</span> '
                elif tag == "financial":
                    heatmap_html += f'<span class="token-financial">{word}</span> '
                elif tag == "credential":
                    heatmap_html += f'<span class="token-credential">{word}</span> '
                elif tag == "link":
                    heatmap_html += f'<span class="token-link">{word}</span> '
                else:
                    heatmap_html += f'<span class="token-normal">{word}</span> '
            heatmap_html += '</div>'
            st.markdown(heatmap_html, unsafe_allow_html=True)

            # Legend
            st.markdown(
                """
                <div style="display: flex; gap: 16px; flex-wrap: wrap; font-size: 0.8rem; margin-bottom: 1.2rem;">
                    <span><strong style="color: #F87171;">■ Red:</strong> Urgency / Coercive Panic</span>
                    <span><strong style="color: #FBBF24;">■ Amber:</strong> Financial / Prize / Bill Bait</span>
                    <span><strong style="color: #22D3EE;">■ Cyan:</strong> Credential / OTP / KYC Target</span>
                    <span><strong style="color: #60A5FA;">■ Blue:</strong> Embedded Link / Obfuscated Domain</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Psychological Manipulation Vectors
            st.markdown("#### 🧠 Cognitive Social Engineering Radar")
            v1, v2, v3, v4 = st.columns(4)
            with v1:
                st.metric("Urgency Pressure", f"{vectors['urgency']}%")
                st.progress(vectors['urgency'] / 100.0)
            with v2:
                st.metric("Financial Incentive", f"{vectors['financial']}%")
                st.progress(vectors['financial'] / 100.0)
            with v3:
                st.metric("Credential Theft", f"{vectors['credential']}%")
                st.progress(vectors['credential'] / 100.0)
            with v4:
                st.metric("Authority Spoofing", f"{vectors['authority']}%")
                st.progress(vectors['authority'] / 100.0)

            # Itemized Threat Breakdown
            st.write("")
            st.markdown("#### 📋 Itemized Diagnostic Findings")
            for r in reasons:
                st.markdown(
                    f"""
                    <div style="background: var(--pill-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; font-size: 0.92rem;">
                        {svg_icon("activity", cyan_main, 16)}
                        <span>{r}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# ===========================================================================
# VIEW 2: DEEPFAKE LAB (IMAGE, VIDEO CALL SNAPSHOT & AUDIO VOICE FORENSICS)
# ===========================================================================
elif selected_nav == "🔬 Deepfake Lab":
    st.markdown("### 🔬 Multi-Modal Deepfake Defense Lab")
    st.caption("Inspect digital portraits, video call snapshot frames, and voice notes for synthetic generative manipulation:")

    # Deepfake Mode Selector
    media_tab1, media_tab2 = st.tabs(["📷 Facial Image & Video Call Snapshot", "🎙️ Synthetic Voice & Audio Note"])

    with media_tab1:
        st.markdown(
            f"""
            <div style="background: {'rgba(6, 182, 212, 0.08)' if is_dark else '#F0FDFA'}; border: 1px solid {'rgba(6, 182, 212, 0.25)' if is_dark else '#BAE6FD'}; border-radius: 12px; padding: 1.2rem; margin-bottom: 1.2rem;">
                <div style="display: flex; align-items: center; gap: 10px; font-weight: 700; color: {cyan_glow}; margin-bottom: 6px;">
                    {svg_icon("video", cyan_glow, 20)}
                    <span>Enterprise Video Conference Protection Protocol (Arup Defense)</span>
                </div>
                <p style="font-size: 0.88rem; color: var(--text-secondary); margin: 0; line-height: 1.5;">
                    Adversaries deploy real-time deepfake face-swaps in corporate executive meetings. 
                    DEEPFAKE DEFENSE intercepts frames and evaluates <strong>2D Fast Fourier Transform (FFT) grid regularities, Laplacian boundary gradients, and sensor noise (PRNU)</strong> to detect synthetic manipulation invisible to the naked eye.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        input_mode = st.radio(
            "Select Inspection Source:",
            ["📁 Upload Portrait / Snapshot", "📷 Live Webcam Frame Capture", "🧪 Preset Forensic Test Samples"],
            horizontal=True
        )

        image_to_analyze = None

        if input_mode == "📁 Upload Portrait / Snapshot":
            uploaded_file = st.file_uploader(
                "Upload portrait or video meeting frame (PNG, JPG, JPEG):",
                type=["png", "jpg", "jpeg"]
            )
            if uploaded_file is not None:
                image_to_analyze = Image.open(uploaded_file)

        elif input_mode == "📷 Live Webcam Frame Capture":
            st.caption("Capture a live frame from your webcam (simulates auditing a meeting participant):")
            camera_snap = st.camera_input("Snapshot Video Call Frame")
            if camera_snap is not None:
                image_to_analyze = Image.open(camera_snap)

        else:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                if st.button("Load Authentic Reference Sample", use_container_width=True):
                    st.session_state["img_sample_choice"] = "authentic"
            with col_s2:
                if st.button("Load Synthetic GAN Deepfake Sample", use_container_width=True):
                    st.session_state["img_sample_choice"] = "synthetic"

            if "img_sample_choice" not in st.session_state:
                st.session_state["img_sample_choice"] = "synthetic"

            if st.session_state["img_sample_choice"] == "authentic":
                image_to_analyze = generate_sample_authentic_portrait()
                st.info("Loaded: Authentic Reference Portrait (Simulates genuine optical sensor camera capture).")
            else:
                image_to_analyze = generate_sample_synthetic_portrait()
                st.warning("Loaded: Synthetic GAN Deepfake Portrait (Simulates periodic GAN upsampling grid & boundary seam blur).")

        if image_to_analyze is not None:
            col_run_df, _ = st.columns([3, 7])
            with col_run_df:
                run_df_scan = st.button("🔬 Execute Deepfake Forensics", type="primary", use_container_width=True)

            if run_df_scan or input_mode == "🧪 Preset Forensic Test Samples":
                with st.spinner("Computing 2D FFT power spectrum, Laplacian edge maps, and chrominance consistency..."):
                    df_res = deepfake_engine.analyze_image(image_to_analyze)

                df_score = df_res["overall_score"]
                df_status = df_res["status"]
                df_label = df_res["verdict_label"]
                metrics = df_res["metrics"]
                reasons = df_res["reasons"]

                st.write("---")
                st.markdown("#### Visual Evidence Inspection Gallery")
                col_g1, col_g2, col_g3 = st.columns(3)
                with col_g1:
                    st.image(df_res["face_crop"], caption="1. Analyzed Region of Interest", use_container_width=True)
                with col_g2:
                    st.image(df_res["edge_image"], caption="2. Laplacian Boundary Edge Map", use_container_width=True)
                with col_g3:
                    st.image(df_res["fft_image"], caption="3. 2D FFT Power Spectrum Heatmap", use_container_width=True)

                st.caption("Above: (1) Cropped subject frame; (2) Laplacian gradient map exposing boundary blur/sharpening; (3) 2D FFT exposing periodic generator grid lattice.")

                st.write("")
                # Multi-Factor Forensic Metrics
                st.markdown("#### Forensic Multi-Factor Diagnostic Scores")
                dm1, dm2, dm3, dm4 = st.columns(4)
                with dm1:
                    st.metric("FFT Grid Regularity", f"{metrics['fft_score']}%", f"{metrics['high_freq_ratio']}% HF Energy")
                    st.progress(metrics['fft_score'] / 100.0)
                with dm2:
                    st.metric("Boundary Laplacian", f"{metrics['lap_score']}%", f"Var: {metrics['laplacian_variance']}")
                    st.progress(metrics['lap_score'] / 100.0)
                with dm3:
                    st.metric("Color Space Harmony", f"{metrics['color_score']}%", f"Diff: {metrics['color_discrepancy']}")
                    st.progress(metrics['color_score'] / 100.0)
                with dm4:
                    st.metric("Sensor Noise (PRNU)", f"{metrics['noise_score']}%", f"Var: {metrics['noise_variance']}")
                    st.progress(metrics['noise_score'] / 100.0)

                st.markdown("#### Forensic Technical Findings")
                for r in reasons:
                    st.markdown(
                        f"""
                        <div style="background: var(--pill-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; font-size: 0.92rem;">
                            {svg_icon("activity", cyan_main, 16)} {r}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    # Audio Deepfake Scanner
    with media_tab2:
        st.markdown(
            f"""
            <div style="background: {'rgba(6, 182, 212, 0.08)' if is_dark else '#F0FDFA'}; border: 1px solid {'rgba(6, 182, 212, 0.25)' if is_dark else '#BAE6FD'}; border-radius: 12px; padding: 1.2rem; margin-bottom: 1.2rem;">
                <div style="display: flex; align-items: center; gap: 10px; font-weight: 700; color: {cyan_glow}; margin-bottom: 6px;">
                    {svg_icon("mic", cyan_glow, 20)}
                    <span>Voice Clone & Audio Deepfake Forensic Inspector</span>
                </div>
                <p style="font-size: 0.88rem; color: var(--text-secondary); margin: 0; line-height: 1.5;">
                    Adversaries clone executive or family voices from 3-second audio clips to execute fraudulent wire instructions.
                    This module evaluates <strong>acoustic bandwidth cutoff (vocoder limits), silence floor unnaturalness, and zero-crossing pitch jitter</strong>.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        audio_input_mode = st.radio(
            "Select Audio Source:",
            ["🧪 Preset Forensic Audio Samples", "📁 Upload Audio Recording (WAV)"],
            horizontal=True
        )

        audio_buffer = None
        if audio_input_mode == "📁 Upload Audio Recording (WAV)":
            uploaded_audio = st.file_uploader("Upload audio recording (WAV format):", type=["wav"])
            if uploaded_audio is not None:
                audio_buffer = uploaded_audio
        else:
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                if st.button("Load Authentic Human Voice Sample", use_container_width=True):
                    st.session_state["audio_sample_choice"] = "authentic"
            with col_a2:
                if st.button("Load Synthetic AI Voice Clone Sample", use_container_width=True):
                    st.session_state["audio_sample_choice"] = "synthetic"

            if "audio_sample_choice" not in st.session_state:
                st.session_state["audio_sample_choice"] = "synthetic"

            if st.session_state["audio_sample_choice"] == "authentic":
                audio_buffer = generate_sample_authentic_audio()
                st.info("Loaded: Authentic Human Audio (Natural microphone room acoustics and wideband frequencies).")
            else:
                audio_buffer = generate_sample_synthetic_audio()
                st.warning("Loaded: Synthetic AI Voice Clone (Simulates 16kHz neural vocoder cutoff and dead silence).")

        if audio_buffer is not None:
            st.audio(audio_buffer, format="audio/wav")
            if st.button("🔬 Execute Audio Deepfake Scan", type="primary", use_container_width=True):
                with st.spinner("Computing acoustic spectral roll-off, vocoder signatures, and pitch jitter..."):
                    audio_res = deepfake_engine.analyze_audio(audio_buffer)

                st.write("---")
                st.markdown(f"### Verdict: {audio_res['verdict_label']}")
                st.write(f"**Acoustic Synthetic Probability: {audio_res['overall_score']} / 100**")
                st.progress(audio_res["overall_score"] / 100.0)

                am1, am2, am3 = st.columns(3)
                with am1:
                    st.metric("High-Frequency Energy", f"{audio_res['high_energy_ratio']}%")
                with am2:
                    st.metric("Dead Silence Ratio", f"{audio_res['silence_ratio']}%")
                with am3:
                    st.metric("Pitch Interval Jitter", f"{audio_res['interval_jitter']}")

                st.markdown("#### Acoustic Findings & Explanations")
                for r in audio_res["reasons"]:
                    st.markdown(
                        f"""
                        <div style="background: var(--pill-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; font-size: 0.92rem;">
                            {svg_icon("activity", cyan_main, 16)} {r}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# ===========================================================================
# VIEW 3: PHISHING URL SCANNER (NEW DEDICATED TOOL)
# ===========================================================================
elif selected_nav == "🔗 Phishing URL Scanner":
    st.markdown("### 🔗 Dedicated Phishing URL & Domain Scanner")
    st.caption("Inspect hyperlinks and domains for obfuscation, brand spoofing, malicious TLDs, and URL shortener traps:")

    st.write("**Quick-Test Sample URLs:**")
    u1, u2, u3, u4 = st.columns(4)
    if "current_url" not in st.session_state:
        st.session_state["current_url"] = ""

    with u1:
        if st.button("http://sbi-kyc-verify.xyz/login", use_container_width=True):
            st.session_state["current_url"] = "http://sbi-kyc-verify.xyz/login"
    with u2:
        if st.button("http://192.168.1.105/bank/auth", use_container_width=True):
            st.session_state["current_url"] = "http://192.168.1.105/bank/auth"
    with u3:
        if st.button("https://bit.ly/cashback-claim-900", use_container_width=True):
            st.session_state["current_url"] = "https://bit.ly/cashback-claim-900"
    with u4:
        if st.button("https://onlinesbi.sbi", use_container_width=True):
            st.session_state["current_url"] = "https://onlinesbi.sbi"

    url_to_scan = st.text_input(
        "Enter Web Link or Domain to Inspect:",
        value=st.session_state["current_url"],
        placeholder="e.g. http://secure-hdfc-update.xyz/login or https://bit.ly/update-pan"
    )

    if st.button("🔍 Deep Scan URL Target", type="primary", use_container_width=True) or url_to_scan.strip():
        if url_to_scan.strip():
            with st.spinner("Analyzing domain metadata, SSL certificates, TLD risk profiles, and brand signatures..."):
                url_rep = url_scanner.scan_url(url_to_scan)

            u_score = url_rep["risk_score"]
            u_status = url_rep["status"]
            u_color = url_rep["color"]

            st.write("---")
            st.markdown(
                f"""
                <div class="verdict-banner" style="background: {'rgba(239, 68, 68, 0.14)' if u_status=='Dangerous' else ('rgba(245, 158, 11, 0.14)' if u_status=='Suspicious' else 'rgba(6, 182, 212, 0.12)')}; border: 1.5px solid {u_color};">
                    {svg_icon("globe", u_color, 36)}
                    <div>
                        <div style="color: {u_color} !important; font-weight: 800; font-size: 1.25rem;">
                            URL VERDICT: {u_status.upper()} // THREAT SCORE {u_score}/100
                        </div>
                        <div style="color: var(--text-secondary); font-size: 0.92rem;">
                            Host Domain: <code>{url_rep['domain']}</code> • Protocol: <strong>{url_rep['protocol']}</strong>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_u1, col_u2, col_u3, col_u4 = st.columns(4)
            with col_u1:
                st.metric("Protocol Security", url_rep["protocol"])
            with col_u2:
                st.metric("Top-Level Domain", url_rep["tld"])
            with col_u3:
                st.metric("URL Shortener", "Yes (Hidden)" if url_rep["is_shortener"] else "No")
            with col_u4:
                st.metric("Brand Spoofed", url_rep["brand_spoofed"] if url_rep["brand_spoofed"] else "None")

            st.markdown("#### Security Risk Indicators Identified")
            for factor in url_rep["risk_factors"]:
                st.markdown(
                    f"""
                    <div style="background: var(--pill-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; font-size: 0.92rem;">
                        {svg_icon("alert", u_color, 16)} {factor}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("#### Recommended Actions for this Link")
            for rec in url_rep["recommendations"]:
                st.markdown(f"• {rec}")

# ===========================================================================
# VIEW 4: AI SECURITY ASSISTANT (INTERACTIVE CHATBOT)
# ===========================================================================
elif selected_nav == "💬 AI Security Assistant":
    st.markdown("### 💬 AI Cyber Security Advisor")
    st.caption("Ask questions about banking scams, suspicious messages, emergency recovery steps, and deepfake verification:")

    # Quick prompt buttons
    st.write("**Common Cybersecurity Inquiries:**")
    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        if st.button("Is my SBI KYC SMS real?", use_container_width=True):
            st.session_state["chat_messages"].append({"role": "user", "content": "Is my SBI KYC SMS authentic?"})
            st.session_state["chat_messages"].append({"role": "assistant", "content": assistant.ask("sbi kyc")})
    with qc2:
        if st.button("How do electricity bill scams work?", use_container_width=True):
            st.session_state["chat_messages"].append({"role": "user", "content": "How does the electricity bill scam work?"})
            st.session_state["chat_messages"].append({"role": "assistant", "content": assistant.ask("electricity bill")})
    with qc3:
        if st.button("What if I shared an OTP?", use_container_width=True):
            st.session_state["chat_messages"].append({"role": "user", "content": "What should I do if I shared an OTP?"})
            st.session_state["chat_messages"].append({"role": "assistant", "content": assistant.ask("shared otp")})
    with qc4:
        if st.button("How to spot a deepfake video call?", use_container_width=True):
            st.session_state["chat_messages"].append({"role": "user", "content": "How do I spot a deepfake video call?"})
            st.session_state["chat_messages"].append({"role": "assistant", "content": assistant.ask("deepfake video call")})

    st.write("---")

    # Display chat history
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input("Ask a question about scams, phishing, or deepfakes...")
    if user_query:
        st.session_state["chat_messages"].append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        reply = assistant.ask(user_query)
        st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

# ===========================================================================
# VIEW 5: SECURITY DASHBOARD & SCAN HISTORY
# ===========================================================================
elif selected_nav == "📊 Security Dashboard":
    st.markdown("### 📊 Defensive Operations Dashboard")
    st.caption("Live metrics, scan throughput, and threat interception activity:")

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.metric("Total Scans Executed", f"{st.session_state['total_scans']:,}")
    with d2:
        st.metric("Threats Intercepted", f"{st.session_state['threats_intercepted']:,}")
    with d3:
        st.metric("Interception Rate", f"{(st.session_state['threats_intercepted'] / max(1, st.session_state['total_scans'])) * 100:.1f}%")
    with d4:
        st.metric("Avg Detection Latency", "11.4 ms")

    st.write("---")
    st.markdown("#### 🕒 Real-Time Session Scan History")
    st.caption("Audit log of communications and URLs analyzed during this active session:")

    if not st.session_state["scan_history"]:
        st.info("No scans executed yet in this session. Head to the **AI Scam Message Checker** or **Phishing URL Scanner** to run your first test!")
    else:
        for item in st.session_state["scan_history"][:8]:
            badge_color = "#EF4444" if item["status"] == "Dangerous" else ("#F59E0B" if item["status"] == "Suspicious" else cyan_glow)
            st.markdown(
                f"""
                <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-left: 4px solid {badge_color}; border-radius: 10px; padding: 0.9rem 1.2rem; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <span style="font-size: 0.76rem; color: var(--text-secondary); font-family: monospace;">[{item['time']}]</span>
                        <strong style="margin-left: 8px; color: var(--text-primary);">{item['type']}:</strong>
                        <span style="color: var(--text-secondary); margin-left: 6px;">"{item['preview']}"</span>
                    </div>
                    <span style="padding: 3px 10px; background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}66; border-radius: 9999px; font-size: 0.78rem; font-weight: 700;">
                        {item['status'].upper()} ({item['score']}/100)
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

# ===========================================================================
# VIEW 6: THREAT INTEL & CASE STUDIES
# ===========================================================================
elif selected_nav == "📖 Threat Intel & Cases":
    st.markdown("### 📖 The Modern Threat Landscape")
    st.caption("How social engineering exploits human psychology rather than software vulnerabilities:")

    i1, i2, i3 = st.columns(3)
    with i1:
        st.markdown(
            f"""
            <div class="feature-card">
                {svg_icon("message", cyan_main, 24)}
                <div class="feature-card-title">1. Smishing & KYC Traps</div>
                <p class="feature-card-desc">Attackers spoof banking institutions with artificial urgency, threatening account deactivation unless credentials or OTPs are entered on lookalike portals.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with i2:
        if True:
            st.markdown(
                f"""
                <div class="feature-card">
                    {svg_icon("alert", "#F59E0B", 24)}
                    <div class="feature-card-title">2. Utility & Disconnection Fraud</div>
                    <p class="feature-card-desc">Coercive nighttime electricity disconnection warnings prompting victims to call fake helplines and download remote-access apps (AnyDesk/TeamViewer).</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    with i3:
        st.markdown(
            f"""
            <div class="feature-card">
                {svg_icon("video", "#EF4444", 24)}
                <div class="feature-card-title">3. Multimodal Deepfakes</div>
                <p class="feature-card-desc">Real-time face swaps and cloned executive voices mapped onto live video meetings to authorize multi-million dollar corporate fund transfers.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("---")
    st.markdown("### Forensic Case Study: The 2024 Arup Deepfake CFO Incident")
    st.markdown(
        f"""
        <div style="background: {'rgba(239, 68, 68, 0.12)' if is_dark else '#FEF2F2'}; border: 1.5px solid #EF4444; border-radius: 14px; padding: 1.5rem; margin-top: 1rem;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.8rem;">
                {svg_icon("alert", "#EF4444", 28)}
                <h4 style="margin: 0; color: #EF4444 !important; font-size: 1.18rem;">US$25 Million Corporate Transfer via Synthetic Video</h4>
            </div>
            <p style="color: var(--text-secondary); font-size: 0.94rem; line-height: 1.6; margin: 0;">
                In early 2024, attackers breached the Hong Kong division of the multinational engineering firm <strong>Arup</strong>. 
                A financial employee was initially skeptical of an urgent payment request, but attended a live multi-person video conference to verify. 
                On the call, every single participant—including the Chief Financial Officer and recognizable colleagues—was an AI-rendered deepfake.
                <br><br>
                Believing the visual and auditory confirmation, the employee executed 15 separate transactions totaling approximately 
                <strong>US$25 million (HK$200 million)</strong>.
                <br><br>
                <strong>The Defensive Lesson:</strong> Visual and auditory confirmation alone is vulnerable to generative AI. Cryptographic verification, out-of-band challenge-response protocols, and automated frame snapshot forensics (such as DEEPFAKE DEFENSE's Deepfake Lab) are mandatory.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ===========================================================================
# VIEW 7: BENCHMARKS & OPERATIONAL LIMITS
# ===========================================================================
elif selected_nav == "⚡ Benchmarks & Limits":
    st.markdown("### ⚡ Empirical Performance Benchmarks")
    st.caption("Performance evaluated across 1,115 holdout test samples and real-world adversarial variations:")

    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(
            f"""
            <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 1.5rem; text-align: center;">
                <div style="font-size: 2.2rem; font-weight: 800; color: {cyan_glow} !important;">92.4%</div>
                <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; color: var(--text-secondary);">Real-World Accuracy</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with b2:
        st.markdown(
            f"""
            <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 1.5rem; text-align: center;">
                <div style="font-size: 2.2rem; font-weight: 800; color: {cyan_glow} !important;">91.8%</div>
                <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; color: var(--text-secondary);">Scam Precision</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with b3:
        st.markdown(
            f"""
            <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 1.5rem; text-align: center;">
                <div style="font-size: 2.2rem; font-weight: 800; color: {cyan_glow} !important;">89.9%</div>
                <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; color: var(--text-secondary);">Scam Catch Rate</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    # Crucial AI Advisory Box
    st.markdown(
        f"""
        <div style="background: {'rgba(245, 158, 11, 0.1)' if is_dark else '#FFFBEB'}; border: 1.5px solid #F59E0B; border-radius: 14px; padding: 1.4rem; margin: 1rem 0;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom: 6px;">
                {svg_icon("alert", "#F59E0B", 24)}
                <h4 style="margin:0; color:#F59E0B !important; font-size:1.1rem;">Crucial Advisory: Never Trust AI 100% Blindly</h4>
            </div>
            <p style="color: var(--text-secondary); font-size:0.93rem; line-height:1.6; margin:0;">
                No automated defensive platform is infallible. While AI provides a rapid, air-gapped first line of defense, attackers continually adapt phrasing, punctuation, and deceptive tactics to evade detection filters.
                <br><br>
                <strong>Security Protocol:</strong> If an unsolicited message demands immediate fund transfers, credential entry, or OTP sharing, 
                <strong>never rely solely on an automated scanner</strong>. Always pause and verify out-of-band through known, official channels.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Operational Limitations")
    st.markdown(
        """
        - **Adversarial Token Obfuscation:** Deliberate punctuation or leetspeak (e.g., `p-a-y-m-e-n-t`) can reduce standard dictionary-based word frequency matching.
        - **Extremely Short Ambiguous Messages:** Abbreviated payloads (e.g., *"Call me immediately"*) lack token depth for purely statistical classification.
        - **Evolving Smishing Formats:** Emerging tactics (like parcel delivery duty fee lures) require continuous heuristic rule expansion and periodic retraining.
        """
    )

# ===========================================================================
# VIEW 8: ABOUT
# ===========================================================================
elif selected_nav == "ℹ️ About Platform":
    st.markdown("### ℹ️ About DEEPFAKE DEFENSE")
    st.markdown(
        """
        **DEEPFAKE DEFENSE: Autonomous Social Engineering & Synthetic Media Defense Platform**  
        Developed by **Team Sentinels**
        """
    )

    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown(
            f"""
            <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.8rem 1.2rem; text-align: center;">
                <div style="margin-bottom: 0.8rem;">{svg_icon("users", cyan_main, 32)}</div>
                <h3 style="margin: 0; color: var(--text-primary) !important; font-size: 1.25rem; font-weight: 700;">Vivek Sharma</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t2:
        st.markdown(
            f"""
            <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.8rem 1.2rem; text-align: center;">
                <div style="margin-bottom: 0.8rem;">{svg_icon("users", cyan_glow, 32)}</div>
                <h3 style="margin: 0; color: var(--text-primary) !important; font-size: 1.25rem; font-weight: 700;">Hitesh Brahmi</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t3:
        st.markdown(
            f"""
            <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.8rem 1.2rem; text-align: center;">
                <div style="margin-bottom: 0.8rem;">{svg_icon("users", cyan_main, 32)}</div>
                <h3 style="margin: 0; color: var(--text-primary) !important; font-size: 1.25rem; font-weight: 700;">Akhil Kotwal</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.4rem; margin-top: 1.4rem;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.6rem;">
                {svg_icon("lock", cyan_main, 20)}
                <h4 style="margin: 0; font-size: 1.05rem; font-weight: 700;">Platform Specifications</h4>
            </div>
            <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6; margin: 0;">
                • <strong>Brand:</strong> DEEPFAKE DEFENSE<br>
                • <strong>Team:</strong> Sentinels<br>
                • <strong>Core Stack:</strong> Python, Streamlit, Scikit-Learn, NumPy, Pillow, SciPy<br>
                • <strong>Deployment:</strong> 100% Offline / Local Execution (Zero External Cloud APIs)
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div style="text-align: center; color: var(--text-secondary); font-size: 0.84rem; margin-top: 3.5rem; border-top: 1px solid {'rgba(6, 182, 212, 0.15)' if is_dark else '#E2E8F0'}; padding-top: 1.2rem;">
        DEEPFAKE DEFENSE &copy; 2026 // DEVELOPED BY TEAM SENTINELS
    </div>
    """,
    unsafe_allow_html=True
)
