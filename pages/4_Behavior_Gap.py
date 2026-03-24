"""
📉 Behavior Gap — Monte Carlo SIP vs Panic simulation & behavior gap analysis.
"""

import streamlit as st

st.set_page_config(page_title="Behavior Gap | SheepOrSleep", page_icon="📉", layout="wide")

from ui.theme import get_custom_css, COLORS, PLOTLY_DARK_TEMPLATE
from ui.components import (
    metric_card, section_header, hero_banner, format_inr, score_gauge,
)
from config.stock_universe import get_display_options, symbol_from_display
from analytics.behavior_gap import BehaviorGapCalculator
from analytics.portfolio_simulator import PortfolioSimulator
from ai.groq_client import GroqClient
from ai.nudge_engine import NudgeEngine

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

st.markdown(get_custom_css(), unsafe_allow_html=True)

hero_banner(
    "📉 Behavior Gap Analyzer",
    "Quantify the financial cost of emotional investing — SIP discipline vs. panic selling through Monte Carlo simulation"
)

# ── Stock Selection & Parameters ──
col1, col2, col3, col4 = st.columns(4)

with col1:
    display_opts = get_display_options()
    default_idx = 0
    if "selected_display" in st.session_state:
        try:
            default_idx = display_opts.index(st.session_state["selected_display"])
        except ValueError:
            default_idx = 0
    selected = st.selectbox("Select Stock", display_opts, index=default_idx, key="bg_stock")
    symbol = symbol_from_display(selected)

with col2:
    sim_years = st.slider("Simulation Period (Years)", 3, 20, 10, key="sim_years")

with col3:
    sip_amount = st.number_input("Monthly SIP (₹)", 1000, 100000, 10000, step=1000, key="sip_amt")

with col4:
    n_simulations = st.selectbox("Simulations", [100, 500, 1000], index=1, key="n_sims")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tab Layout ──
tab1, tab2, tab3 = st.tabs(["🎲 Monte Carlo Simulation", "📅 Missing Best Days", "📊 Behavior Gap"])

