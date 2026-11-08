---
name: Calm Behavioral Fintech
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#464555'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#777587'
  outline-variant: '#c7c4d8'
  surface-tint: '#4d44e3'
  primary: '#3525cd'
  on-primary: '#ffffff'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#c3c0ff'
  secondary: '#006c4a'
  on-secondary: '#ffffff'
  secondary-container: '#82f5c1'
  on-secondary-container: '#00714e'
  tertiary: '#703a00'
  on-tertiary: '#ffffff'
  tertiary-container: '#934e00'
  on-tertiary-container: '#ffd2b1'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#85f8c4'
  secondary-fixed-dim: '#68dba9'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#ffdcc3'
  tertiary-fixed-dim: '#ffb77d'
  on-tertiary-fixed: '#2f1500'
  on-tertiary-fixed-variant: '#6e3900'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.04em
  data-metric-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  data-metric-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
---

## Brand & Style

This design system targets Indian retail investors navigating high-stress market cycles, volatile assets, and behavioral biases like FOMO and panic selling. The aesthetic rejects the hyper-stimulated, casino-like visual vernacular of speculative trading apps in favor of intentional calm, emotional stability, and intellectual clarity.

The visual style is **Corporate Modern with Warm Minimalist Discipline**:
- **Generous Whitespace**: High visual breathing room to lower cognitive load and reduce impulsive financial actions.
- **Micro-Structured Precision**: Ultra-subtle borders paired with soft, low-contrast shadows establish grounded structural containers.
- **Reassuring Authority**: Geometric structure through modern typographic hierarchy balanced against accessible rounded containers that invite inspection without intimidation.

## Colors

The palette establishes an emotional baseline of rational clarity:
- **Primary Brand Indigo (`#4F46E5`)**: Anchor tone for high-intent actions, structural branding, selected analytical tabs, and progress indicators.
- **Calm Status Green (`#059669`)**: Conveys discipline, rational rebalancing, stable capital flow, and healthy behavioral indices.
- **Watch Status Amber (`#D97706`)**: Alerts to impending biases, excessive churn, or market turbulence without inducing panic.
- **High Status Red (`#DC2626`)**: Reserved strictly for critical behavioral risk, catastrophic stops, and severe irrational drawdown warnings.
- **Neutral Slate Spectrum**:
  - Dark Slate (`#0F172A`): Primary headings, critical portfolio figures, and high-emphasis labels.
  - Mid Slate (`#475569`): Explanatory body text, contextual guidance, and metadata.
  - Muted Slate (`#64748B`): Inactive iconography, chart crosshairs, and auxiliary timestamps.
  - Border Substrate (`#E2E8F0`): Structural containment for light surfaces.
  - Canvas Base (`#F7F8FA`): Off-white, low-glare surface preventing eye strain during long analytical sessions.
  - Card & Module Surface (`#FFFFFF`): Pure white, elevated containers.

In dark contexts, surfaces invert to rich navy slates (`#0F172A` canvas base, `#1E293B` elevated cards) with light borders (`#334155`) to sustain visual calm without OLED-harsh contrasts.

## Typography

The type system blends structural geometric warmth with clinical tabular precision:
- **Headlines (`Plus Jakarta Sans`)**: Delivers open counters and smooth curves that instill confidence without sounding sterile.
- **Body & Labels (`Inter`)**: Neutral workhorse tuned for high legibility across small sizes, density tables, and dense explanatory annotations.
- **Numeric & Monetary Treatment**: All numerical metrics, percentage shifts, and INR figures must employ OpenType tabular figures (`font-variant-numeric: tabular-nums;`) to maintain vertical column alignments.
- **Rupee Glyph (`₹`)**: Displayed with equal visual baseline weighting and matching stroke weight to its following numerical value (e.g., `₹12,45,000`).

## Layout & Spacing

The platform uses a responsive 12-column layout grid on desktop with bounded horizontal max-width containers (1280px) to prevent dashboard fatigue across ultra-wide monitors.

### Breakpoints & Geometry
- **Mobile (< 768px)**: 4 columns, 16px (`1rem`) outer margins, 16px gutters. Analytical modules fold into full-width vertical stacks.
- **Tablet (768px – 1024px)**: 8 columns, 24px (`1.5rem`) outer margins, 20px gutters. Dual-column metrics pairing.
- **Desktop (> 1024px)**: 12 columns, 32px (`2rem`) outer margins, 24px (`1.5rem`) gutters. Asymmetrical split views (e.g., 8-column analytical area paired with a 4-column contextual Copilot/bias gauge pane).

