"""
🐑 Herd Detector — CCK Model herding analysis for Indian stock sectors.
"""

import streamlit as st

st.set_page_config(page_title="Herd Detector | SheepOrSleep", page_icon="🐑", layout="wide")

from ui.theme import get_custom_css, COLORS, PLOTLY_DARK_TEMPLATE
from ui.components import (
    metric_card, section_header, hero_banner, score_gauge,
    status_badge, glass_container,
)
from config.stock_universe import get_all_sectors, get_sector_symbols
from analytics.herd_detector import HerdDetector
from ai.groq_client import GroqClient
from ai.nudge_engine import NudgeEngine

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ── Header ──
hero_banner(
    "🐑 Herd Detector",
    "Detect herding behavior using the Chang, Cheng & Khorana (CCK) econometric model — Are investors following the crowd?"
)

# ── Parameters ──
col_p1, col_p2 = st.columns(2)
with col_p1:
    selected_sector = st.selectbox("Select Sector for Analysis", get_all_sectors(), index=0)
with col_p2:
    lookback = st.selectbox(
        "Lookback Period",
        ["6 Months", "1 Year", "2 Years"],
        index=1,
    )
    period_map = {"6 Months": 180, "1 Year": 365, "2 Years": 730}
    period_days = period_map[lookback]

