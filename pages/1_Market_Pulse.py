"""
📊 Market Pulse — Real-time market overview & sector analysis.
"""

import streamlit as st

st.set_page_config(page_title="Market Pulse | SheepOrSleep", page_icon="📊", layout="wide")

from ui.theme import get_custom_css, COLORS, PLOTLY_DARK_TEMPLATE
from ui.components import metric_card, section_header, hero_banner, status_badge
from config.stock_universe import get_all_sectors, get_stocks_by_sector, get_sector_symbols
from data.stock_data import fetch_realtime_quote, fetch_historical_data, fetch_index_data
from data.market_indicators import compute_sector_performance, compute_volatility_regime, compute_market_breadth

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ── Header ──
hero_banner("📊 Market Pulse", "Real-time Indian stock market overview — indices, sectors, breadth & volatility")

# ── Index Performance ──
section_header("Market Indices", "📈")

try:
    indices = fetch_index_data()
    cols = st.columns(3)
    for i, (sym, data) in enumerate(indices.items()):
        with cols[i]:
            change = data.get("change", 0)
            delta_str = f"{'▲' if change >= 0 else '▼'} {abs(change):.2f} ({data.get('change_pct', 0):+.2f}%)"
            metric_card(
                label=data.get("display_name", sym),
                value=f"₹{data.get('price', 0):,.2f}",
                delta=delta_str,
                delta_color="#00E676" if change >= 0 else "#FF1744",
                icon="📈" if change >= 0 else "📉",
            )
except Exception:
    st.info("📡 Loading index data...")

st.markdown("<br>", unsafe_allow_html=True)

# ── Volatility Regime ──
section_header("Volatility Regime", "🌊")

try:
    vol_data = compute_volatility_regime()
    col1, col2, col3 = st.columns(3)

    with col1:
        regime_colors = {"HIGH VOLATILITY": "#FF1744", "NORMAL": "#FFC107", "LOW VOLATILITY": "#00E676", "UNKNOWN": "#78909C"}
        color = regime_colors.get(vol_data["regime"], "#78909C")
        metric_card(
            label="Current Regime",
            value=vol_data["regime"],
            icon="🌊",
        )

    with col2:
        metric_card(
            label="Annualized Volatility",
            value=f"{vol_data['current_vol']:.1f}%",
            delta=f"Avg: {vol_data['avg_vol']:.1f}%",
            delta_color=COLORS["info"],
        )

    with col3:
        metric_card(
            label="Volatility Percentile",
            value=f"{vol_data['percentile']:.0f}th",
            delta="Higher = more volatile than usual",
            delta_color=COLORS["muted"],
        )

    # Volatility chart
    vol_series = vol_data.get("series")
    if vol_series is not None and not vol_series.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=vol_series.index,
            y=vol_series["vol_20"],
            fill="tozeroy",
            fillcolor="rgba(124, 77, 255, 0.15)",
            line=dict(color=COLORS["primary"], width=2),
            name="20D Volatility",
        ))
        fig.add_hline(y=vol_data["avg_vol"], line_dash="dash", line_color=COLORS["warning"],
                      annotation_text="Average", annotation_position="top right")
        fig.update_layout(
            **PLOTLY_DARK_TEMPLATE["layout"],
            height=300,
            title=dict(text="NIFTY 50 — Rolling 20-Day Annualized Volatility", font=dict(size=13)),
            yaxis_title="Volatility (%)",
        )
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.info("🌊 Loading volatility data...")

st.markdown("<br>", unsafe_allow_html=True)

# ── Market Breadth ──
section_header("Market Breadth", "📊")

try:
    breadth = compute_market_breadth()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Advancing", str(breadth["advancing"]), icon="🟢")
    with col2:
        metric_card("Declining", str(breadth["declining"]), icon="🔴")
    with col3:
        metric_card("A/D Ratio", str(breadth["ad_ratio"]), icon="⚖️")
    with col4:
        signal_color = {"BULLISH": "success", "BEARISH": "danger", "NEUTRAL": "warning"}
        metric_card("Signal", breadth["signal"], icon="📡")

    # Breadth pie chart
    fig = go.Figure(go.Pie(
        labels=["Advancing", "Declining", "Unchanged"],
        values=[breadth["advancing"], breadth["declining"], breadth["unchanged"]],
        hole=0.5,
        marker=dict(colors=[COLORS["success"], COLORS["danger"], COLORS["muted"]]),
        textinfo="label+percent",
        textfont=dict(size=12),
    ))
    fig.update_layout(**PLOTLY_DARK_TEMPLATE["layout"], height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
except Exception:
    st.info("📊 Computing market breadth...")

st.markdown("<br>", unsafe_allow_html=True)

# ── Sector Performance ──
section_header("Sector Performance", "🏭")

period_sel = st.selectbox("Performance Period", ["1 Month", "3 Months", "6 Months"], index=0, key="sector_period")
period_map = {"1 Month": 30, "3 Months": 90, "6 Months": 180}

try:
    sector_df = compute_sector_performance(period_map[period_sel])

    if not sector_df.empty:
        # Sector bar chart
        fig = go.Figure()
        colors = [COLORS["success"] if val >= 0 else COLORS["danger"]
                  for val in sector_df["Avg Return (%)"]]

        fig.add_trace(go.Bar(
            x=sector_df["Sector"],
            y=sector_df["Avg Return (%)"],
            marker_color=colors,
            text=sector_df["Avg Return (%)"].apply(lambda x: f"{x:+.1f}%"),
            textposition="outside",
        ))

        fig.update_layout(
            **PLOTLY_DARK_TEMPLATE["layout"],
            height=400,
            title=dict(text=f"Sector Returns — {period_sel}", font=dict(size=13)),
            yaxis_title="Average Return (%)",
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Sector table
        st.dataframe(
            sector_df,
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("Computing sector performance...")
except Exception:
    st.info("🏭 Loading sector data...")

# ── Top Movers ──
st.markdown("<br>", unsafe_allow_html=True)
section_header("Quick Stock Scanner", "🔎")

scan_sector = st.selectbox("Scan Sector", ["All Sectors"] + get_all_sectors(), key="scan_sector")

if scan_sector != "All Sectors":
    scan_symbols = get_sector_symbols(scan_sector)[:10]
else:
    from config.stock_universe import STOCK_UNIVERSE
    scan_symbols = [s["symbol"] for s in STOCK_UNIVERSE if s["index"] == "NIFTY 50"][:15]

if st.button("🔍 Scan Stocks", key="scan_btn"):
    with st.spinner("Scanning..."):
        records = []
        for sym in scan_symbols:
            q = fetch_realtime_quote(sym)
            if q.get("price", 0) > 0:
                records.append({
                    "Symbol": sym,
                    "Price (₹)": q["price"],
                    "Change (%)": q["change_pct"],
                    "Volume": q["volume"],
                    "P/E": q["pe_ratio"],
                })

        if records:
            scan_df = pd.DataFrame(records).sort_values("Change (%)", ascending=False)
            st.dataframe(scan_df, hide_index=True, use_container_width=True)
