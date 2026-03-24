"""
Reusable UI components — glassmorphism cards, gauges, badges.
"""

from __future__ import annotations
import streamlit as st
from ui.theme import COLORS


def metric_card(label: str, value: str, delta: str = "", delta_color: str = "", icon: str = ""):
    """Render a premium glassmorphism metric card."""
    delta_html = ""
    if delta:
        color = delta_color or ("#00E676" if delta.startswith("+") or delta.startswith("▲") else "#FF1744")
        delta_html = f'<div class="metric-delta" style="color: {color};">{delta}</div>'

    icon_html = f'<div style="font-size:1.5rem; margin-bottom:4px;">{icon}</div>' if icon else ""

    st.markdown(f"""
    <div class="metric-card">
        {icon_html}
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def score_gauge(score: float, label: str, max_score: float = 100):
    """Render a circular score gauge."""
    pct = min(score / max_score, 1.0)

    if pct >= 0.7:
        color = COLORS["danger"]
    elif pct >= 0.5:
        color = COLORS["accent"]
    elif pct >= 0.3:
        color = COLORS["warning"]
    else:
        color = COLORS["success"]

    # CSS conic-gradient gauge
    angle = int(pct * 360)
    st.markdown(f"""
    <div style="text-align: center;">
        <div class="score-ring" style="
            background: conic-gradient(
                {color} 0deg,
                {color} {angle}deg,
                rgba(255,255,255,0.05) {angle}deg,
                rgba(255,255,255,0.05) 360deg
            );
        ">
            <div style="
                width: 110px; height: 110px; border-radius: 50%;
                background: #0E1117;
                display: flex; align-items: center; justify-content: center;
                flex-direction: column;
            ">
                <div class="score-value" style="color: {color};">{score:.0f}</div>
            </div>
        </div>
        <div class="score-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def status_badge(text: str, variant: str = "info"):
    """Render a status badge. Variants: danger, warning, success, info."""
    st.markdown(f'<span class="badge badge-{variant}">{text}</span>', unsafe_allow_html=True)


def glass_container(content: str):
    """Wrap content in a glassmorphism container."""
    st.markdown(f'<div class="glass-card">{content}</div>', unsafe_allow_html=True)


def section_header(title: str, icon: str = ""):
    """Render a styled section header."""
    st.markdown(f'<div class="section-header">{icon} {title}</div>', unsafe_allow_html=True)


def hero_banner(title: str, subtitle: str):
    """Render a hero gradient banner."""
    st.markdown(f"""
    <div class="hero-gradient">
        <h1 style="margin:0; font-weight:900; font-size:2.2rem;">{title}</h1>
        <p style="margin:8px 0 0 0; opacity:0.8; font-size:1.1rem; font-weight:400;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def sentiment_badge(sentiment: str, score: float = 0):
    """Render a sentiment badge with color."""
    if sentiment == "POSITIVE":
        variant = "success"
        icon = "📈"
    elif sentiment == "NEGATIVE":
        variant = "danger"
        icon = "📉"
    else:
        variant = "info"
        icon = "📊"

    score_text = f" ({score:+.2f})" if score else ""
    st.markdown(
        f'<span class="badge badge-{variant}">{icon} {sentiment}{score_text}</span>',
        unsafe_allow_html=True
    )


def panic_level_indicator(level: str, score: float, color: str):
    """Render a panic level indicator with animated pulse for high levels."""
    pulse_class = "pulse-alert" if score >= 70 else ""
    st.markdown(f"""
    <div class="glass-card {pulse_class}" style="
        text-align: center;
        border-color: {color}33;
    ">
        <div style="font-size: 3rem; font-weight: 900; color: {color};">{score:.0f}</div>
        <div style="font-size: 1rem; font-weight: 700; color: {color}; text-transform: uppercase;
            letter-spacing: 2px; margin-top: 4px;">{level}</div>
        <div style="font-size: 0.8rem; opacity: 0.6; margin-top: 8px;">Panic Score (0-100)</div>
    </div>
    """, unsafe_allow_html=True)


def format_inr(value: float) -> str:
    """Format a number in Indian Rupee style with commas."""
    if value >= 10000000:
        return f"₹{value / 10000000:.2f} Cr"
    elif value >= 100000:
        return f"₹{value / 100000:.2f} L"
    elif value >= 1000:
        return f"₹{value:,.0f}"
    else:
        return f"₹{value:.2f}"


def format_market_cap(value: float) -> str:
    """Format market cap for display."""
    if not value or value == 0:
        return "N/A"
    if value >= 1e12:
        return f"₹{value / 1e12:.2f}T"
    elif value >= 1e9:
        return f"₹{value / 1e9:.2f}B"
    elif value >= 1e7:
        return f"₹{value / 1e7:.2f}Cr"
    else:
        return f"₹{value:,.0f}"