# ── Run Analysis ──
if st.button("🔍 Analyze Herding", type="primary", use_container_width=True):
    with st.spinner(f"Analyzing herding in {selected_sector} sector..."):
        detector = HerdDetector(period_days=period_days)
        result = detector.analyze_sector(selected_sector)

    if "error" in result:
        st.error(result["error"])
    else:
        reg = result["regression"]
        csad_df = result["csad_df"]
        rolling = result["rolling_intensity"]

        # ── Key Metrics ──
        section_header("Herding Analysis Results", "📊")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            score_gauge(
                reg["herding_intensity"],
                "Herding Intensity",
            )
        with col2:
            metric_card(
                label="γ₂ Coefficient",
                value=f"{reg['gamma2']:.6f}",
                delta="Negative → Herding" if reg['gamma2'] < 0 else "Non-negative → No Herding",
                delta_color=COLORS["danger"] if reg['gamma2'] < 0 else COLORS["success"],
            )
        with col3:
            metric_card(
                label="P-value",
                value=f"{reg['gamma2_pvalue']:.4f}",
                delta="Significant (< 0.05)" if reg['gamma2_pvalue'] < 0.05 else "Not Significant",
                delta_color=COLORS["danger"] if reg['gamma2_pvalue'] < 0.05 else COLORS["success"],
            )
        with col4:
            metric_card(
                label="Model R²",
                value=f"{reg['r_squared']:.4f}",
                delta=f"Observations: {reg['n_observations']}",
                delta_color=COLORS["info"],
            )

        # ── Herding Status Banner ──
        if reg["herding_detected"]:
            st.markdown(f"""
            <div class="glass-card pulse-alert" style="border-color: {COLORS['danger']}33; text-align: center;">
                <div style="font-size: 1.5rem;">🚨</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: {COLORS['danger']};">
                    HERDING DETECTED in {selected_sector}
                </div>
                <div style="font-size: 0.85rem; opacity: 0.7; margin-top: 6px;">
                    γ₂ = {reg['gamma2']:.6f} (p = {reg['gamma2_pvalue']:.4f}) — Return dispersion decreases
                    during extreme market moves, indicating investors are ignoring private information.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="glass-card" style="border-color: {COLORS['success']}33; text-align: center;">
                <div style="font-size: 1.5rem;">✅</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: {COLORS['success']};">
                    NO HERDING in {selected_sector}
                </div>
                <div style="font-size: 0.85rem; opacity: 0.7; margin-top: 6px;">
                    Return dispersion follows rational expectations — investors appear to be
                    making independent decisions.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── CSAD vs Market Return Scatter ──
        section_header("CSAD vs Market Return — Quadratic Regression", "📈")

        fig = go.Figure()

        # Scatter plot
        fig.add_trace(go.Scatter(
            x=csad_df["Abs_Market_Return"],
            y=csad_df["CSAD"],
            mode="markers",
            marker=dict(
                size=5,
                color=csad_df["Market_Return"],
                colorscale="RdYlGn",
                showscale=True,
                colorbar=dict(title="Mkt Return"),
                opacity=0.6,
            ),
            name="Daily CSAD",
        ))

        # Fitted quadratic curve
        if len(reg["y_pred"]) > 0:
            sorted_idx = np.argsort(csad_df["Abs_Market_Return"].values)
            fig.add_trace(go.Scatter(
                x=csad_df["Abs_Market_Return"].values[sorted_idx],
                y=reg["y_pred"][sorted_idx],
                mode="lines",
                line=dict(color=COLORS["accent"], width=3),
                name=f"Fitted: CSAD = {reg['alpha']:.4f} + {reg['gamma1']:.4f}|Rm| + ({reg['gamma2']:.4f})Rm²",
            ))

        fig.update_layout(
            **PLOTLY_DARK_TEMPLATE["layout"],
            height=450,
            title=dict(text="CSAD vs |Market Return| — CCK Quadratic Model", font=dict(size=14)),
            xaxis_title="|Market Return|",
            yaxis_title="CSAD",
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Rolling Herding Intensity ──
        if not rolling.empty:
            section_header("Rolling Herding Intensity Over Time", "⏱️")

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=rolling.index,
                y=rolling.values,
                fill="tozeroy",
                fillcolor="rgba(255, 23, 68, 0.15)",
                line=dict(color=COLORS["danger"], width=2),
                name="Herding Intensity",
            ))
            fig2.add_hline(y=50, line_dash="dash", line_color=COLORS["warning"],
                          annotation_text="High Herding Threshold", annotation_position="top right")

            fig2.update_layout(
                **PLOTLY_DARK_TEMPLATE["layout"],
                height=350,
                title=dict(text=f"Rolling {detector.window}-Day Herding Intensity", font=dict(size=13)),
                yaxis_title="Intensity (0-100)",
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ── AI Insight ──
        groq = GroqClient()
        if groq.is_available and reg["herding_detected"]:
            section_header("🤖 AI Analysis", "")
            with st.spinner("Generating AI insight..."):
                nudge = NudgeEngine(groq)
                insight = nudge.generate_herding_alert(
                    selected_sector,
                    reg["herding_intensity"],
                    reg["gamma2"],
                )
                st.markdown(f'<div class="glass-card">{insight}</div>', unsafe_allow_html=True)

        # ── CCK Model Explanation ──
        with st.expander("📖 Understanding the CCK Model"):
            st.markdown("""
            ### The Chang, Cheng & Khorana (CCK) Model

            The CCK model tests whether individual stock returns converge during extreme market moves.

            **Regression Equation:**

            `CSAD_t = α + γ₁|R_m,t| + γ₂(R_m,t)² + ε_t`

            **Interpretation:**
            - **γ₂ < 0 and significant** → **Herding confirmed**. During large market swings,
              individual returns cluster around the market mean more than expected.
            - **γ₂ ≥ 0** → No herding. Return dispersion follows rational asset pricing predictions.

            **CSAD** (Cross-Sectional Absolute Deviation) measures how spread out individual stock
            returns are from the market average on any given day.

            **In Indian markets**, herding is most pronounced in:
            - Capital Goods and IT sectors (strong herding)
            - Banking sector (more independent decision-making)
            """)

# ── Cross-Sector Comparison ──
st.markdown("<br>", unsafe_allow_html=True)
section_header("Cross-Sector Herding Comparison", "🔥")

if st.button("🗺️ Run Cross-Sector Scan", key="cross_sector"):
    with st.spinner("Scanning all sectors (this may take a moment)..."):
        detector = HerdDetector(period_days=365)
        comparison = detector.cross_sector_comparison()

    if not comparison.empty:
        # Heatmap bar
        fig3 = go.Figure()
        colors_bar = [
            COLORS["danger"] if row["Herding Detected"] == "✅ Yes" else COLORS["success"]
            for _, row in comparison.iterrows()
        ]
        fig3.add_trace(go.Bar(
            x=comparison["Sector"],
            y=comparison["Intensity (0-100)"],
            marker_color=colors_bar,
            text=comparison["Herding Detected"],
            textposition="outside",
        ))
        fig3.update_layout(
            **PLOTLY_DARK_TEMPLATE["layout"],
            height=400,
            title=dict(text="Herding Intensity by Sector", font=dict(size=14)),
            yaxis_title="Herding Intensity (0-100)",
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.dataframe(comparison, hide_index=True, use_container_width=True)
    else:
        st.warning("Insufficient data for cross-sector comparison.")