### Rhythm
Component internals follow strict multiples of 4px/8px:
- Compact elements (badges, buttons, inputs) leverage `space-xs` (4px) to `space-md` (16px) internal padding.
- Card interiors enforce `space-lg` (24px) padding to preserve an airy, premium finish.
- Structural module gaps rely on `space-xl` (32px) and `space-2xl` (48px).

## Elevation & Depth

This system avoids heavy drop shadows and neon glows in favor of restrained tactile elevation:

1. **Base Flat Layer (`Level 0`)**: Canvas backdrop (`#F7F8FA`).
2. **Structural Cards (`Level 1`)**: Pure white background (`#FFFFFF`), an ultra-fine border (`1px solid #E2E8F0`), and an ambient diffused shadow: `0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.02)`.
3. **Interactive & Hoverable Tiles (`Level 2`)**: `0 4px 6px -1px rgba(15, 23, 42, 0.05), 0 2px 4px -2px rgba(15, 23, 42, 0.03)` with border shifting to `#CBD5E1`.
4. **Drawers & Floating Contexts (`Level 3 - AI Copilot`)**: Distinct separation via `0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04)`, reinforced by an internal hairline border and a soft backdrop scrim (`rgba(15, 23, 42, 0.3)` with `4px` blur).

## Shapes

The design system applies a **Rounded (Level 2)** shape discipline:
- **Cards & Primary Modules**: 12px to 16px corner radiuses (`rounded-lg` / `rounded-xl`), creating soft containment shields without feeling child-like.
- **Controls & Form Elements**: 8px (`rounded-md`) to ensure crisp interaction boundaries for inputs, buttons, and dropdowns.
- **Status Pills, Behavioral Indicators & Tags**: Full pill styling (`9999px`) for quick scanability and distinct separation from rectangular interactive inputs.

## Components

### Buttons
- **Primary**: Solid Indigo (`#4F46E5`), white text, 8px radius, 0 1px 2px rgba(0,0,0,0.05) shadow. Subtle hover transition to `#4338CA`.
- **Secondary / Calm**: 1px border `#E2E8F0`, white background, Slate 900 text. Hover states lift with subtle Slate 50 background (`#F8FAFC`).
- **Quiet / Ghost**: Transparent container, text `#475569`, hover background `#F1F5F9`.

### Cards & Module Containers
- Surface `#FFFFFF`, 1px crisp border `#E2E8F0`, 12px–16px border-radius, 24px padding.
- Internal headers split with 1px border or distinct 16px margin spacing.

### Status Pills & Behavioral Badges
- Pill shape (`9999px`), 4px 10px padding.
- **Calm (Disciplined)**: Light green tint (`#ECFDF5`), green border (`#A7F3D0`), text `#047857`, 12px checkmark or serene shield icon.
- **Watch (Elevated Activity)**: Light amber tint (`#FFFBEB`), amber border (`#FDE68A`), text `#B45309`, alert icon.
- **High Risk (FOMO / Panic Danger)**: Light red tint (`#FEF2F2`), red border (`#FECACA`), text `#B91C1C`, warning icon.

### Form Inputs & Checkboxes
- **Inputs**: 8px radius, 40px height, border 1px `#CBD5E1`, typography 14px Inter with placeholder in `#94A3B8`. Focus state introduces a crisp ring: 2px Indigo `#4F46E5` with 2px offset.
- **Checkboxes & Radios**: 4px radius for checkboxes, 50% for radios; checked fill `#4F46E5` with white check/dot.

### Specialized Behavioral Components
- **Semicircle Behavior Gauge**:
  - Displays investor emotional state (e.g., "Panic", "Neutral", "Euphoric/FOMO").
  - 180-degree arch divided into smooth calibrated segments with soft gradient strokes (`#059669` transitioning through `#D97706` to `#DC2626`).
  - Central reading in `Plus Jakarta Sans` 24px bold tabular text with a secondary label pill beneath.
- **Clean Interactive Charts**:
  - Soft gradients over harsh solid fills (e.g., indigo stroke with `rgba(79, 70, 229, 0.08)` to transparent fill).
  - Tabular tooltips styled as mini Level-2 cards with 1px border and monetary INR values.
- **Analytical Section Tabs**:
  - Segmented control pills or low-key baseline tabs. Active state features a solid white segment or a 2px Indigo baseline indicator.
- **Collapsible Technical Accordions**:
  - Clean borders `#E2E8F0` with subtle chevron transitions (180-degree smooth transform) revealing behavioral analysis tips.
- **AI Copilot Drawer**:
  - Slides from the right (420px desktop width), framed by an ultra-thin left border.
  - Features reassuring conversational tone cards, distinct message bubbles (user: `#F1F5F9`, assistant: `#FFFFFF` with 1px border), and instant behavioral check prompts.