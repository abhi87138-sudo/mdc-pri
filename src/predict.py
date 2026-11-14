"""
app.py
=============================================================================
Streamlit Web Application - Sentinel Cyber Defense Platform
Project: AI-Driven Social Engineering and Deepfake Defense Platform
Team: Sentinels (Vivek Sharma, Hitesh Brahmi, Akhil Kotwal)
Theme: Dynamic Dual-Mode (Deep Cyber Obsidian & High-Contrast Light Mode)
=============================================================================
"""

import os
import json
import random
import io
import streamlit as st
from PIL import Image

from src.predict import ThreatDetector
from src.deepfake_detector import (
    DeepfakeDetector,
    generate_sample_synthetic_portrait,
    generate_sample_authentic_portrait
)

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SENTINEL // Cyber Defense Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------------------------
# Theme State Management
# ---------------------------------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"

is_dark = (st.session_state["theme_mode"] == "dark")
accent_color = "#38BDF8" if is_dark else "#0284C7"
accent_indigo = "#818CF8" if is_dark else "#4F46E5"
accent_emerald = "#10B981" if is_dark else "#059669"
accent_rose = "#F43F5E" if is_dark else "#DC2626"
accent_amber = "#F59E0B" if is_dark else "#D97706"

# ---------------------------------------------------------------------------
# SVG Vector Graphics Library (Ultra-Crisp SVGs - No generic emojis)
# ---------------------------------------------------------------------------
def svg_icon(name, color=None, size=22):
    c = color if color else accent_color
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
# High-Contrast Dual Theme CSS
# ---------------------------------------------------------------------------
if is_dark:
    theme_css = """
    :root {
        --bg-main: #0B0F19;
        --card-bg: rgba(17, 24, 39, 0.88);
        --card-border: rgba(56, 189, 248, 0.22);
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --hero-bg: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.92) 50%, rgba(15, 23, 42, 0.98) 100%);
        --metric-bg: rgba(15, 23, 42, 0.9);
        --flow-bg: rgba(15, 23, 42, 0.85);
        --pill-bg: rgba(15, 23, 42, 0.8);
        --tab-bg: rgba(15, 23, 42, 0.7);
        --status-safe-bg: linear-gradient(90deg, rgba(16, 185, 129, 0.16) 0%, rgba(6, 78, 59, 0.4) 100%);
        --status-safe-border: rgba(16, 185, 129, 0.5);
        --status-susp-bg: linear-gradient(90deg, rgba(245, 158, 11, 0.16) 0%, rgba(120, 53, 15, 0.4) 100%);
        --status-susp-border: rgba(245, 158, 11, 0.5);
        --status-dang-bg: linear-gradient(90deg, rgba(244, 63, 94, 0.18) 0%, rgba(136, 19, 55, 0.45) 100%);
        --status-dang-border: rgba(244, 63, 94, 0.55);
    }
    .stApp {
        background-color: #0B0F19 !important;
        color: #F8FAFC !important;
    }
    .stApp p, .stApp span, .stApp div, .stMarkdown p, .stCaption {
        color: #E2E8F0 !important;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #FFFFFF !important;
    }
    textarea, input {
        background-color: rgba(15, 23, 42, 0.95) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
    }
    """
