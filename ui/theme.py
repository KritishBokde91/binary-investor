"""
Premium dark theme with glassmorphism — custom CSS for Streamlit.
"""


def get_custom_css() -> str:
    """Return the full custom CSS for the SheepOrSleep app."""
    return """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ─── Global ──────────────────────────────────── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ─── Glassmorphism Cards ─────────────────────── */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .glass-card:hover {
        border-color: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    /* ─── Metric Cards ───────────────────────────── */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 24px;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.2;
        margin: 8px 0;
    }

    .metric-label {
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        opacity: 0.7;
    }

    .metric-delta {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 4px;
    }

    /* ─── Status Badges ──────────────────────────── */
    .badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }

    .badge-danger {
        background: rgba(255, 23, 68, 0.15);
        color: #FF1744;
        border: 1px solid rgba(255, 23, 68, 0.3);
    }

    .badge-warning {
        background: rgba(255, 193, 7, 0.15);
        color: #FFC107;
        border: 1px solid rgba(255, 193, 7, 0.3);
    }

    .badge-success {
        background: rgba(0, 230, 118, 0.15);
        color: #00E676;
        border: 1px solid rgba(0, 230, 118, 0.3);
    }

    .badge-info {
        background: rgba(41, 182, 246, 0.15);
        color: #29B6F6;
        border: 1px solid rgba(41, 182, 246, 0.3);
    }

    /* ─── Section Headers ────────────────────────── */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        margin: 28px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.08);
    }

    /* ─── Score Gauges ───────────────────────────── */
    .score-ring {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        position: relative;
    }

    .score-value {
        font-size: 2.2rem;
        font-weight: 900;
    }

    .score-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-align: center;
        margin-top: 8px;
        opacity: 0.8;
    }

    /* ─── Sentiment Colors ───────────────────────── */
    .sentiment-positive { color: #00E676; }
    .sentiment-negative { color: #FF1744; }
    .sentiment-neutral { color: #78909C; }

    /* ─── Chat Messages ──────────────────────────── */
    .chat-user {
        background: rgba(41, 182, 246, 0.1);
        border: 1px solid rgba(41, 182, 246, 0.2);
        border-radius: 16px 16px 4px 16px;
        padding: 14px 20px;
        margin: 8px 0;
    }

    .chat-ai {
        background: rgba(123, 31, 162, 0.1);
        border: 1px solid rgba(123, 31, 162, 0.2);
        border-radius: 16px 16px 16px 4px;
        padding: 14px 20px;
        margin: 8px 0;
    }

    /* ─── Animated Gradients ─────────────────────── */
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .hero-gradient {
        background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
        background-size: 200% 200%;
        animation: gradient-shift 8s ease infinite;
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 24px;
    }

    /* ─── Tables ──────────────────────────────────── */
    .styled-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 0.9rem;
    }

    .styled-table th {
        background: rgba(255, 255, 255, 0.05);
        padding: 12px 16px;
        text-align: left;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.78rem;
        letter-spacing: 0.8px;
    }

    .styled-table td {
        padding: 10px 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* ─── Buttons ─────────────────────────────────── */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    /* ─── Sidebar ─────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: rgba(15, 15, 25, 0.95);
        backdrop-filter: blur(20px);
    }

    /* ─── Expander ────────────────────────────────── */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1rem;
    }

    /* ─── Pulse animation for alerts ──────────────── */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }

    .pulse-alert {
        animation: pulse 2s infinite;
    }

    /* ─── Plotly chart container ──────────────────── */
    .plotly-chart-container {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        padding: 8px;
        border: 1px solid rgba(255,255,255,0.05);
    }
</style>
"""


PLOTLY_DARK_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#FFFFFF"),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.1)",
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.1)",
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11),
        ),
    )
)

# Color Palette
COLORS = {
    "primary": "#7C4DFF",
    "secondary": "#00E5FF",
    "accent": "#FF6D00",
    "success": "#00E676",
    "danger": "#FF1744",
    "warning": "#FFC107",
    "info": "#29B6F6",
    "muted": "#78909C",
    "bg_dark": "#0A0A1A",
    "bg_card": "rgba(255,255,255,0.05)",
    "gradient_1": ["#667eea", "#764ba2"],
    "gradient_2": ["#f093fb", "#f5576c"],
    "gradient_3": ["#4facfe", "#00f2fe"],
    "gradient_4": ["#43e97b", "#38f9d7"],
    "gradient_5": ["#fa709a", "#fee140"],
    "chart_colors": [
        "#7C4DFF", "#00E5FF", "#FF6D00", "#00E676", "#FF1744",
        "#FFC107", "#29B6F6", "#E040FB", "#76FF03", "#FF3D00",
    ],
}
