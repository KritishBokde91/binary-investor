"""
News headline scraping (Google News RSS) and Groq LLM-based sentiment analysis.
"""

from __future__ import annotations

import re
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

from config.settings import settings


@st.cache_data(ttl=settings.CACHE_TTL_NEWS, show_spinner=False)
def fetch_news_headlines(query: str, max_results: int = 15) -> list[dict]:
    """
    Fetch news headlines from Google News RSS feed for a given query.
    Returns list of dicts with: title, link, published, source.
    """
    try:
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(query + ' stock India')}&hl=en-IN&gl=IN&ceid=IN:en"
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        resp.raise_for_status()

        headlines = []
        # Simple XML parsing without external dependency
        items = re.findall(r"<item>(.*?)</item>", resp.text, re.DOTALL)

        for item in items[:max_results]:
            title_match = re.search(r"<title>(.*?)</title>", item)
            link_match = re.search(r"<link/>(.*?)(?:<|\n)", item)
            if not link_match:
                link_match = re.search(r"<link>(.*?)</link>", item)
            pub_match = re.search(r"<pubDate>(.*?)</pubDate>", item)
            source_match = re.search(r"<source.*?>(.*?)</source>", item)

            title = title_match.group(1) if title_match else "N/A"
            # Clean HTML entities
            title = title.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'").replace("&quot;", '"')

            headlines.append({
                "title": title,
                "link": link_match.group(1).strip() if link_match else "",
                "published": pub_match.group(1) if pub_match else "",
                "source": source_match.group(1) if source_match else "Google News",
            })

        return headlines

    except Exception as e:
        st.warning(f"News fetch error: {e}")
        return []


def analyze_sentiment_batch(
    headlines: list[dict],
    groq_client,
) -> list[dict]:
    """
    Use Groq LLM to analyze sentiment of news headlines.
    Returns headlines with added: sentiment (POSITIVE/NEGATIVE/NEUTRAL), score (-1 to 1), reasoning.
    """
    if not headlines or not groq_client:
        # Fallback: keyword-based sentiment
        return _keyword_sentiment(headlines)

    titles = [h["title"] for h in headlines]
    titles_text = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))

    prompt = f"""Analyze the sentiment of each financial news headline below for Indian stock market context.
For each headline, provide:
- sentiment: POSITIVE, NEGATIVE, or NEUTRAL
- score: float from -1.0 (very negative) to 1.0 (very positive)
- reason: one-line explanation

Headlines:
{titles_text}

Respond ONLY in this exact JSON format:
{{"results": [{{"index": 1, "sentiment": "POSITIVE", "score": 0.7, "reason": "..."}}]}}"""

    try:
        response = groq_client.chat(prompt, temperature=0.1)
        import json
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            results = data.get("results", [])

            for r in results:
                idx = r.get("index", 0) - 1
                if 0 <= idx < len(headlines):
                    headlines[idx]["sentiment"] = r.get("sentiment", "NEUTRAL")
                    headlines[idx]["score"] = float(r.get("score", 0))
                    headlines[idx]["reason"] = r.get("reason", "")

            # Fill missing
            for h in headlines:
                if "sentiment" not in h:
                    h["sentiment"] = "NEUTRAL"
                    h["score"] = 0.0
                    h["reason"] = "Unable to analyze"

            return headlines
    except Exception:
        pass

    return _keyword_sentiment(headlines)


def _keyword_sentiment(headlines: list[dict]) -> list[dict]:
    """Fallback keyword-based sentiment when LLM is unavailable."""
    positive_words = {
        "surge", "soar", "gain", "rally", "bull", "rise", "profit", "growth",
        "up", "high", "record", "buy", "upgrade", "positive", "strong",
        "boost", "outperform", "beat", "recover", "jump", "breakthrough",
    }
    negative_words = {
        "crash", "fall", "plunge", "bear", "loss", "decline", "drop", "sell",
        "panic", "fear", "crisis", "warn", "risk", "cut", "low", "weak",
        "downgrade", "slump", "tumble", "recession", "correction", "volatile",
    }

    for h in headlines:
        title_lower = h["title"].lower()
        pos_count = sum(1 for w in positive_words if w in title_lower)
        neg_count = sum(1 for w in negative_words if w in title_lower)

        if pos_count > neg_count:
            h["sentiment"] = "POSITIVE"
            h["score"] = min(0.3 + pos_count * 0.15, 1.0)
        elif neg_count > pos_count:
            h["sentiment"] = "NEGATIVE"
            h["score"] = max(-0.3 - neg_count * 0.15, -1.0)
        else:
            h["sentiment"] = "NEUTRAL"
            h["score"] = 0.0

        h["reason"] = "Keyword-based analysis"

    return headlines


def compute_daily_sentiment_score(headlines: list[dict]) -> float:
    """Compute aggregate daily sentiment score from analyzed headlines."""
    if not headlines:
        return 0.0
    scores = [h.get("score", 0) for h in headlines if "score" in h]
    return round(sum(scores) / max(len(scores), 1), 3) if scores else 0.0


def get_sentiment_summary(headlines: list[dict]) -> dict:
    """Return sentiment distribution summary."""
    if not headlines:
        return {"positive": 0, "negative": 0, "neutral": 0, "total": 0, "avg_score": 0}

    pos = sum(1 for h in headlines if h.get("sentiment") == "POSITIVE")
    neg = sum(1 for h in headlines if h.get("sentiment") == "NEGATIVE")
    neu = sum(1 for h in headlines if h.get("sentiment") == "NEUTRAL")

    return {
        "positive": pos,
        "negative": neg,
        "neutral": neu,
        "total": len(headlines),
        "avg_score": compute_daily_sentiment_score(headlines),
    }
