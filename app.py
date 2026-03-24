"""
SheepOrSleep — AI-Driven Behavioral Bias Detector for Indian Stocks
Main application entry point.
"""

import streamlit as st

st.set_page_config(
    page_title="SheepOrSleep | AI Bias Detector",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.theme import get_custom_css, COLORS
from ui.components import (
    metric_card, hero_banner, section_header, status_badge,
    format_inr, format_market_cap, glass_container,
)
from config.settings import settings
from config.stock_universe import get_display_options, symbol_from_display, get_all_sectors
from data.stock_data import fetch_realtime_quote, fetch_index_data, fetch_historical_data
from ai.groq_client import GroqClient

# ── Inject Custom CSS ──
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0;">
        <div style="font-size: 2.5rem;">🐑</div>
        <div style="font-size: 1.4rem; font-weight: 800; margin: 4px 0;">SheepOrSleep</div>
        <div style="font-size: 0.75rem; opacity: 0.6; letter-spacing: 1px; text-transform: uppercase;">
            AI Behavioral Bias Detector
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Dynamic stock selector
    st.markdown("##### 🔍 Select Stock")
    display_options = get_display_options()
    selected_display = st.selectbox(
        "Choose any Indian stock",
        options=display_options,
        index=0,
        label_visibility="collapsed",
    )
    selected_symbol = symbol_from_display(selected_display)

    # Store in session state
    st.session_state["selected_symbol"] = selected_symbol
    st.session_state["selected_display"] = selected_display

    st.divider()

    # Analysis parameters
    st.markdown("##### ⚙️ Parameters")
    lookback_period = st.selectbox(
        "Lookback Period",
        options=["1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "5 Years"],
        index=3,
    )
    period_map = {
        "1 Month": 30, "3 Months": 90, "6 Months": 180,
        "1 Year": 365, "2 Years": 730, "5 Years": 1825,
    }
    st.session_state["lookback_days"] = period_map.get(lookback_period, 365)

    st.divider()

    # Status indicators
    groq = GroqClient()
    if groq.is_available:
        st.markdown(
            '<span class="badge badge-success">🤖 AI Copilot Active</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span class="badge badge-warning">⚠️ AI Copilot Offline</span>',
            unsafe_allow_html=True
        )

    st.markdown(f"""
    <div style="margin-top: 8px; font-size: 0.75rem; opacity: 0.5;">
        Model: {settings.GROQ_MODEL}<br>
        Version: {settings.APP_VERSION}
    </div>
    """, unsafe_allow_html=True)

    # Warnings
    warnings = settings.validate()
    for w in warnings:
        st.caption(f"⚠️ {w}")


# ── Main Page: Dashboard Home ──
hero_banner(
    "🐑 SheepOrSleep",
    "AI-Driven Behavioral Bias Detector for Indian Stocks — Stop Following the Herd, Start Making Data-Driven Decisions"
)

# ── Market Indices Overview ──
section_header("Market Overview", "📊")

try:
    indices = fetch_index_data()
    cols = st.columns(3)
    for i, (sym, data) in enumerate(indices.items()):
        with cols[i]:
            change = data.get("change", 0)
            delta_str = f"{'▲' if change >= 0 else '▼'} {abs(change):.2f} ({data.get('change_pct', 0):+.2f}%)"
            delta_color = "#00E676" if change >= 0 else "#FF1744"
            metric_card(
                label=data.get("display_name", sym),
                value=f"₹{data.get('price', 0):,.2f}",
                delta=delta_str,
                delta_color=delta_color,
                icon="📈" if change >= 0 else "📉",
            )
except Exception as e:
    st.info("📡 Market data loading... Please refresh if indices don't appear.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Selected Stock Quick View ──
section_header(f"Selected: {selected_display}", "🎯")

try:
    quote = fetch_realtime_quote(selected_symbol)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        change = quote.get("change", 0)
        metric_card(
            label="Current Price",
            value=f"₹{quote.get('price', 0):,.2f}",
            delta=f"{'▲' if change >= 0 else '▼'} {abs(change):.2f} ({quote.get('change_pct', 0):+.2f}%)",
            delta_color="#00E676" if change >= 0 else "#FF1744",
        )

    with col2:
        metric_card(
            label="Volume",
            value=f"{quote.get('volume', 0):,.0f}",
            delta=f"Avg: {quote.get('avg_volume', 0):,.0f}",
            delta_color=COLORS["info"],
        )

    with col3:
        metric_card(
            label="Market Cap",
            value=format_market_cap(quote.get("market_cap", 0)),
            delta=f"P/E: {quote.get('pe_ratio', 0):.1f}",
            delta_color=COLORS["muted"],
        )

    with col4:
        w52h = quote.get("week_52_high", 0)
        w52l = quote.get("week_52_low", 0)
        price = quote.get("price", 0)
        if w52h and w52l and w52h > w52l:
            position = (price - w52l) / (w52h - w52l) * 100
        else:
            position = 50
        metric_card(
            label="52W Range Position",
            value=f"{position:.0f}%",
            delta=f"L: ₹{w52l:,.0f} | H: ₹{w52h:,.0f}",
            delta_color=COLORS["muted"],
        )
except Exception:
    st.info("📡 Loading stock data...")

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick Price Chart ──
section_header("Price History", "📈")

try:
    df = fetch_historical_data(selected_symbol, st.session_state.get("lookback_days", 365))
    if not df.empty:
        import plotly.graph_objects as go
        from ui.theme import PLOTLY_DARK_TEMPLATE

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC",
            increasing_line_color=COLORS["success"],
            decreasing_line_color=COLORS["danger"],
        ))

        fig.update_layout(
            **PLOTLY_DARK_TEMPLATE["layout"],
            height=450,
            xaxis_rangeslider_visible=False,
            showlegend=False,
            title=dict(text=f"{selected_display} — Candlestick Chart", font=dict(size=14)),
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No historical data available for this stock.")
except Exception as e:
    st.info("📈 Loading chart data...")

# ── Feature Navigation ──
st.markdown("<br>", unsafe_allow_html=True)
section_header("Explore Analytics", "🧭")

col1, col2, col3, col4, col5 = st.columns(5)

features = [
    ("📊", "Market Pulse", "Real-time market overview & sector analysis"),
    ("🐑", "Herd Detector", "CCK model herding analysis across sectors"),
    ("🚨", "Panic Scanner", "Multi-factor panic selling detection"),
    ("📉", "Behavior Gap", "Monte Carlo SIP vs Panic simulation"),
    ("🤖", "AI Copilot", "Chat with your AI financial advisor"),
]

for col, (icon, title, desc) in zip([col1, col2, col3, col4, col5], features):
    with col:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; min-height: 150px;">
            <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
            <div style="font-size: 1rem; font-weight: 700; margin-bottom: 6px;">{title}</div>
            <div style="font-size: 0.78rem; opacity: 0.6;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-top: 30px; opacity: 0.4; font-size: 0.8rem;">
    Use the sidebar pages ← to navigate to each analytics module
</div>
""", unsafe_allow_html=True)
