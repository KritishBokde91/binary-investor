"""
🚨 Panic Scanner — Multi-factor panic selling detection.
"""

import streamlit as st

st.set_page_config(page_title="Panic Scanner | SheepOrSleep", page_icon="🚨", layout="wide")

from ui.theme import get_custom_css, COLORS, PLOTLY_DARK_TEMPLATE
from ui.components import (
    metric_card, section_header, hero_banner, panic_level_indicator,
    score_gauge, format_inr,
)
from config.stock_universe import (
    get_display_options, symbol_from_display,
    get_all_sectors, get_sector_symbols, STOCK_UNIVERSE,
)
from analytics.panic_detector import PanicDetector
from ai.groq_client import GroqClient
from ai.nudge_engine import NudgeEngine
from ai.sentiment_analyzer import SentimentAnalyzer

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

st.markdown(get_custom_css(), unsafe_allow_html=True)

hero_banner("🚨 Panic Scanner", "Detect panic selling signals using volume spikes, price-volume divergence & AI sentiment analysis")

# ── Stock Selection ──
col_sel1, col_sel2 = st.columns([3, 1])
with col_sel1:
    display_opts = get_display_options()
    default_idx = 0
    if "selected_display" in st.session_state:
        try:
            default_idx = display_opts.index(st.session_state["selected_display"])
        except ValueError:
            default_idx = 0
    selected = st.selectbox("Select Stock", display_opts, index=default_idx, key="panic_stock")
    symbol = symbol_from_display(selected)

with col_sel2:
    scan_period = st.selectbox("Period", ["1 Month", "3 Months", "6 Months"], index=1, key="panic_period")
    period_map = {"1 Month": 30, "3 Months": 90, "6 Months": 180}
    period_days = period_map[scan_period]


