"""
🤖 AI Copilot — Chat-based AI financial advisor powered by Groq LLM.
"""

import streamlit as st

st.set_page_config(page_title="AI Copilot | SheepOrSleep", page_icon="🤖", layout="wide")

from ui.theme import get_custom_css, COLORS
from ui.components import section_header, hero_banner, metric_card
from config.stock_universe import get_display_options, symbol_from_display
from ai.groq_client import GroqClient
from ai.nudge_engine import NudgeEngine
from data.stock_data import fetch_realtime_quote, fetch_historical_data
from analytics.panic_detector import PanicDetector
from config.settings import settings

st.markdown(get_custom_css(), unsafe_allow_html=True)

hero_banner(
    "🤖 AI Financial Copilot",
    "Your personal behavioral finance advisor — Ask about stocks, biases, and investment strategies"
)

groq = GroqClient()

if not groq.is_available:
    st.error("""
    ⚠️ **Groq API Key Required**

    The AI Copilot needs a valid Groq API key. Please:
    1. Get a free API key from [console.groq.com](https://console.groq.com)
    2. Add it to your `.env` file: `GROQ_API_KEY=your_key_here`
    3. Restart the application
    """)
    st.stop()

# ── Sidebar Context ──
with st.sidebar:
    st.markdown("##### 🎯 Chat Context")
    display_opts = get_display_options()
    default_idx = 0
    if "selected_display" in st.session_state:
        try:
            default_idx = display_opts.index(st.session_state["selected_display"])
        except ValueError:
            default_idx = 0
    selected = st.selectbox("Context Stock", display_opts, index=default_idx, key="copilot_stock")
    symbol = symbol_from_display(selected)
    stock_name = selected.split("(")[0].strip()

    include_context = st.checkbox("Include live market data in chat", value=True)

# ── Build Market Context ──
market_context = ""
if include_context:
    try:
        quote = fetch_realtime_quote(symbol)
        market_context = f"""
Stock: {stock_name} ({symbol})
Current Price: ₹{quote.get('price', 0):,.2f}
Change: {quote.get('change_pct', 0):+.2f}%
Volume: {quote.get('volume', 0):,}
P/E Ratio: {quote.get('pe_ratio', 0):.1f}
52W High: ₹{quote.get('week_52_high', 0):,.2f}
52W Low: ₹{quote.get('week_52_low', 0):,.2f}
Market Cap: ₹{quote.get('market_cap', 0):,.0f}
"""
    except Exception:
        market_context = f"Stock: {stock_name} ({symbol})"

# ── Quick Action Buttons ──
section_header("Quick Actions", "⚡")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Analyze This Stock", use_container_width=True, key="qa_analyze"):
        quick_prompt = f"Give me a comprehensive behavioral analysis of {stock_name}. What biases should I watch for when investing in this stock? Include any sector-specific herding tendencies."
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({"role": "user", "content": quick_prompt})

with col2:
    if st.button("🐑 Am I Being a Sheep?", use_container_width=True, key="qa_sheep"):
        quick_prompt = f"I'm thinking of buying {stock_name} because everyone on social media is talking about it. Help me evaluate whether I'm falling into herd mentality. What should I check independently?"
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({"role": "user", "content": quick_prompt})

with col3:
    if st.button("😰 Should I Panic?", use_container_width=True, key="qa_panic"):
        quick_prompt = f"{stock_name} has been falling recently and I'm scared. Should I sell? Help me think through this rationally."
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({"role": "user", "content": quick_prompt})

with col4:
    if st.button("💰 SIP Strategy", use_container_width=True, key="qa_sip"):
        quick_prompt = f"Explain why a SIP in {stock_name} (or its sector) might be better than trying to time the market. Use data from Indian markets."
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({"role": "user", "content": quick_prompt})

st.markdown("<br>", unsafe_allow_html=True)

# ── Chat Interface ──
section_header("Chat with AI Copilot", "💬")

st.markdown(f"""
<div style="font-size: 0.8rem; opacity: 0.5; margin-bottom: 12px;">
    Model: {settings.GROQ_MODEL} | Context: {stock_name}
</div>
""", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role, avatar="🧑‍💼" if role == "user" else "🤖"):
        st.markdown(message["content"])

# Process any pending quick action (last message that hasn't been responded to)
if (st.session_state.messages
    and st.session_state.messages[-1]["role"] == "user"
    and not any(m["role"] == "assistant" and i > 0 and st.session_state.messages[i-1] == st.session_state.messages[-1]
                for i, m in enumerate(st.session_state.messages))):

    # Need to generate response for the last user message
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            nudge = NudgeEngine(groq)
            response = nudge.chat_copilot(st.session_state.messages, market_context)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Chat input
if prompt := st.chat_input("Ask about investing, biases, or any Indian stock..."):
    # Display user message
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            nudge = NudgeEngine(groq)
            response = nudge.chat_copilot(st.session_state.messages, market_context)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# ── Clear Chat ──
st.markdown("<br>", unsafe_allow_html=True)
col_clear1, col_clear2 = st.columns([3, 1])
with col_clear2:
    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.messages = []
        st.rerun()

# ── AI Behavioral Report ──
st.markdown("<br>", unsafe_allow_html=True)
section_header("Auto-Generated Behavioral Report", "📋")

if st.button("📋 Generate Full Report", type="primary", use_container_width=True, key="gen_report"):
    with st.spinner(f"Generating comprehensive behavioral report for {stock_name}..."):
        # Gather data
        try:
            panic = PanicDetector().compute_panic_score(symbol, 90)
            panic_info = f"Panic Score: {panic['panic_score']}/100 ({panic['level']})"
        except Exception:
            panic_info = "Panic Score: N/A"

        report_prompt = f"""Generate a comprehensive behavioral finance report for {stock_name} ({symbol}).

Market Data:
{market_context}

{panic_info}

Structure the report as follows:

## 🐑 Herding Risk Assessment
Analyze the likelihood that current interest in this stock is driven by herd behavior.

## 🚨 Panic Selling Risk
Based on current volatility and sentiment, assess the risk of panic selling.

## 📊 Behavioral Biases to Watch
List the top 3 biases most relevant to this stock right now.

## 💡 Rational Investor Checklist
5 data-driven checks an investor should make before buying/selling.

## 🎯 Recommended Behavioral Strategy
What approach minimizes the impact of cognitive biases for this stock?

Use ₹ for all monetary values. Reference Indian market context."""

        response = groq.chat(report_prompt)
        st.markdown(f'<div class="glass-card">{response}</div>', unsafe_allow_html=True)
