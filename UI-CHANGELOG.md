# UI Redesign & Data Integrity Changelog

This document summarizes the rebuild of the **SheepOrSleep** frontend to align pixel-faithfully with the `UI_DESIGN/` specifications (Desktop 1440px & Mobile 390px) while maintaining strict financial, econometric, and data integrity.

---

## 1. What Was Built

### A. Design Tokens & Typography (`DESIGN.md`)
- **Theme Translation**: Mapped all Google Material 3 tokens into CSS custom properties in `binary-investor/app/globals.css` with dark mode support (`.dark` class).
- **Colors**:
  - Primary: `#3525cd` (Navy Indigo), Primary Container: `#4f46e5`
  - Secondary: `#006d3b` (Forest Green), On-Secondary: `#ffffff`
  - Tertiary / Amber: `#b45309`, On-Tertiary: `#ffffff`
  - Error: `#ba1a1a`
  - Surface hierarchy: `surface` (`#faf8ff`), `surface-container-low` (`#f3f2fa`), `surface-container` (`#edeef6`), `surface-container-high` (`#e7e8f0`), `surface-container-highest` (`#e1e2ea`)
- **Typography**: Integrated Google Fonts `Plus Jakarta Sans` for headlines, `Inter` for body/tables, and `Material Symbols Outlined` for iconography.
- **Shadows & Radii**: Elevation shadows (`shadow-sm`, `shadow-md`, `shadow-lg`) and custom radius (`rounded-xl` = 12px, `rounded-2xl` = 16px).

### B. Shared Modular Components
- `SemicircleGauge.tsx`: 180° calibrated SVG gauge with needle animation, center score readout, arc tracks, and status chips (`Calm`, `Watch`, `Risk`).
- `RangeBar52W.tsx`: 52-week price range progress slider with current price pin, median marker notch, and ₹ milestones.
- `StatusChip.tsx`: Semantic status pill tags (`calm`, `watch`, `risk`, `edge`, `neutral`).
- `MetricTile.tsx`: Responsive metric tiles with labels, values, subtexts, and trend arrows.
- `NoticeBanner.tsx`: Plain English Behavioral Takeaway callout banner.
- `SkeletonLoader.tsx`: Pulse loading state skeleton for asynchronous queries.
- `DegradedStateBanner.tsx`: Resilient warning card shown when market data inputs are incomplete or upstream providers fail.
- `StockSelectorModal.tsx`: Searchable 54-stock modal categorized across NIFTY 50 and NIFTY NEXT 50 sectors.
- `AICopilotDrawer.tsx`: Slide-over drawer on desktop (1440px) and bottom sheet on mobile (390px) with Llama-3.3-70b behavioral prompts.

### C. Recharts Visualizations
- `PriceVolumeChart.tsx`: Dual-axis price & volume chart with non-zero Y-axis, Area/Candlestick toggle, and panic volume markers.
- `CSADScatterChart.tsx`: CCK $|R_{m,t}|$ vs $CSAD_t$ quadratic regression scatter plot with fitted curvature.
- `MissingDaysBarChart.tsx`: Horizontal bar chart for the impact of missing 0, 5, 10, 15, 20, 30 best days, formatted with Indian currency units (`₹40k`, `₹80k`, `₹1.2L`).
- `MonteCarloHistogram.tsx`: Dual-distribution histogram comparing 500-10,000 simulated paths of Disciplined SIP vs. Panic Selling.

### D. Navigation & Layout
- `Header.tsx`: Fixed top bar with stock search trigger, navigation links, light/dark theme toggle, and delayed EOD status indicator.
- `MobileTabBar.tsx`: Fixed 64px mobile bottom navigation (`Dashboard`, `Copilot`, `Learn`) with $\ge 44\text{px}$ touch targets.
- `Footer.tsx`: Regulatory educational disclaimer and methodology reference links.

---

## 2. Elements Skipped or Adapted (Lack of Backend Data)

In adherence to the core rule (*"Use only data the backend actually returns. No invented sections, numbers, badges or 'live' labels"*):

1. **Beta vs NIFTY 50**:
   - *Mockup*: Displayed `Beta: 0.82`.
   - *Backend*: Does not compute CAPM Beta.
   - *Fix*: Substituted with real **Day Trading Range** (`dayLow` – `dayHigh`), which is directly computed from EOD quotes.
2. **Proprietary NSE Delivery % (64%)**:
   - *Mockup*: Displayed `Delivery %: 64%`.
   - *Backend*: Yahoo Finance does not supply proprietary NSE delivery volume.
   - *Fix*: Labeled truthfully as **Range Expansion Ratio** / **Delivery Proxy** (`est_del`), using intraday high-low range heuristic.
3. **Social Media Sentiment (+180% chatter)**:
   - *Mockup*: Included arbitrary social sentiment buzz metrics.
   - *Backend*: No social media scraper exists.
   - *Fix*: Omitted entirely and replaced with empirical **Order Flow Independence** derived from the CCK dispersion model.
4. **User Profile (`Arjun P.`)**:
   - *Mockup*: Displayed a hardcoded user avatar and name.
   - *Fix*: Replaced with an anonymous, session-based status indicator ("Calm Mode") to avoid misleading personalization without an auth system.
5. **"Live" Tag**:
   - *Mockup*: Tagged data as `• Live`.
   - *Fix*: Explicitly labeled as **"End-of-day data, delayed"** to comply with Indian market data licensing and regulatory disclosure guidelines.

---

## 3. Differences From Mockups & Text-Overlap Fixes

1. **Price Change Display Glitch**:
   - *Mockup / Old Code*: Displayed `+1.29% (+163.00%)` (appending `%` to the absolute point change ₹163.00).
   - *Fix*: Formatted clearly as `+₹163.00 (+1.29%) today`.
2. **Horizontal Bar Chart Duplicate Axis Ticks**:
   - *Old Code*: Truncated rupee rounding rendered repeated axis labels (`₹0  ₹0  ₹1L  ₹1L`).
   - *Fix*: Dynamic thousand (`k`) and lakh (`L`) formatting so labels render cleanly (`₹40k  ₹80k  ₹1.2L  ₹1.6L`).
3. **Panic Volatility String**:
   - *Old Code*: Displayed `Volatility is normal at 268800% vs avg 2250.00%` due to double 100x multiplication.
   - *Fix*: Properly prints `Realized 20-day volatility is 23.5% p.a. vs 1-year average of 22.5%`.
4. **Compliance & Educational Copy**:
   - Replaced prescriptive financial advice headers ("Recommended Actions") with "Behavioral Considerations" and prominent disclaimers ("Educational information, not financial advice").