if st.button("🚨 Run Panic Analysis", type="primary", use_container_width=True):
    with st.spinner(f"Scanning {selected} for panic signals..."):
        detector = PanicDetector()
        result = detector.compute_panic_score(symbol, period_days)

    # ── Panic Score ──
    section_header("Panic Score", "🎯")

    col1, col2 = st.columns([1, 2])
    with col1:
        panic_level_indicator(result["level"], result["panic_score"], result["color"])

    with col2:
        # Factor breakdown radar
        factors = result["factors"]
        categories = list(factors.keys())
        values = list(factors.values())
        values.append(values[0])  # Close the radar
        categories.append(categories[0])

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(255, 23, 68, 0.15)",
            line=dict(color=COLORS["danger"], width=2),
            name="Panic Factors",
        ))
        fig_radar.update_layout(
            **PLOTLY_DARK_TEMPLATE["layout"],
            height=350,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    visible=True, range=[0, 100],
                    gridcolor="rgba(255,255,255,0.1)",
                ),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            ),
            title=dict(text="Panic Factor Breakdown", font=dict(size=13)),
            showlegend=False,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Factor Details ──
    section_header("Factor Scores", "📊")
    cols = st.columns(5)
    factor_icons = ["📊", "📦", "↕️", "📉", "🌊"]
    factor_colors = [
        COLORS["danger"] if v >= 50 else COLORS["warning"] if v >= 25 else COLORS["success"]
        for v in factors.values()
    ]
    for i, (col, (name, val)) in enumerate(zip(cols, factors.items())):
        with col:
            metric_card(
                label=name,
                value=f"{val:.0f}/100",
                icon=factor_icons[i],
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Volume Analysis ──
    details = result.get("details", {})
    vol_data = details.get("volume_anomaly_data")

    if vol_data is not None and not vol_data.empty:
        section_header("Volume Anomaly Detection", "📊")

        fig_vol = go.Figure()

        # Volume bars
        vol_colors = [
            COLORS["danger"] if panic else (COLORS["warning"] if spike else COLORS["primary"])
            for panic, spike in zip(vol_data["Panic_Volume"], vol_data["Volume_Spike"])
        ]

        fig_vol.add_trace(go.Bar(
            x=vol_data.index,
            y=vol_data["Volume"],
            marker_color=vol_colors,
            name="Volume",
            opacity=0.7,
        ))

        # Z-score overlay
        fig_vol.add_trace(go.Scatter(
            x=vol_data.index,
            y=vol_data["Volume_Zscore"] * vol_data["Volume"].max() / 5,
            mode="lines",
            line=dict(color=COLORS["accent"], width=1.5),
            name="Z-Score (scaled)",
            yaxis="y2",
        ))

        fig_vol.update_layout(
            **PLOTLY_DARK_TEMPLATE["layout"],
            height=400,
            title=dict(text="Volume Analysis — Red bars indicate panic selling volume", font=dict(size=13)),
            yaxis_title="Volume",
            yaxis2=dict(
                title="Z-Score",
                overlaying="y",
                side="right",
                gridcolor="rgba(255,255,255,0.03)",
            ),
            barmode="overlay",
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    # ── Price-Volume Divergence ──
    div_data = details.get("divergence_data")
    if div_data is not None and not div_data.empty:
        section_header("Price-Volume Divergence", "↕️")

        fig_div = go.Figure()

        fig_div.add_trace(go.Scatter(
            x=div_data.index, y=div_data["Price_Mom_5"] * 100,
            mode="lines", line=dict(color=COLORS["info"], width=2),
            name="5D Price Momentum (%)",
        ))
        fig_div.add_trace(go.Scatter(
            x=div_data.index, y=div_data["Vol_Mom_5"] * 100,
            mode="lines", line=dict(color=COLORS["accent"], width=2),
            name="5D Volume Momentum (%)",
        ))

        # Mark divergence points
        panic_points = div_data[div_data["Panic_Divergence"]]
        if not panic_points.empty:
            fig_div.add_trace(go.Scatter(
                x=panic_points.index,
                y=panic_points["Price_Mom_5"] * 100,
                mode="markers",
                marker=dict(color=COLORS["danger"], size=12, symbol="x"),
                name="🚨 Panic Divergence",
            ))

        fig_div.update_layout(
            **PLOTLY_DARK_TEMPLATE["layout"],
            height=350,
            title=dict(text="Price Down + Volume Up = Panic Signal", font=dict(size=13)),
            yaxis_title="Momentum (%)",
        )
        st.plotly_chart(fig_div, use_container_width=True)

    # ── News Sentiment ──
    section_header("News Sentiment", "📰")
    with st.spinner("Analyzing news sentiment..."):
        groq = GroqClient()
        analyzer = SentimentAnalyzer(groq)
        stock_name = selected.split("(")[0].strip()
        sentiment = analyzer.analyze_stock_sentiment(stock_name)

    if sentiment and sentiment.get("headlines"):
        summary = sentiment["summary"]
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            metric_card("Positive", str(summary["positive"]), icon="📈")
        with col_s2:
            metric_card("Negative", str(summary["negative"]), icon="📉")
        with col_s3:
            metric_card("Avg Score", f"{summary['avg_score']:+.2f}", icon="📊")

        # Headlines table
        for h in sentiment["headlines"][:8]:
            sentiment_icon = {"POSITIVE": "🟢", "NEGATIVE": "🔴", "NEUTRAL": "⚪"}.get(h.get("sentiment", ""), "⚪")
            st.markdown(f"{sentiment_icon} **{h['title']}** — *{h.get('source', '')}*")

    # ── AI Nudge ──
    if groq.is_available and result["panic_score"] >= 30:
        section_header("🤖 AI Behavioral Nudge", "")
        with st.spinner("Generating AI insight..."):
            nudge = NudgeEngine(groq)
            insight = nudge.generate_panic_nudge(
                stock_name, result["panic_score"], result["factors"]
            )
            st.markdown(f'<div class="glass-card">{insight}</div>', unsafe_allow_html=True)

# ── Batch Scan ──
st.markdown("<br>", unsafe_allow_html=True)
section_header("Batch Panic Scanner", "🔎")

scan_sector = st.selectbox("Scan Sector", get_all_sectors(), key="batch_sector")

if st.button("🚨 Scan Sector for Panic", key="batch_scan"):
    symbols = get_sector_symbols(scan_sector)
    with st.spinner(f"Scanning {len(symbols)} stocks in {scan_sector}..."):
        detector = PanicDetector()
        scan_df = detector.scan_multiple(symbols)

    if not scan_df.empty:
        st.dataframe(scan_df, hide_index=True, use_container_width=True)

        # Visualize
        fig_batch = go.Figure()
        colors_batch = [
            COLORS["danger"] if s >= 50 else COLORS["warning"] if s >= 25 else COLORS["success"]
            for s in scan_df["Panic Score"]
        ]
        fig_batch.add_trace(go.Bar(
            x=scan_df["Symbol"],
            y=scan_df["Panic Score"],
            marker_color=colors_batch,
            text=scan_df["Level"],
            textposition="outside",
        ))
        fig_batch.update_layout(
            **PLOTLY_DARK_TEMPLATE["layout"],
            height=400,
            title=dict(text=f"Panic Scores — {scan_sector} Sector", font=dict(size=14)),
            yaxis_title="Panic Score (0-100)",
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig_batch, use_container_width=True)