# ══════════════════════════════════════════════════════
# TAB 1: Monte Carlo SIP vs Panic Seller
# ══════════════════════════════════════════════════════
with tab1:
    if st.button("🎲 Run Monte Carlo Simulation", type="primary", use_container_width=True, key="run_mc"):
        with st.spinner(f"Running {n_simulations} simulations over {sim_years} years..."):
            simulator = PortfolioSimulator(n_simulations=n_simulations, sip_amount=sip_amount)
            results = simulator.simulate_sip_vs_panic(symbol, years=sim_years)

        # ── Results Summary ──
        section_header("Simulation Results", "💰")

        cost = results["cost_of_panic"]

        # Hero stat
        st.markdown(f"""
        <div class="hero-gradient" style="text-align: center;">
            <div style="font-size: 0.9rem; opacity: 0.7; text-transform: uppercase; letter-spacing: 2px;">
                The Cost of Panic Selling
            </div>
            <div style="font-size: 3rem; font-weight: 900; color: {COLORS['danger']}; margin: 8px 0;">
                {format_inr(cost['mean_loss'])}
            </div>
            <div style="font-size: 1.1rem; opacity: 0.8;">
                Average wealth destroyed by emotional decisions over {sim_years} years
            </div>
            <div style="font-size: 0.85rem; opacity: 0.6; margin-top: 8px;">
                SIP beats Panic Seller in <b>{cost['win_rate']}%</b> of {n_simulations} scenarios
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            metric_card(
                "Total Invested",
                format_inr(results["total_invested"]),
                f"₹{sip_amount:,}/month × {sim_years}yr",
                COLORS["info"],
                icon="💵",
            )
        with col_m2:
            metric_card(
                "SIP Median Wealth",
                format_inr(results["sip"]["median"]),
                f"Range: {format_inr(results['sip']['p10'])} – {format_inr(results['sip']['p90'])}",
                COLORS["success"],
                icon="📈",
            )
        with col_m3:
            metric_card(
                "Panic Median Wealth",
                format_inr(results["panic"]["median"]),
                f"Range: {format_inr(results['panic']['p10'])} – {format_inr(results['panic']['p90'])}",
                COLORS["danger"],
                icon="📉",
            )
        with col_m4:
            metric_card(
                "Wealth Reduction",
                f"{cost['pct_loss']:.1f}%",
                f"Median gap: {format_inr(cost['median_loss'])}",
                COLORS["accent"],
                icon="💸",
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Distribution Comparison ──
        section_header("Wealth Distribution Comparison", "📊")

        fig_dist = go.Figure()

        fig_dist.add_trace(go.Histogram(
            x=results["sip"]["all_results"],
            name="Disciplined SIP",
            opacity=0.7,
            marker_color=COLORS["success"],
            nbinsx=50,
        ))
        fig_dist.add_trace(go.Histogram(
            x=results["panic"]["all_results"],
            name="Panic Seller",
            opacity=0.7,
            marker_color=COLORS["danger"],
            nbinsx=50,
        ))

        fig_dist.add_vline(x=results["sip"]["median"], line_dash="dash",
                          line_color=COLORS["success"], annotation_text="SIP Median")
        fig_dist.add_vline(x=results["panic"]["median"], line_dash="dash",
                          line_color=COLORS["danger"], annotation_text="Panic Median")

        fig_dist.update_layout(
            **PLOTLY_DARK_TEMPLATE["layout"],
            height=400,
            title=dict(text=f"Final Wealth Distribution — {n_simulations} Monte Carlo Simulations", font=dict(size=14)),
            xaxis_title="Final Portfolio Value (₹)",
            yaxis_title="Frequency",
            barmode="overlay",
        )
        st.plotly_chart(fig_dist, use_container_width=True)

        # ── Comparison Table ──
        section_header("Detailed Comparison", "📋")

        comp_data = {
            "Metric": ["Mean Wealth", "Median Wealth", "10th Percentile (Worst)", "90th Percentile (Best)", "Minimum", "Maximum"],
            "Disciplined SIP (₹)": [
                f"{results['sip']['mean']:,.0f}",
                f"{results['sip']['median']:,.0f}",
                f"{results['sip']['p10']:,.0f}",
                f"{results['sip']['p90']:,.0f}",
                f"{results['sip']['min']:,.0f}",
                f"{results['sip']['max']:,.0f}",
            ],
            "Panic Seller (₹)": [
                f"{results['panic']['mean']:,.0f}",
                f"{results['panic']['median']:,.0f}",
                f"{results['panic']['p10']:,.0f}",
                f"{results['panic']['p90']:,.0f}",
                f"{results['panic']['min']:,.0f}",
                f"{results['panic']['max']:,.0f}",
            ],
        }
        st.dataframe(pd.DataFrame(comp_data), hide_index=True, use_container_width=True)

        # ── AI Insight ──
        groq = GroqClient()
        if groq.is_available:
            section_header("🤖 AI SIP Reinforcement", "")
            with st.spinner("Generating AI insight..."):
                nudge = NudgeEngine(groq)
                insight = nudge.generate_sip_reinforcement(results)
                st.markdown(f'<div class="glass-card">{insight}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# TAB 2: Missing Best Days Impact
# ══════════════════════════════════════════════════════
with tab2:
    section_header("Impact of Missing the Best Market Days", "📅")

    st.markdown("""
    <div class="glass-card">
        <b>Key Insight:</b> Panic sellers who exit during crashes often miss the subsequent recovery rallies.
        Missing just 10 of the best trading days in a decade can reduce returns by over 50%.
    </div>
    """, unsafe_allow_html=True)

    years_lookup = st.slider("Analysis Period (Years)", 3, 15, 10, key="miss_years")
    initial_inv = st.number_input("Initial Investment (₹)", 10000, 10000000, 100000, step=10000, key="miss_inv")

    if st.button("📅 Calculate Impact", type="primary", use_container_width=True, key="run_miss"):
        with st.spinner("Analyzing historical data..."):
            calc = BehaviorGapCalculator()
            impact_df = calc.compute_missing_best_days_impact(symbol, years_lookup, initial_inv)

        if not impact_df.empty:
            # Impact table
            st.dataframe(impact_df, hide_index=True, use_container_width=True)

            # Bar chart
            fig_miss = go.Figure()
            colors_miss = [COLORS["success"]] + [COLORS["danger"]] * (len(impact_df) - 1)
            fig_miss.add_trace(go.Bar(
                x=impact_df["Scenario"],
                y=impact_df["Final Value (₹)"],
                marker_color=colors_miss,
                text=impact_df["Total Return (%)"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
            ))
            fig_miss.update_layout(
                **PLOTLY_DARK_TEMPLATE["layout"],
                height=400,
                title=dict(text=f"Final Wealth by Scenario — {format_inr(initial_inv)} invested", font=dict(size=14)),
                yaxis_title="Final Value (₹)",
                xaxis_tickangle=-15,
            )
            st.plotly_chart(fig_miss, use_container_width=True)

            # Reduction chart
            fig_red = go.Figure()
            fig_red.add_trace(go.Bar(
                x=impact_df["Scenario"][1:],
                y=impact_df["% Reduction"][1:],
                marker_color=COLORS["accent"],
                text=impact_df["% Reduction"][1:].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
            ))
            fig_red.update_layout(
                **PLOTLY_DARK_TEMPLATE["layout"],
                height=300,
                title=dict(text="% Wealth Reduction from Missing Best Days", font=dict(size=13)),
                yaxis_title="Reduction (%)",
            )
            st.plotly_chart(fig_red, use_container_width=True)
        else:
            st.warning("Insufficient historical data for this analysis.")


# ══════════════════════════════════════════════════════
# TAB 3: Behavior Gap Estimation
# ══════════════════════════════════════════════════════
with tab3:
    section_header("Your Behavior Gap", "📊")

    st.markdown("""
    <div class="glass-card">
        <b>What is the Behavior Gap?</b> It's the difference between the investment's actual return
        and what the average investor earns — caused by buying high (FOMO) and selling low (panic).
        Studies show this gap costs Indian investors 2-4% CAGR annually.
    </div>
    """, unsafe_allow_html=True)

    gap_years = st.slider("Analysis Period (Years)", 2, 10, 5, key="gap_years")

    if st.button("📊 Calculate Behavior Gap", type="primary", use_container_width=True, key="run_gap"):
        with st.spinner("Computing behavior gap..."):
            calc = BehaviorGapCalculator()
            gap = calc.compute_behavior_gap(symbol, gap_years)

        if gap:
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                metric_card(
                    "Investment CAGR",
                    f"{gap['investment_cagr']:.2f}%",
                    "What the stock actually returned",
                    COLORS["success"],
                    icon="📈",
                )
            with col_g2:
                metric_card(
                    "Estimated Investor CAGR",
                    f"{gap['estimated_investor_cagr']:.2f}%",
                    "What the average investor earned",
                    COLORS["warning"],
                    icon="👤",
                )
            with col_g3:
                gap_color = COLORS["danger"] if gap["behavior_gap"] > 2 else COLORS["warning"]
                metric_card(
                    "Behavior Gap",
                    f"{gap['behavior_gap']:.2f}%",
                    gap["gap_interpretation"],
                    gap_color,
                    icon="📉",
                )

            # Visualize gap
            fig_gap = go.Figure()
            fig_gap.add_trace(go.Bar(
                x=["Investment Return", "Investor Return", "Behavior Gap"],
                y=[gap["investment_cagr"], gap["estimated_investor_cagr"], gap["behavior_gap"]],
                marker_color=[COLORS["success"], COLORS["warning"], COLORS["danger"]],
                text=[f"{gap['investment_cagr']:.2f}%", f"{gap['estimated_investor_cagr']:.2f}%", f"{gap['behavior_gap']:.2f}%"],
                textposition="outside",
            ))
            fig_gap.update_layout(
                **PLOTLY_DARK_TEMPLATE["layout"],
                height=350,
                title=dict(text=f"Behavior Gap — {selected.split('(')[0].strip()}", font=dict(size=14)),
                yaxis_title="CAGR (%)",
            )
            st.plotly_chart(fig_gap, use_container_width=True)

            # Cost translation
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 0.85rem; opacity: 0.6; text-transform: uppercase; letter-spacing: 1.5px;">
                    10-Year Cost of Behavior Gap on ₹10,00,000
                </div>
                <div style="font-size: 2.5rem; font-weight: 900; color: {COLORS['danger']}; margin: 8px 0;">
                    {format_inr(1000000 * ((1 + gap['investment_cagr']/100)**10 - (1 + gap['estimated_investor_cagr']/100)**10))}
                </div>
                <div style="font-size: 0.85rem; opacity: 0.6;">
                    This is how much emotional decisions cost over a decade
                </div>
            </div>
            """, unsafe_allow_html=True)

            # AI Insight
            groq = GroqClient()
            if groq.is_available:
                section_header("🤖 AI Behavioral Insight", "")
                with st.spinner("Generating insight..."):
                    nudge = NudgeEngine(groq)
                    insight = nudge.generate_behavior_gap_insight(gap)
                    st.markdown(f'<div class="glass-card">{insight}</div>', unsafe_allow_html=True)
        else:
            st.warning("Insufficient data for behavior gap analysis.")

        # DCA Analysis
        section_header("DCA (Rupee-Cost Averaging) Performance", "💰")
        with st.spinner("Computing DCA performance..."):
            calc2 = BehaviorGapCalculator()
            dca = calc2.compute_worst_timing_analysis(symbol, gap_years, sip_amount)

        if dca:
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                metric_card("Total Invested", format_inr(dca["total_invested"]), icon="💵")
            with col_d2:
                metric_card("DCA Final Value", format_inr(dca["dca_final_value"]),
                           f"Return: {dca['dca_return_pct']:+.2f}%",
                           COLORS["success"] if dca["dca_return_pct"] > 0 else COLORS["danger"],
                           icon="📈")
            with col_d3:
                metric_card("Months Invested", str(dca["n_months"]), icon="📅")

            # DCA curve
            if "dca_curve" in dca and dca["dca_curve"] is not None:
                fig_dca = go.Figure()
                fig_dca.add_trace(go.Scatter(
                    x=dca["dca_curve"].index,
                    y=dca["dca_curve"].values,
                    fill="tozeroy",
                    fillcolor="rgba(0, 230, 118, 0.1)",
                    line=dict(color=COLORS["success"], width=2),
                    name="DCA Portfolio Value",
                ))

                # Invested amount line
                invested_monthly = [sip_amount * (i+1) for i in range(len(dca["dca_curve"]))]
                fig_dca.add_trace(go.Scatter(
                    x=dca["dca_curve"].index,
                    y=invested_monthly,
                    line=dict(color=COLORS["muted"], width=1, dash="dash"),
                    name="Amount Invested",
                ))

                fig_dca.update_layout(
                    **PLOTLY_DARK_TEMPLATE["layout"],
                    height=350,
                    title=dict(text="DCA Portfolio Growth Over Time", font=dict(size=13)),
                    yaxis_title="Value (₹)",
                )
                st.plotly_chart(fig_dca, use_container_width=True)