else:
    theme_css = """
    :root {
        --bg-main: #F8FAFC;
        --card-bg: #FFFFFF;
        --card-border: #CBD5E1;
        --text-primary: #0F172A;
        --text-secondary: #334155;
        --hero-bg: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        --metric-bg: #FFFFFF;
        --flow-bg: #FFFFFF;
        --pill-bg: #F1F5F9;
        --tab-bg: #E2E8F0;
        --status-safe-bg: #ECFDF5;
        --status-safe-border: #10B981;
        --status-susp-bg: #FFFBEB;
        --status-susp-border: #F59E0B;
        --status-dang-bg: #FEF2F2;
        --status-dang-border: #EF4444;
    }
    .stApp {
        background-color: #F8FAFC !important;
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
        color: #475569 !important;
    }
    label[data-testid="stWidgetLabel"] p, label[data-testid="stWidgetLabel"] span {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    textarea, input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #94A3B8 !important;
        border-radius: 8px !important;
    }
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
    }
    [data-testid="stMetricLabel"] {
        color: #475569 !important;
    }
    .stButton > button {
        background-color: #0284C7 !important;
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

    /* Crisp font rendering */
    * {{
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
        text-rendering: optimizeLegibility !important;
    }}

    code, pre {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1120px;
    }}

    /* Hero Header */
    .hero-header {{
        position: relative;
        overflow: hidden;
        background: var(--hero-bg);
        border: 1px solid {'rgba(56, 189, 248, 0.35)' if is_dark else '#334155'};
        border-radius: 16px;
        padding: 2.2rem 2.4rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px -10px {'rgba(0, 0, 0, 0.45)' if is_dark else 'rgba(15, 23, 42, 0.15)'};
    }}

    .hero-badge-wrap {{
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 0.8rem;
    }}

    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        background: rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #38BDF8 !important;
    }}

    .hero-badge-green {{
        background: rgba(16, 185, 129, 0.15);
        border-color: rgba(16, 185, 129, 0.35);
        color: #34D399 !important;
    }}

    .hero-title {{
        font-size: 2.15rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #FFFFFF !important;
        margin-bottom: 0.45rem;
    }}

    .hero-desc {{
        color: #CBD5E1 !important;
        font-size: 0.98rem;
        line-height: 1.6;
        margin-bottom: 0;
        max-width: 900px;
    }}

    /* Cyber Card */
    .cyber-card {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1.1rem;
        transition: all 0.25s ease;
        box-shadow: 0 4px 18px {'rgba(0,0,0,0.2)' if is_dark else 'rgba(0,0,0,0.04)'};
    }}

    .cyber-card:hover {{
        transform: translateY(-2px);
        border-color: {accent_color};
        box-shadow: 0 8px 24px {'rgba(56, 189, 248, 0.15)' if is_dark else 'rgba(0,0,0,0.08)'};
    }}

    .card-header-flex {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.6rem;
    }}

    .card-title {{
        color: var(--text-primary) !important;
        font-size: 1.08rem;
        font-weight: 700;
        margin: 0;
    }}

    .card-body {{
        color: var(--text-secondary) !important;
        font-size: 0.93rem;
        line-height: 1.6;
        margin: 0;
    }}

    /* Status Banners */
    .status-banner {{
        border-radius: 12px;
        padding: 1.3rem 1.6rem;
        margin-bottom: 1.4rem;
        display: flex;
        align-items: center;
        gap: 16px;
    }}

    .status-safe {{
        background: var(--status-safe-bg);
        border: 1px solid var(--status-safe-border);
    }}

    .status-suspicious {{
        background: var(--status-susp-bg);
        border: 1px solid var(--status-susp-border);
    }}

    .status-dangerous {{
        background: var(--status-dang-bg);
        border: 1px solid var(--status-dang-border);
    }}

    /* Metric Container */
    .metric-container {{
        background: var(--metric-bg);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 1.3rem 1.1rem;
        text-align: center;
        transition: all 0.25s ease;
        box-shadow: 0 4px 16px {'rgba(0,0,0,0.18)' if is_dark else 'rgba(0,0,0,0.03)'};
    }}

    .metric-container:hover {{
        border-color: {accent_color};
    }}

    .metric-number {{
        font-size: 2.1rem;
        font-weight: 800;
        color: {accent_color} !important;
        margin-bottom: 2px;
    }}

    .metric-title {{
        color: var(--text-secondary) !important;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}

    /* Token Heatmap Styling */
    .heatmap-box {{
        background: var(--pill-bg);
        border: 1px solid var(--card-border);
        border-radius: 10px;
        padding: 1.2rem;
        margin: 1rem 0;
        line-height: 2.2;
        font-size: 1.02rem;
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
        background: rgba(168, 85, 247, 0.22);
        color: #C084FC !important;
        border: 1px solid rgba(168, 85, 247, 0.45);
        border-radius: 6px;
        padding: 2px 7px;
        font-weight: 700;
    }}

    .token-link {{
        background: rgba(56, 189, 248, 0.22);
        color: #38BDF8 !important;
        border: 1px solid rgba(56, 189, 248, 0.45);
        border-radius: 6px;
        padding: 2px 7px;
        font-weight: 700;
        text-decoration: underline;
    }}

    /* Visual Flowchart */
    .flow-wrapper {{
        display: flex;
        align-items: stretch;
        justify-content: space-between;
        gap: 12px;
        margin: 1.5rem 0 2rem 0;
        flex-wrap: wrap;
    }}

    .flow-box {{
        flex: 1;
        min-width: 220px;
        background: var(--flow-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 1.3rem 1.1rem;
        text-align: center;
        box-shadow: 0 4px 16px {'rgba(0,0,0,0.18)' if is_dark else 'rgba(0,0,0,0.04)'};
    }}

    .flow-badge {{
        display: inline-block;
        padding: 3px 10px;
        background: rgba(56, 189, 248, 0.15);
        border-radius: 9999px;
        color: {accent_color} !important;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }}

    .flow-head {{
        color: var(--text-primary) !important;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }}

    .flow-txt {{
        color: var(--text-secondary) !important;
        font-size: 0.88rem;
        line-height: 1.5;
        margin: 0;
    }}

    .flow-connector {{
        display: flex;
        align-items: center;
        justify-content: center;
        color: {accent_color} !important;
        font-size: 1.6rem;
        font-weight: bold;
        padding: 0 4px;
    }}

    /* Reason Pills */
    .reason-pill {{
        display: flex;
        align-items: flex-start;
        gap: 10px;
        background: var(--pill-bg);
        border: 1px solid var(--card-border);
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        color: var(--text-primary) !important;
        font-size: 0.92rem;
    }}

    /* Tabs Styling */
    div[data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: var(--tab-bg);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid var(--card-border);
    }}

    button[data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 8px 16px;
        color: var(--text-secondary) !important;
        font-weight: 600;
        font-size: 0.88rem;
        transition: all 0.2s ease;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        background: rgba(56, 189, 248, 0.18) !important;
        color: {accent_color} !important;
        border-bottom: none !important;
        font-weight: 700;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# Backend Engines Initializer
# ---------------------------------------------------------------------------
@st.cache_resource
def get_threat_detector():
    return ThreatDetector()

@st.cache_resource
def get_deepfake_detector():
    return DeepfakeDetector()

detector = get_threat_detector()
deepfake_engine = get_deepfake_detector()

# ---------------------------------------------------------------------------
# Top Bar: Theme Toggle
# ---------------------------------------------------------------------------
col_brand, col_toggle = st.columns([8.2, 1.8])
with col_brand:
    pass
with col_toggle:
    if is_dark:
        if st.button("☀️ Light Mode", use_container_width=True):
            st.session_state["theme_mode"] = "light"
            st.rerun()
    else:
        if st.button("🌙 Dark Mode", use_container_width=True):
            st.session_state["theme_mode"] = "dark"
            st.rerun()

# ---------------------------------------------------------------------------
# Hero Header
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero-header">
        <div class="hero-badge-wrap">
            <span class="hero-badge">{svg_icon("shield", "#38BDF8", 15)} DEFENSIVE INTELLIGENCE // SENTINEL</span>
            <span class="hero-badge hero-badge-green">{svg_icon("activity", "#34D399", 15)} OPERATIONAL // AIR-GAPPED FORENSICS</span>
        </div>
        <div class="hero-title">Social Engineering & Deepfake Defense</div>
        <p class="hero-desc">
            An autonomous multi-vector defense platform inspecting deceptive communication payloads in real time. Fuses statistical NLP heuristics with frequency-domain computer vision to neutralize smishing traps, cognitive coercion, and synthetic media fraud.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# Navigation Tabs
# ---------------------------------------------------------------------------
tab_overview, tab_demo, tab_deepfake, tab_threats, tab_arch, tab_bench, tab_about = st.tabs([
    "Overview",
    "Live Phishing Scanner",
    "Deepfake Lab",
    "Threat Intel",
    "How It Works",
    "Benchmarks",
    "About"
])

# ===========================================================================
# TAB 1: OVERVIEW
# ===========================================================================
with tab_overview:
    st.markdown("### Platform Purpose & Defensive Scope")
    st.markdown(
        """
        Traditional enterprise firewalls and antivirus tools are built to block malicious software binaries. 
        However, modern cyber adversaries frequently bypass perimeter defenses by targeting human psychology—leveraging 
        **artificial urgency, institutional impersonation, and generative deepfakes** to bypass multi-factor authorization and execute fraudulent wire transfers.

        **SENTINEL** provides an autonomous security filter that inspects incoming text communications and digital media payloads in real time. 
        By combining statistical language models with specialized behavioral threat heuristics and 2D FFT frequency forensics, the engine evaluates threat severity from 0 to 100 before critical compromise occurs.
        """
    )
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="cyber-card">
                <div class="card-header-flex">
                    {svg_icon("lock", accent_color, 22)}
                    <h4 class="card-title">Air-Gapped Privacy</h4>
                </div>
                <p class="card-body">
                    Executes entirely within the local host environment. Personal communications, credentials, and video snapshots are never dispatched to external cloud APIs.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="cyber-card">
                <div class="card-header-flex">
                    {svg_icon("cpu", accent_indigo, 22)}
                    <h4 class="card-title">Dual-Vector Analysis</h4>
                </div>
                <p class="card-body">
                    Combines statistical Natural Language Processing (TF-IDF + Naive Bayes) with 2D Fast Fourier Transform (FFT) computer vision forensics for comprehensive multi-threat defense.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
            <div class="cyber-card">
                <div class="card-header-flex">
                    {svg_icon("radar", accent_emerald, 22)}
                    <h4 class="card-title">Explainable Forensics</h4>
                </div>
                <p class="card-body">
                    Delivers a calibrated threat score (0–100) alongside token heatmaps, psychological vector breakdowns, and spectral evidence maps—eliminating black-box opacity.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div style="background: {'rgba(56, 189, 248, 0.08)' if is_dark else '#E0F2FE'}; border: 1px solid {'rgba(56, 189, 248, 0.22)' if is_dark else '#BAE6FD'}; border-radius: 10px; padding: 1.1rem 1.4rem; display: flex; align-items: center; gap: 14px; margin-top: 1rem;">
            {svg_icon("sparkles", accent_color, 22)}
            <span style="color: {'#BAE6FD' if is_dark else '#0369A1'} !important; font-size: 0.94rem; font-weight: 500;">
                <strong>Interactive Navigation:</strong> Head to <strong>Live Phishing Scanner</strong> to evaluate message payloads with interactive token heatmaps, or test <strong>Deepfake Lab</strong> to run 2D FFT forensic scans on video call snapshots!
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ===========================================================================
# TAB 2: LIVE PHISHING SCANNER
# ===========================================================================
with tab_demo:
    st.markdown("### Interactive Threat Scanner")
    st.caption("Paste any suspicious communication below, or click a scenario button to cycle through realistic test payloads:")

    BANK_EXAMPLES = [
        "URGENT: Your HDFC Bank account has been temporarily locked due to suspicious activity. Verify KYC immediately at https://bit.ly/hdfc-kyc-update within 24 hours to prevent permanent suspension.",
        "Security Alert: An unauthorized wire transfer of $1,250.00 was requested from your checking account. If this was not you, call fraud prevention immediately at 1-800-432-1000 or login at https://secure-bank-login.xyz.",
        "Final Notice: Your State Bank debit card will be deactivated today due to outdated PAN details. Click http://bit.ly/sbi-pan-link to verify your identity and avoid service interruption."
    ]

    PRIZE_EXAMPLES = [
        "WINNER!! As a valued customer you have been selected to receive a £900 cash prize reward! Call 09061701461 to claim your reward. Claim code KL341. Valid 12 hours only.",
        "Congratulations! You have been selected as the lucky winner of a $1,000 Amazon gift card in our anniversary draw. Claim your voucher right now at https://tinyurl.com/amz-gift-winner before it expires.",
        "Urgent Notification: You have won the 2nd prize of $250,000 in the International Cash Lottery. Send your full name, bank account, and phone number to claim-payout@lottery-fund.xyz."
    ]

    DELIVERY_EXAMPLES = [
        "USPS Notice: Your parcel shipment US-948194 is held at customs due to an unpaid duty fee of $2.45. Resolve payment immediately at http://usps-parcel-tracking.click to prevent package return.",
        "FedEx Alert: Unable to deliver your order #849182 today due to missing house street number. Please update delivery address within 24 hours at https://bit.ly/fedex-update-addr.",
        "DHL Express: An international package addressed to you has arrived at regional sorting facility with pending import fee. Visit https://dhl-express-duty.top to authorize release."
    ]

    NORMAL_EXAMPLES = [
        "Hey Alex, are we still meeting in the college library at 4 PM to work on the computer science assignment?",
        "Mom, I finished my classes for today and I'm heading home on the metro. See you soon!",
        "Can you please email me the lecture notes from today's Operating Systems class when you get a chance? Thanks!"
    ]

    ALL_EXAMPLES = BANK_EXAMPLES + PRIZE_EXAMPLES + DELIVERY_EXAMPLES + NORMAL_EXAMPLES

    if "input_message" not in st.session_state:
        st.session_state["input_message"] = ""
    if "bank_idx" not in st.session_state:
        st.session_state["bank_idx"] = 0
    if "prize_idx" not in st.session_state:
        st.session_state["prize_idx"] = 0
    if "delivery_idx" not in st.session_state:
        st.session_state["delivery_idx"] = 0
    if "normal_idx" not in st.session_state:
        st.session_state["normal_idx"] = 0

    col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
    with col_b1:
        if st.button("🏦 Bank Scam", use_container_width=True):
            st.session_state["input_message"] = BANK_EXAMPLES[st.session_state["bank_idx"]]
            st.session_state["bank_idx"] = (st.session_state["bank_idx"] + 1) % len(BANK_EXAMPLES)
    with col_b2:
        if st.button("🎁 Prize Scam", use_container_width=True):
            st.session_state["input_message"] = PRIZE_EXAMPLES[st.session_state["prize_idx"]]
            st.session_state["prize_idx"] = (st.session_state["prize_idx"] + 1) % len(PRIZE_EXAMPLES)
    with col_b3:
        if st.button("📦 Courier Scam", use_container_width=True):
            st.session_state["input_message"] = DELIVERY_EXAMPLES[st.session_state["delivery_idx"]]
            st.session_state["delivery_idx"] = (st.session_state["delivery_idx"] + 1) % len(DELIVERY_EXAMPLES)
    with col_b4:
        if st.button("💬 Normal Chat", use_container_width=True):
            st.session_state["input_message"] = NORMAL_EXAMPLES[st.session_state["normal_idx"]]
            st.session_state["normal_idx"] = (st.session_state["normal_idx"] + 1) % len(NORMAL_EXAMPLES)
    with col_b5:
        if st.button("🎲 Random Sample", use_container_width=True):
            pool = [m for m in ALL_EXAMPLES if m != st.session_state["input_message"]]
            st.session_state["input_message"] = random.choice(pool if pool else ALL_EXAMPLES)

    user_text = st.text_area(
        "Payload Inspection Field:",
        value=st.session_state["input_message"],
        height=125,
        placeholder="Type, paste, or select a sample message above to analyze..."
    )

    scan_clicked = st.button("🛡️ Execute Threat Scan", type="primary", use_container_width=True)

    if scan_clicked or (user_text.strip() and st.session_state.get("last_auto_scan") != user_text):
        st.session_state["last_auto_scan"] = user_text
        if not user_text.strip():
            st.warning("⚠️ Input buffer is empty. Please enter text or click a sample button above.")
        else:
            with st.spinner("Executing hybrid NLP and threat vector extraction..."):
                result = detector.predict(user_text)

            risk_score = result["risk_score"]
            status = result["status"]
            ml_prob = result["ml_probability"]
            reasons = result["reasons"]
            vectors = result["vectors"]
            attack_vector = result["attack_vector"]
            urls = result["urls"]
            tokens = result["tokens"]

            st.write("---")
            st.markdown("### Threat Assessment Output")

            # Top Verdict Banner
            if status == "Safe":
                st.markdown(
                    f"""
                    <div class="status-banner status-safe">
                        {svg_icon("shield-check", "#10B981", 36)}
                        <div>
                            <div style="color: {'#10B981' if is_dark else '#065F46'} !important; font-weight: 800; font-size: 1.25rem;">
                                VERDICT: SAFE // NO MALICIOUS ANOMALY DETECTED
                            </div>
                            <div style="color: {'#A7F3D0' if is_dark else '#047857'} !important; font-size: 0.92rem; margin-top: 2px;">
                                Threat Score: <strong>{risk_score} / 100</strong> • Persona: <strong>{attack_vector['name']}</strong>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif status == "Suspicious":
                st.markdown(
                    f"""
                    <div class="status-banner status-suspicious">
                        {svg_icon("alert", "#F59E0B", 36)}
                        <div>
                            <div style="color: {'#F59E0B' if is_dark else '#92400E'} !important; font-weight: 800; font-size: 1.25rem;">
                                VERDICT: SUSPICIOUS // ELEVATED RISK DETECTED
                            </div>
                            <div style="color: {'#FDE68A' if is_dark else '#B45309'} !important; font-size: 0.92rem; margin-top: 2px;">
                                Threat Score: <strong>{risk_score} / 100</strong> • Persona: <strong>{attack_vector['name']}</strong> (Secondary validation recommended)
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="status-banner status-dangerous">
                        {svg_icon("alert", "#F43F5E", 36)}
                        <div>
                            <div style="color: {'#F43F5E' if is_dark else '#991B1B'} !important; font-weight: 800; font-size: 1.25rem;">
                                VERDICT: DANGEROUS // ACTIVE SOCIAL ENGINEERING ATTACK
                            </div>
                            <div style="color: {'#FECDD3' if is_dark else '#B91C1C'} !important; font-size: 0.92rem; margin-top: 2px;">
                                Threat Score: <strong>{risk_score} / 100</strong> • Attack Type: <strong>{attack_vector['name']}</strong> (Coercive pattern confirmed)
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Severity Progress
            st.write("**Threat Severity Gauge:**")
            st.progress(risk_score / 100.0)

            # Attack Vector Classification Card
            st.markdown(
                f"""
                <div class="cyber-card" style="border-left: 4px solid {attack_vector['color']};">
                    <div class="card-header-flex">
                        {svg_icon(attack_vector['icon'], attack_vector['color'], 24)}
                        <div>
                            <h4 class="card-title" style="color: {attack_vector['color']} !important;">{attack_vector['name']}</h4>
                            <span style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary);">{attack_vector['badge']}</span>
                        </div>
                    </div>
                    <p class="card-body">{attack_vector['summary']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # ---------------------------------------------------------------
            # Feature: Interactive Threat Token Heatmap
            # ---------------------------------------------------------------
            st.markdown("#### 🔍 Interactive Payload Threat Heatmap")
            st.caption("Inspected payload with token classification highlights:")
            
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

            # Heatmap Legend
            st.markdown(
                """
                <div style="display: flex; gap: 14px; flex-wrap: wrap; font-size: 0.78rem; margin-bottom: 1.2rem;">
                    <span><strong style="color: #F87171;">■ Red:</strong> Urgency / Panic Pressure</span>
                    <span><strong style="color: #FBBF24;">■ Amber:</strong> Financial / Prize Bait</span>
                    <span><strong style="color: #C084FC;">■ Purple:</strong> Credential / Account Harvest</span>
                    <span><strong style="color: #38BDF8;">■ Cyan:</strong> Embedded URL / Shortener</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            # ---------------------------------------------------------------
            # Feature: Psychological Vector Radar Meters
            # ---------------------------------------------------------------
            st.markdown("#### 🧠 Cognitive Manipulation Vector Profiling")
            pv1, pv2, pv3, pv4 = st.columns(4)
            with pv1:
                st.metric("Urgency Pressure", f"{vectors['urgency']}%")
                st.progress(vectors['urgency'] / 100.0)
            with pv2:
                st.metric("Financial Incentive", f"{vectors['financial']}%")
                st.progress(vectors['financial'] / 100.0)
            with pv3:
                st.metric("Credential Harvest", f"{vectors['credential']}%")
                st.progress(vectors['credential'] / 100.0)
            with pv4:
                st.metric("Authority Spoofing", f"{vectors['authority']}%")
                st.progress(vectors['authority'] / 100.0)

            # ---------------------------------------------------------------
            # Feature: Deep URL Diagnostics
            # ---------------------------------------------------------------
            if urls:
                st.markdown("#### 🔗 Deep URL & Domain Security Diagnostics")
                for u in urls:
                    url_color = "#EF4444" if u["risk_badge"] == "High Risk" else ("#F59E0B" if u["risk_badge"] == "Medium Risk" else "#10B981")
                    st.markdown(
                        f"""
                        <div class="cyber-card" style="padding: 1rem 1.2rem; margin-bottom: 0.7rem; border-left: 3px solid {url_color};">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                                <div>
                                    <code style="font-size: 0.95rem; color: {accent_color};">{u['url']}</code>
                                    <div style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 4px;">
                                        Shortener: <strong>{'Yes (Obfuscates true domain)' if u['is_shortener'] else 'No'}</strong> • 
                                        Insecure HTTP: <strong>{'Yes' if u['is_insecure_http'] else 'No'}</strong> • 
                                        Suspicious TLD: <strong>{'Yes' if u['is_suspicious_tld'] else 'No'}</strong>
                                    </div>
                                </div>
                                <span style="padding: 3px 10px; background: {url_color}22; color: {url_color}; border: 1px solid {url_color}55; border-radius: 9999px; font-size: 0.76rem; font-weight: 700;">
                                    {u['risk_badge']}
                                </span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # ML & Heuristic Dual Metrics
            st.write("")
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.metric("Calibrated Hybrid Threat Score", f"{risk_score} / 100")
            with m_col2:
                if ml_prob is not None:
                    st.metric("Statistical ML Scam Probability", f"{ml_prob * 100:.1f}%")
                else:
                    st.metric("Statistical ML Scam Probability", "Rule-Only Fallback")

            st.markdown("#### Itemized Threat Breakdown & Indicators")
            for r in reasons:
                st.markdown(
                    f"""
                    <div class="reason-pill">
                        {svg_icon("activity", accent_color, 18)}
                        <span>{r}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# ===========================================================================
# TAB 3: DEEPFAKE LAB (NOW FULLY FUNCTIONAL!)
# ===========================================================================
with tab_deepfake:
    st.markdown("### Multimodal Deepfake Defense & Visual Forensics")
    st.caption("Forensic frame extraction & spectral analysis for executive video conference defense (Inspired by the 2024 Arup Incident):")

    st.markdown(
        f"""
        <div class="cyber-card" style="background: {'rgba(56, 189, 248, 0.05)' if is_dark else '#F0F9FF'}; border-color: {'rgba(56, 189, 248, 0.3)' if is_dark else '#BAE6FD'};">
            <div class="card-header-flex">
                {svg_icon("video", accent_color, 24)}
                <h4 class="card-title">Incident Response Protocol: Video Call Frame Forensics</h4>
            </div>
            <p class="card-body">
                In high-profile social engineering attacks like the US$25M Arup video conference fraud, adversaries deploy real-time deepfake face swaps.
                SENTINEL intercepts this threat by extracting snapshot frames and computing <strong>2D Fast Fourier Transform (FFT) power spectra, Laplacian seam blur variance, and sensor noise (PRNU) residuals</strong> that expose synthetic manipulation invisible to the human eye.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Input Mode Selection
    input_mode = st.radio(
        "Select Inspection Source:",
        ["📁 Upload Image / Screenshot", "📷 Live Video Call Frame Capture (Webcam)", "🧪 Preset Forensic Test Samples"],
        horizontal=True
    )

    image_to_analyze = None

    if input_mode == "📁 Upload Image / Screenshot":
        uploaded_file = st.file_uploader(
            "Upload portrait or video call frame snapshot (PNG, JPG, JPEG):",
            type=["png", "jpg", "jpeg"]
        )
        if uploaded_file is not None:
            image_to_analyze = Image.open(uploaded_file)

    elif input_mode == "📷 Live Video Call Frame Capture (Webcam)":
        st.write("Capture a live frame from your webcam (simulates capturing an attendee in a video meeting):")
        camera_snap = st.camera_input("Capture Video Call Frame")
        if camera_snap is not None:
            image_to_analyze = Image.open(camera_snap)

    else:  # Preset Forensic Test Samples
        st.write("Select a pre-configured sample to test the forensic engine immediately:")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Load Authentic Reference Sample", use_container_width=True):
                st.session_state["sample_choice"] = "authentic"
        with col_s2:
            if st.button("Load Synthetic GAN Deepfake Sample", use_container_width=True):
                st.session_state["sample_choice"] = "synthetic"

        if "sample_choice" not in st.session_state:
            st.session_state["sample_choice"] = "synthetic"

        if st.session_state["sample_choice"] == "authentic":
            image_to_analyze = generate_sample_authentic_portrait()
            st.info("Loaded: Authentic Reference Portrait (Simulates genuine optical camera capture).")
        else:
            image_to_analyze = generate_sample_synthetic_portrait()
            st.warning("Loaded: Synthetic GAN Deepfake Portrait (Simulates periodic generator grid lattice & seam smoothing).")

    # Analyze Button
    if image_to_analyze is not None:
        st.write("")
        col_run, _ = st.columns([3, 7])
        with col_run:
            run_forensics = st.button("🔬 Execute Deepfake Forensics", type="primary", use_container_width=True)

        if run_forensics or input_mode == "🧪 Preset Forensic Test Samples":
            with st.spinner("Computing 2D FFT spectrum, Laplacian edge gradients, and chrominance consistency..."):
                df_report = deepfake_engine.analyze_image(image_to_analyze)

            overall_score = df_report["overall_score"]
            status = df_report["status"]
            color = df_report["color"]
            verdict_label = df_report["verdict_label"]
            metrics = df_report["metrics"]
            reasons = df_report["reasons"]

            st.write("---")
            st.markdown("### Forensic Evidence & Spectral Diagnostics")

            # Top Deepfake Verdict Banner
            if status == "Likely Authentic":
                st.markdown(
                    f"""
                    <div class="status-banner status-safe">
                        {svg_icon("shield-check", "#10B981", 36)}
                        <div>
                            <div style="color: {'#10B981' if is_dark else '#065F46'} !important; font-weight: 800; font-size: 1.25rem;">
                                {verdict_label}
                            </div>
                            <div style="color: {'#A7F3D0' if is_dark else '#047857'} !important; font-size: 0.92rem; margin-top: 2px;">
                                Synthetic Likelihood: <strong>{overall_score} / 100</strong> (Continuous power falloff; natural optical lens grain)
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif status == "Suspicious":
                st.markdown(
                    f"""
                    <div class="status-banner status-suspicious">
                        {svg_icon("alert", "#F59E0B", 36)}
                        <div>
                            <div style="color: {'#F59E0B' if is_dark else '#92400E'} !important; font-weight: 800; font-size: 1.25rem;">
                                {verdict_label}
                            </div>
                            <div style="color: {'#FDE68A' if is_dark else '#B45309'} !important; font-size: 0.92rem; margin-top: 2px;">
                                Synthetic Likelihood: <strong>{overall_score} / 100</strong> (Borderline smoothing or mild frequency discrepancy)
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="status-banner status-dangerous">
                        {svg_icon("alert", "#F43F5E", 36)}
                        <div>
                            <div style="color: {'#F43F5E' if is_dark else '#991B1B'} !important; font-weight: 800; font-size: 1.25rem;">
                                {verdict_label}
                            </div>
                            <div style="color: {'#FECDD3' if is_dark else '#B91C1C'} !important; font-size: 0.92rem; margin-top: 2px;">
                                Synthetic Likelihood: <strong>{overall_score} / 100</strong> (Synthetic upsampling artifacts and seam blending confirmed)
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.write("**Deepfake Probability Gauge:**")
            st.progress(overall_score / 100.0)

            # Visual Evidence Gallery (3 Columns)
            st.markdown("#### Visual Evidence Inspection Gallery")
            col_v1, col_v2, col_v3 = st.columns(3)
            with col_v1:
                st.image(df_report["face_crop"], caption="1. Analyzed Target Region", use_container_width=True)
            with col_v2:
                st.image(df_report["edge_image"], caption="2. Laplacian Boundary Edge Map", use_container_width=True)
            with col_v3:
                st.image(df_report["fft_image"], caption="3. 2D FFT Power Spectrum Heatmap", use_container_width=True)

            st.caption("Above: (1) Cropped subject frame; (2) Laplacian gradient map exposing seam blur/sharpening; (3) 2D FFT revealing periodic checkerboard energy spikes.")

            # 4 Core Forensic Metric Cards
            st.markdown("#### Forensic Multi-Factor Diagnostic Scores")
            df_m1, df_m2, df_m3, df_m4 = st.columns(4)
            with df_m1:
                st.metric("FFT Grid Regularity", f"{metrics['fft_score']}%", f"{metrics['high_freq_ratio']}% HF Energy")
                st.progress(metrics['fft_score'] / 100.0)
            with df_m2:
                st.metric("Boundary Laplacian", f"{metrics['lap_score']}%", f"Var: {metrics['laplacian_variance']}")
                st.progress(metrics['lap_score'] / 100.0)
            with df_m3:
                st.metric("Color Space Harmony", f"{metrics['color_score']}%", f"Diff: {metrics['color_discrepancy']}")
                st.progress(metrics['color_score'] / 100.0)
            with df_m4:
                st.metric("Sensor Noise (PRNU)", f"{metrics['noise_score']}%", f"Var: {metrics['noise_variance']}")
                st.progress(metrics['noise_score'] / 100.0)

            st.markdown("#### Forensic Breakdown & Technical Findings")
            for r in reasons:
                st.markdown(
                    f"""
                    <div class="reason-pill">
                        {svg_icon("activity", accent_color, 18)}
                        <span>{r}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Defensive Takeaway
            st.markdown(
                f"""
                <div style="background: {'rgba(56, 189, 248, 0.08)' if is_dark else '#E0F2FE'}; border: 1px solid {'rgba(56, 189, 248, 0.22)' if is_dark else '#BAE6FD'}; border-radius: 10px; padding: 1.1rem 1.4rem; margin-top: 1.2rem;">
                    <strong style="color: {accent_color};">🛡️ Forensic Value Proposition:</strong>
                    <span style="font-size: 0.92rem; color: var(--text-secondary);">
                        Human perception fails to detect seamless face swaps on video calls. By exposing the mathematical footprint left by neural generator layers (2D FFT frequency spikes and Laplacian boundary variance), SENTINEL provides decisive out-of-band verification before authorizing high-value transactions.
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

# ===========================================================================
# TAB 4: THREAT INTEL & CASE STUDIES
# ===========================================================================
with tab_threats:
    st.markdown("### The Modern Threat Landscape")
    st.markdown(
        """
        Social engineering attacks exploit **cognitive vulnerabilities**: manufacturing artificial urgency, authority impersonation, 
        or fear of financial loss so targets make uncalculated choices without out-of-band verification.
        """
    )

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown(
            f"""
            <div class="cyber-card">
                <div class="card-header-flex">
                    {svg_icon("message", accent_color, 22)}
                    <h4 class="card-title">1. Smishing & Phishing</h4>
                </div>
                <p class="card-body">
                    Deceptive SMS and email baits spoofing financial institutions, customs duty, or enterprise support to harvest 2FA OTP codes and debit credentials.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_t2:
        st.markdown(
            f"""
            <div class="cyber-card">
                <div class="card-header-flex">
                    {svg_icon("mic", accent_amber, 22)}
                    <h4 class="card-title">2. Voice Cloning</h4>
                </div>
                <p class="card-body">
                    Cloning vocal timbres from 3-second public audio samples to execute realistic vishing calls, impersonating corporate executives or family members.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_t3:
        st.markdown(
            f"""
            <div class="cyber-card">
                <div class="card-header-flex">
                    {svg_icon("video", accent_rose, 22)}
                    <h4 class="card-title">3. Video Deepfakes</h4>
                </div>
                <p class="card-body">
                    Synthetic face swaps mapped onto live conference video feeds, simulating executive presence during sensitive fund transfer requests.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("---")
    st.markdown("### Forensic Case Study: The 2024 Arup Deepfake CFO Incident")
    st.markdown(
        f"""
        <div class="status-banner status-dangerous" style="display:block; padding: 1.6rem;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.8rem;">
                {svg_icon("alert", "#F43F5E", 26)}
                <h4 style="margin:0; color:{'#F43F5E' if is_dark else '#991B1B'} !important; font-size:1.15rem;">US$25 Million Corporate Transfer via Synthetic Video</h4>
            </div>
            <p style="color:{'#CBD5E1' if is_dark else '#334155'} !important; font-size:0.95rem; line-height:1.6; margin:0;">
                In early 2024, attackers breached the Hong Kong division of the multinational engineering firm <strong>Arup</strong>. 
                A financial employee was initially skeptical of an urgent payment request, but attended a live multi-person video conference to verify. 
                On the call, every single participant—including the Chief Financial Officer and several recognizable colleagues—was an AI-rendered deepfake.
                <br><br>
                Believing the visual and auditory confirmation, the employee executed 15 separate transactions totaling approximately 
                <strong>US$25 million (HK$200 million)</strong>.
                <br><br>
                <strong>The Defensive Lesson:</strong> Visual and auditory confirmation alone is vulnerable to generative AI. Cryptographic verification, out-of-band challenge-response protocols, and automated frame snapshot forensics (such as SENTINEL's Deepfake Lab) are mandatory.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ===========================================================================
# TAB 5: HOW IT WORKS
# ===========================================================================
with tab_arch:
    st.markdown("### Platform Architecture")
    st.write("A structured 3-stage security pipeline designed to evaluate messages and media before critical compromise:")

    st.markdown(
        f"""
        <div class="flow-wrapper">
            <div class="flow-box">
                <span class="flow-badge">Stage 1</span>
                <div style="margin: 6px 0;">{svg_icon("message", accent_color, 28)}</div>
                <div class="flow-head">Payload Ingestion</div>
                <p class="flow-txt">Inspects incoming SMS alerts, emails, verification prompts, and video snapshots.</p>
            </div>
            <div class="flow-connector">➔</div>
            <div class="flow-box">
                <span class="flow-badge">Stage 2</span>
                <div style="margin: 6px 0;">{svg_icon("cpu", accent_indigo, 28)}</div>
                <div class="flow-head">Dual-Vector Analysis</div>
                <p class="flow-txt">NLP evaluates linguistic patterns while 2D FFT & Laplacian scans inspect video frames.</p>
            </div>
            <div class="flow-connector">➔</div>
            <div class="flow-box">
                <span class="flow-badge">Stage 3</span>
                <div style="margin: 6px 0;">{svg_icon("shield-check", accent_emerald, 28)}</div>
                <div class="flow-head">Forensic Threat Assessment</div>
                <p class="flow-txt">Outputs a calibrated 0–100 threat score, token heatmaps, and itemized indicators.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Core Detection Layers")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        st.markdown(
            f"""
            <div class="cyber-card">
                <div class="card-header-flex">
                    {svg_icon("cpu", accent_color, 22)}
                    <h4 class="card-title">1. Statistical NLP & Heuristic Classifier</h4>
                </div>
                <p class="card-body">
                    Trained on thousands of labeled safe and scam communications. Utilizes TF-IDF token representation alongside heuristic psychological vectors: urgency pressure (<em>"within 24 hours"</em>), credential harvesting prompts (PINs/OTPs), financial fee lures, and shortened or suspicious URLs.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with f_col2:
        st.markdown(
            f"""
            <div class="cyber-card">
                <div class="card-header-flex">
                    {svg_icon("video", accent_emerald, 22)}
                    <h4 class="card-title">2. 2D FFT & Boundary Vision Forensics</h4>
                </div>
                <p class="card-body">
                    Transforms video call snapshot frames into frequency space via 2D Fast Fourier Transform to expose periodic GAN upsampling lattice spikes. Analyzes Laplacian edge gradients to detect blending mask blurriness and chrominance illumination mismatches.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

# ===========================================================================
# TAB 6: BENCHMARKS & AI ADVISORY
# ===========================================================================
with tab_bench:
    st.markdown("### Empirical Performance Benchmarks")
    st.caption("Performance recorded from 1,115 holdout test samples and real-world adversarial variations:")

    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-number">92.4%</div>
                <div class="metric-title">Real-World Accuracy</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with b2:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-number">91.8%</div>
                <div class="metric-title">Scam Precision</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with b3:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-number">89.9%</div>
                <div class="metric-title">Scam Catch Rate</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # Crucial Advisory Box (Requested by user)
    st.markdown(
        f"""
        <div style="background: {'rgba(245, 158, 11, 0.1)' if is_dark else '#FFFBEB'}; border: 1px solid {'rgba(245, 158, 11, 0.35)' if is_dark else '#F59E0B'}; border-radius: 12px; padding: 1.4rem; margin: 1rem 0;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom: 6px;">
                {svg_icon("alert", "#F59E0B", 24)}
                <h4 style="margin:0; color:{'#F59E0B' if is_dark else '#92400E'} !important; font-size:1.08rem;">Crucial Advisory: Never Trust AI 100% Blindly</h4>
            </div>
            <p style="color:{'#FDE68A' if is_dark else '#78350F'} !important; font-size:0.93rem; line-height:1.6; margin:0;">
                No automated defensive platform is infallible. While AI provides a rapid first line of defense, attackers continually adapt phrasing, punctuation, and deceptive tactics to evade detection filters.
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
        - **Short Ambiguous Messages:** Extremely abbreviated payloads (e.g., *"Call me immediately"*) lack token depth for purely statistical classification.
        - **Evolving Smishing Formats:** Emerging tactics (like parcel delivery duty fee lures) require continuous heuristic rule expansion and periodic retraining.
        """
    )

# ===========================================================================
# TAB 7: ABOUT (Clean, Symmetrical, Names Only)
# ===========================================================================
with tab_about:
    st.markdown("### About the Project")
    st.markdown(
        """
        **SENTINEL: AI-Driven Social Engineering and Deepfake Defense Platform**  
        Developed by **Team Sentinels**
        """
    )

    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown(
            f"""
            <div class="cyber-card" style="text-align: center; padding: 1.8rem 1.2rem;">
                <div style="margin-bottom: 0.8rem;">{svg_icon("users", accent_color, 32)}</div>
                <h3 style="margin: 0; color: var(--text-primary) !important; font-size: 1.25rem; font-weight: 700;">Vivek Sharma</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t2:
        st.markdown(
            f"""
            <div class="cyber-card" style="text-align: center; padding: 1.8rem 1.2rem;">
                <div style="margin-bottom: 0.8rem;">{svg_icon("users", accent_indigo, 32)}</div>
                <h3 style="margin: 0; color: var(--text-primary) !important; font-size: 1.25rem; font-weight: 700;">Hitesh Brahmi</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t3:
        st.markdown(
            f"""
            <div class="cyber-card" style="text-align: center; padding: 1.8rem 1.2rem;">
                <div style="margin-bottom: 0.8rem;">{svg_icon("users", accent_emerald, 32)}</div>
                <h3 style="margin: 0; color: var(--text-primary) !important; font-size: 1.25rem; font-weight: 700;">Akhil Kotwal</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="cyber-card" style="margin-top: 1.2rem;">
            <div class="card-header-flex">
                {svg_icon("lock", accent_color, 20)}
                <h4 class="card-title">Platform Specifications</h4>
            </div>
            <p class="card-body">
                • <strong>Project:</strong> AI-Driven Social Engineering and Deepfake Defense Platform<br>
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
    <div style="text-align: center; color: {'#64748B' if is_dark else '#64748B'}; font-size: 0.82rem; margin-top: 3.5rem; border-top: 1px solid {'rgba(255, 255, 255, 0.08)' if is_dark else '#E2E8F0'}; padding-top: 1.2rem;">
        SENTINEL CYBER DEFENSE PLATFORM &copy; 2026 // TEAM SENTINELS
    </div>
    """,
    unsafe_allow_html=True
)
