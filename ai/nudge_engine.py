"""
Agentic Financial Co-Pilot — AI-driven nudge engine using Groq LLM.
Generates contextual behavioral warnings and investment insights.
"""

from __future__ import annotations

from ai.groq_client import GroqClient


SYSTEM_PROMPT = """You are **SheepOrSleep AI**, an expert behavioral finance advisor specialized in the Indian stock market.

Your role is to help retail investors overcome cognitive biases like:
- **Herd mentality**: Following the crowd without independent analysis
- **Panic selling**: Fear-driven exits during temporary corrections
- **Loss aversion**: Feeling losses ~2x more than equivalent gains
- **Recency bias**: Overweighting recent events

Guidelines:
1. Always ground advice in data and behavioral finance research
2. Reference Indian market context (NIFTY, SENSEX, SEBI regulations)
3. Use ₹ (INR) for monetary values
4. Be empathetic but firm — acknowledge emotions, then redirect to data
5. Never give specific buy/sell recommendations or price targets
6. Encourage systematic investing (SIP) over timing the market
7. Format responses with clear headings and bullet points
8. Keep responses concise and actionable"""


class NudgeEngine:
    """Generate contextual behavioral nudges and investment insights."""

    def __init__(self, groq_client: GroqClient = None):
        self.client = groq_client or GroqClient()

    def generate_panic_nudge(self, stock_name: str, panic_score: float, factors: dict) -> str:
        """Generate a contextual warning when panic is detected."""
        prompt = f"""A retail investor is looking at {stock_name} which currently has a panic score of {panic_score}/100.

Factor breakdown:
{chr(10).join(f'- {k}: {v}/100' for k, v in factors.items())}

Generate a brief, empathetic but data-driven nudge to help the investor avoid impulsive decisions.
Include:
1. What the data is showing
2. Historical context of similar situations in Indian markets
3. What a disciplined investor would do
4. A behavioral bias this situation commonly triggers"""

        return self.client.chat(prompt, SYSTEM_PROMPT)

    def generate_herding_alert(self, sector: str, intensity: float, gamma2: float) -> str:
        """Generate alert when herding is detected in a sector."""
        prompt = f"""Herding behavior has been detected in the **{sector}** sector of the Indian stock market.

- Herding Intensity: {intensity}/100
- CCK Model γ₂ coefficient: {gamma2} (negative = herding confirmed)

Generate a brief alert explaining:
1. What herding means in this sector's context
2. Why following the herd is dangerous here
3. What independent analysis an investor should do instead
4. Historical examples of herding in Indian markets"""

        return self.client.chat(prompt, SYSTEM_PROMPT)

    def generate_behavior_gap_insight(self, gap_data: dict) -> str:
        """Generate insight about an investor's behavior gap."""
        prompt = f"""Behavior Gap Analysis for {gap_data.get('symbol', 'a stock')}:

- Investment CAGR (Buy & Hold): {gap_data.get('investment_cagr', 'N/A')}%
- Estimated Investor CAGR: {gap_data.get('estimated_investor_cagr', 'N/A')}%
- Behavior Gap: {gap_data.get('behavior_gap', 'N/A')}%
- Volume-Price Correlation: {gap_data.get('volume_price_correlation', 'N/A')}

Generate a brief, insightful explanation of:
1. What the behavior gap means in rupee terms for a ₹10 lakh corpus over 10 years
2. Common biases causing this gap
3. Three specific actions to reduce the gap
4. An encouraging data point about SIP performance in Indian markets"""

        return self.client.chat(prompt, SYSTEM_PROMPT)

    def generate_sip_reinforcement(self, sim_results: dict) -> str:
        """Reinforce SIP discipline using Monte Carlo results."""
        cost = sim_results.get("cost_of_panic", {})
        prompt = f"""Monte Carlo Simulation Results ({sim_results.get('n_simulations', 0)} simulations, {sim_results.get('years', 0)} years):

- Disciplined SIP median wealth: ₹{sim_results.get('sip', {}).get('median', 0):,.0f}
- Panic Seller median wealth: ₹{sim_results.get('panic', {}).get('median', 0):,.0f}
- Mean wealth destroyed by panic: ₹{cost.get('mean_loss', 0):,.0f}
- SIP beats panic in {cost.get('win_rate', 0)}% of scenarios

Generate a brief, compelling message that:
1. Quantifies the cost of panic selling in everyday terms
2. Explains the power of Rupee-Cost Averaging
3. References real SIP success stories in Indian mutual funds
4. Ends with a motivational note about long-term wealth creation"""

        return self.client.chat(prompt, SYSTEM_PROMPT)

    def chat_copilot(self, messages: list[dict], market_context: str = "") -> str:
        """Interactive AI copilot conversation."""
        system = SYSTEM_PROMPT
        if market_context:
            system += f"\n\nCurrent market context:\n{market_context}"

        return self.client.chat_with_history(messages, system_prompt=system)
