"""
LLM-based financial sentiment analysis via Groq.
"""

from __future__ import annotations
from ai.groq_client import GroqClient
from data.news_sentiment import analyze_sentiment_batch, fetch_news_headlines


class SentimentAnalyzer:
    """Groq LLM-powered sentiment analysis for financial news."""

    def __init__(self, groq_client: GroqClient = None):
        self.client = groq_client or GroqClient()

    def analyze_stock_sentiment(self, stock_name: str, max_headlines: int = 15) -> dict:
        """Fetch headlines and analyze sentiment for a stock."""
        headlines = fetch_news_headlines(stock_name, max_headlines)
        if not headlines:
            return {"headlines": [], "summary": {"positive": 0, "negative": 0, "neutral": 0, "total": 0, "avg_score": 0}}

        analyzed = analyze_sentiment_batch(headlines, self.client)

        from data.news_sentiment import get_sentiment_summary
        summary = get_sentiment_summary(analyzed)

        return {
            "headlines": analyzed,
            "summary": summary,
        }

    def get_market_sentiment_report(self, stock_name: str, sentiment_data: dict) -> str:
        """Generate an LLM-based interpretation of sentiment data."""
        if not self.client.is_available:
            return self._fallback_report(sentiment_data)

        summary = sentiment_data.get("summary", {})
        headlines = sentiment_data.get("headlines", [])

        top_headlines = "\n".join(
            f"- [{h.get('sentiment', 'N/A')}] {h['title']}"
            for h in headlines[:8]
        )

        prompt = f"""Analyze the current news sentiment for **{stock_name}** in the Indian stock market.

Sentiment Summary:
- Positive: {summary.get('positive', 0)} headlines
- Negative: {summary.get('negative', 0)} headlines
- Neutral: {summary.get('neutral', 0)} headlines
- Average Score: {summary.get('avg_score', 0)} (scale: -1 to +1)

Top Headlines:
{top_headlines}

Provide:
1. Brief overall sentiment assessment (1-2 lines)
2. Key themes driving sentiment
3. Whether current sentiment suggests crowd behavior/herding
4. Recommended investor stance based purely on sentiment (cautious/neutral/opportunistic)"""

        return self.client.chat(prompt)

    def _fallback_report(self, sentiment_data: dict) -> str:
        summary = sentiment_data.get("summary", {})
        score = summary.get("avg_score", 0)
        if score > 0.3:
            return "📈 **Overall Sentiment: Positive** — News flow is largely favorable. However, be cautious of herd-driven optimism."
        elif score < -0.3:
            return "📉 **Overall Sentiment: Negative** — Bearish news dominating. Check if this represents genuine risk or fear-driven overreaction."
        else:
            return "📊 **Overall Sentiment: Neutral** — Mixed news flow. No strong directional bias detected in headline sentiment."
