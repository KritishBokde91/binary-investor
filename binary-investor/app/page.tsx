"use client";

import { useState, useEffect } from "react";
import {
  TrendingUp, TrendingDown, Activity, BarChart2,
  Brain, Zap, AlertTriangle, CheckCircle2, ChevronRight,
  Info, Loader2, RefreshCw, Sparkles, BookOpen,
  ArrowUpRight, ArrowDownRight, DollarSign, Target,
} from "lucide-react";
import Link from "next/link";
import StockSelector from "@/app/components/StockSelector";
import AICopilotPanel from "@/app/components/AICopilot";
import {
  CandlestickChart, VolumeBarChart, PriceAreaChart,
  CSADScatterPlot, PanicVolumeChart, ZScoreChart,
  MCHistogram, MissingDaysChart,
} from "@/app/components/Charts";
import type { StockInfo, AnalysisResult } from "@/app/lib/types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/* ─── Helper: Format large numbers ─── */
function fmt(n: number, digits = 2): string {
  if (!n && n !== 0) return "—";
  if (n >= 1e12) return `₹${(n / 1e12).toFixed(digits)}T`;
  if (n >= 1e9) return `₹${(n / 1e9).toFixed(digits)}B`;
  if (n >= 1e7) return `₹${(n / 1e7).toFixed(digits)}Cr`;
  if (n >= 1e5) return `₹${(n / 1e5).toFixed(digits)}L`;
  return `₹${n.toLocaleString("en-IN", { maximumFractionDigits: digits })}`;
}

function fmtPct(n: number, digits = 2): string {
  if (!n && n !== 0) return "—";
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(digits)}%`;
}

/* ─── Section Wrapper ─── */
function Section({ title, subtitle, icon, children, delay = 0 }: {
  title: string; subtitle?: string; icon?: React.ReactNode;
  children: React.ReactNode; delay?: number;
}) {
  return (
    <div className="glass-card fade-up" style={{ animationDelay: `${delay}s`, opacity: 0 }}>
      <div style={{ padding: "20px 24px 16px", borderBottom: "1px solid var(--glass-border)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {icon && (
            <div style={{
              width: 32, height: 32, borderRadius: 10,
              background: "var(--accent-light)",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              {icon}
            </div>
          )}
          <div>
            <h2 className="section-title">{title}</h2>
            {subtitle && <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>{subtitle}</p>}
          </div>
        </div>
      </div>
      <div style={{ padding: "20px 24px" }}>{children}</div>
    </div>
  );
}

/* ─── Metric Card ─── */
function MetricCard({ label, value, sub, color, icon }: {
  label: string; value: string | number; sub?: string;
  color?: string; icon?: React.ReactNode;
}) {
  return (
    <div className="metric-card" style={{ padding: "18px 20px" }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 8 }}>
        <span style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 500, letterSpacing: "0.04em", textTransform: "uppercase", fontFamily: "var(--font-body)" }}>
          {label}
        </span>
        {icon && <span>{icon}</span>}
      </div>
      <div className="num-display" style={{ fontSize: 22, fontWeight: 700, color: color || "var(--text)", lineHeight: 1.1 }}>
        {value}
      </div>
      {sub && (
        <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 5, fontFamily: "var(--font-body)" }}>
          {sub}
        </div>
      )}
    </div>
  );
}

/* ─── Stat Row ─── */
function StatRow({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="stat-row">
      <span style={{ fontSize: 13, color: "var(--text-secondary)", fontFamily: "var(--font-body)" }}>{label}</span>
      <span className="num-display" style={{ fontSize: 13, fontWeight: 600, color: color || "var(--text)" }}>{value}</span>
    </div>
  );
}

/* ─── Insight Box ─── */
function InsightBox({ icon, text, color = "var(--accent-light)", textColor = "var(--accent)" }: {
  icon: string; text: string; color?: string; textColor?: string;
}) {
  return (
    <div style={{
      background: color, border: `1px solid ${color}`,
      borderRadius: 12, padding: "12px 16px",
      display: "flex", alignItems: "flex-start", gap: 10,
      marginTop: 12,
    }}>
      <span style={{ fontSize: 16, flexShrink: 0, marginTop: 1 }}>{icon}</span>
      <p style={{ fontSize: 12, color: textColor, lineHeight: 1.6, margin: 0, fontFamily: "var(--font-body)" }}>{text}</p>
    </div>
  );
}

/* ─── Score Ring ─── */
function ScoreRing({ score, label, color }: { score: number; label: string; color: string }) {
  const clampedScore = Math.min(100, Math.max(0, score));
  const circumference = 2 * Math.PI * 44;
  const dash = (clampedScore / 100) * circumference;

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
      <div style={{ position: "relative", width: 110, height: 110 }}>
        <svg width="110" height="110" style={{ transform: "rotate(-90deg)" }}>
          <circle cx="55" cy="55" r="44" fill="none" stroke="rgba(30,20,10,0.08)" strokeWidth="8" />
          <circle cx="55" cy="55" r="44" fill="none" stroke={color} strokeWidth="8"
            strokeDasharray={`${dash} ${circumference}`} strokeLinecap="round"
            style={{ transition: "stroke-dasharray 1.2s ease" }} />
        </svg>
        <div style={{
          position: "absolute", inset: 0, display: "flex",
          flexDirection: "column", alignItems: "center", justifyContent: "center",
        }}>
          <span className="num-display" style={{ fontSize: 22, fontWeight: 800, color, lineHeight: 1 }}>
            {clampedScore.toFixed(0)}
          </span>
          <span style={{ fontSize: 9, color: "var(--text-muted)", fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.06em", marginTop: 2 }}>
            /100
          </span>
        </div>
      </div>
      <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", fontFamily: "var(--font-body)" }}>
        {label}
      </span>
    </div>
  );
}

/* ─── Navbar ─── */
function Navbar() {
  return (
    <nav className="navbar" style={{ padding: "0 24px" }}>
      <div style={{ maxWidth: 1320, margin: "0 auto", height: 60, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        {/* Logo */}
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
          <div style={{
            width: 32, height: 32, borderRadius: 9,
            background: "var(--accent)", display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <span style={{ fontSize: 16 }}>🐑</span>
          </div>
          <div>
            <div style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: 16, color: "var(--text)", lineHeight: 1 }}>
              SheepOrSleep
            </div>
            <div style={{ fontSize: 9, color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase", fontFamily: "var(--font-body)" }}>
              Behavioral Bias Detector
            </div>
          </div>
        </Link>

        {/* Nav Links */}
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <Link href="/" style={{
            padding: "6px 14px", borderRadius: 10, fontSize: 13, fontWeight: 500,
            color: "var(--text-secondary)", textDecoration: "none",
            background: "rgba(30,20,10,0.05)", fontFamily: "var(--font-body)",
          }}>
            Dashboard
          </Link>
          <Link href="/copilot" style={{
            padding: "6px 14px", borderRadius: 10, fontSize: 13, fontWeight: 500,
            color: "var(--accent)", textDecoration: "none",
            background: "var(--accent-light)", fontFamily: "var(--font-body)",
            display: "flex", alignItems: "center", gap: 5,
          }}>
            <Sparkles size={12} />
            AI Copilot
          </Link>
        </div>

        {/* Badge */}
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 7, height: 7, borderRadius: "50%", background: "var(--up-mid)" }} className="pulse-soft" />
          <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            Live · CCK Model
          </span>
        </div>
      </div>
    </nav>
  );
}

/* ─── Footer ─── */
function Footer() {
  return (
    <footer className="footer" style={{ padding: "40px 24px 32px" }}>
      <div style={{ maxWidth: 1320, margin: "0 auto" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 40, marginBottom: 32 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <div style={{ width: 28, height: 28, borderRadius: 8, background: "var(--accent)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <span style={{ fontSize: 14 }}>🐑</span>
              </div>
              <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 15, color: "var(--text)" }}>SheepOrSleep</span>
            </div>
            <p style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.7, fontFamily: "var(--font-body)" }}>
              AI-powered behavioral bias detector for Indian stock markets. Built on the CCK econometric model.
            </p>
          </div>
          <div>
            <p style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12, fontFamily: "var(--font-body)" }}>Analysis</p>
            {["Herding Detection (CCK)", "Panic Score", "Behavior Gap", "Monte Carlo SIP", "Missing Days Impact"].map(item => (
              <p key={item} style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6, fontFamily: "var(--font-body)" }}>{item}</p>
            ))}
          </div>
          <div>
            <p style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12, fontFamily: "var(--font-body)" }}>Coverage</p>
            {["NIFTY 50 (41 stocks)", "NIFTY NEXT 50 (13 stocks)", "Real-time via Yahoo Finance", "Groq AI · llama-3.3-70b"].map(item => (
              <p key={item} style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6, fontFamily: "var(--font-body)" }}>{item}</p>
            ))}
          </div>
        </div>
        <div style={{ borderTop: "1px solid var(--glass-border)", paddingTop: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <p style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "var(--font-body)" }}>
            © 2025 SheepOrSleep · Educational purposes only. Not financial advice.
          </p>
          <p style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
            CCK Model · Behavioral Finance Research
          </p>
        </div>
      </div>
    </footer>
  );
}

/* ═══════════════════════════════════════════════════════
   MAIN PAGE
   ═══════════════════════════════════════════════════════ */
export default function DashboardPage() {
  const [selected, setSelected] = useState<StockInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"candle" | "area">("candle");

  const analyze = async (stock: StockInfo) => {
    setSelected(stock);
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: stock.symbol }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data: AnalysisResult = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch data.");
    }
    setLoading(false);
  };

  const quote = result?.quote;
  const isUp = (quote?.changePct || 0) >= 0;

  /* ── Derived conclusion ── */
  const getConclusion = (): { verdict: string; summary: string; actions: string[]; riskLevel: "low" | "medium" | "high" } => {
    if (!result) return { verdict: "", summary: "", actions: [], riskLevel: "low" };

    const { herding, panic, behaviorGap, monteCarlo } = result;
    const panicScore = panic.panicScore;
    const herdDetected = herding.herdingDetected;
    const gap = Math.abs(behaviorGap.behaviorGap);
    const cost = monteCarlo.costOfPanic.pctLoss;

    const flags: string[] = [];
    if (herdDetected) flags.push("herding");
    if (panicScore > 50) flags.push("panic");
    if (gap > 2) flags.push("behavior-gap");

    if (flags.length === 0) {
      return {
        verdict: "✅ Healthy Market Conditions",
        summary: `${quote?.name} shows rational investor behavior with low herding, controlled panic levels (${panicScore.toFixed(0)}/100), and a manageable behavior gap of ${gap.toFixed(1)}% per year. This suggests the market is pricing this stock fairly without significant emotional distortions.`,
        actions: [
          "Consider a systematic SIP strategy for long-term accumulation.",
          `Staying invested vs. panic selling could protect ~${cost.toFixed(1)}% of your returns.`,
          "Monitor the herding score quarterly; sector news can shift this quickly.",
        ],
        riskLevel: "low",
      };
    }

    if (flags.length >= 2) {
      return {
        verdict: "🚨 High Behavioral Risk Detected",
        summary: `${quote?.name} is showing multiple behavioral red flags: ${herdDetected ? "herding behavior is active" : ""} ${panicScore > 50 ? `with a panic score of ${panicScore.toFixed(0)}/100` : ""}${gap > 2 ? `, and investors are losing ${gap.toFixed(1)}% per year by mistiming entries/exits` : ""}. This is a classic setup for behavioral loss.`,
        actions: [
          "Avoid chasing momentum — the herd often gets burned at peaks.",
          `Your panic behavior could cost you ₹${(monteCarlo.costOfPanic.meanLoss / 1e5).toFixed(1)}L over 10 years vs. a disciplined SIP.`,
          "Consider locking in a SIP mandate to remove emotion from the equation.",
          "Set a clear stop-loss and target before entering any position.",
        ],
        riskLevel: "high",
      };
    }

    return {
      verdict: "⚠️ Moderate Behavioral Signals",
      summary: `${quote?.name} has some behavioral distortions worth watching. ${herdDetected ? "Herding is detectable — sector-wide momentum may be inflating prices." : ""}${panicScore > 50 ? `Panic levels are elevated at ${panicScore.toFixed(0)}/100.` : ""}${gap > 2 ? `The ${gap.toFixed(1)}% annual behavior gap suggests investors are timing poorly.` : ""}`,
      actions: [
        "Proceed with caution and position size accordingly.",
        "A SIP beats market timing here — the data supports it strongly.",
        `If currently holding, review your thesis rather than reacting to price action.`,
      ],
      riskLevel: "medium",
    };
  };

  const conclusion = result ? getConclusion() : null;

  const riskColors = {
    low: { bg: "var(--up-bg)", text: "var(--up)", border: "var(--up-border)" },
    medium: { bg: "var(--warn-bg)", text: "var(--warn)", border: "rgba(217,119,6,0.15)" },
    high: { bg: "var(--down-bg)", text: "var(--down)", border: "var(--down-border)" },
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar />

      {/* Hero Section */}
      <div style={{
        background: "var(--glass-heavy)", borderBottom: "1px solid var(--glass-border)",
        padding: "48px 24px",
      }}>
        <div style={{ maxWidth: 1320, margin: "0 auto" }}>
          <div className="fade-up delay-1">
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <span className="badge badge-info">CCK Econometric Model</span>
              <span className="badge badge-neutral">54 Indian Stocks</span>
              <span className="badge badge-neutral">Powered by Groq AI</span>
            </div>
            <h1 style={{
              fontFamily: "var(--font-display)", fontWeight: 800,
              fontSize: "clamp(28px, 4vw, 44px)", color: "var(--text)",
              lineHeight: 1.1, letterSpacing: "-0.03em", marginBottom: 12,
            }}>
              Are you following the herd<br />
              <span style={{ color: "var(--accent)" }}>or making informed decisions?</span>
            </h1>
            <p style={{ fontSize: 15, color: "var(--text-secondary)", maxWidth: 560, lineHeight: 1.7, fontFamily: "var(--font-body)" }}>
              Detect herding, panic selling, and behavioral gaps in your Indian stock picks using rigorous econometric analysis and AI.
            </p>
          </div>

          <div className="fade-up delay-3" style={{ marginTop: 32, display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
            <StockSelector selected={selected} onSelect={analyze} />
            {selected && !loading && !result && (
              <button className="btn-primary" onClick={() => analyze(selected)} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Activity size={15} /> Analyze
              </button>
            )}
            {loading && (
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Loader2 size={16} className="spin-slow" style={{ color: "var(--accent)" }} />
                <span style={{ fontSize: 13, color: "var(--text-secondary)", fontFamily: "var(--font-body)" }}>
                  Fetching data & running CCK model...
                </span>
              </div>
            )}
          </div>

          {error && (
            <div className="fade-in" style={{
              marginTop: 16, padding: "12px 16px", borderRadius: 12,
              background: "var(--down-bg)", border: "1px solid var(--down-border)",
              display: "flex", alignItems: "center", gap: 8,
            }}>
              <AlertTriangle size={14} style={{ color: "var(--down)", flexShrink: 0 }} />
              <span style={{ fontSize: 13, color: "var(--down)", fontFamily: "var(--font-body)" }}>{error}</span>
            </div>
          )}
        </div>
      </div>

      {/* ── Loading Skeleton ── */}
      {loading && (
        <div style={{ maxWidth: 1320, margin: "32px auto", padding: "0 24px", width: "100%" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 24 }}>
            {[...Array(4)].map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 100, borderRadius: 20 }} />
            ))}
          </div>
          <div className="skeleton" style={{ height: 480, borderRadius: 24 }} />
        </div>
      )}

      {/* ══════════════ RESULTS ══════════════ */}
      {result && quote && !loading && (
        <div style={{ maxWidth: 1320, margin: "32px auto", padding: "0 24px 60px", width: "100%", display: "flex", flexDirection: "column", gap: 24 }}>

          {/* ── Stock Header ── */}
          <div className="glass-card fade-up delay-1" style={{ padding: "24px 28px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{
                  width: 52, height: 52, borderRadius: 14,
                  background: isUp ? "var(--up-bg)" : "var(--down-bg)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 24,
                }}>
                  {isUp ? "📈" : "📉"}
                </div>
                <div>
                  <div style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: 22, color: "var(--text)", lineHeight: 1 }}>
                    {quote.name}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4, display: "flex", gap: 8, alignItems: "center", fontFamily: "var(--font-mono)" }}>
                    <span>{quote.symbol.replace(".NS", "")}</span>
                    <span style={{ color: "var(--glass-border)" }}>·</span>
                    <span>{quote.sector}</span>
                  </div>
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
                <div style={{ textAlign: "right" }}>
                  <div className="num-display" style={{ fontSize: 32, fontWeight: 800, color: "var(--text)", lineHeight: 1 }}>
                    ₹{quote.price.toLocaleString("en-IN", { maximumFractionDigits: 2 })}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, justifyContent: "flex-end", marginTop: 4 }}>
                    {isUp
                      ? <ArrowUpRight size={14} style={{ color: "var(--up-mid)" }} />
                      : <ArrowDownRight size={14} style={{ color: "var(--down-mid)" }} />
                    }
                    <span className={`badge ${isUp ? "badge-up" : "badge-down"}`}>
                      {fmtPct(quote.changePct)} ({fmtPct(quote.change, 2)})
                    </span>
                  </div>
                </div>
                <button
                  className="btn-ghost"
                  onClick={() => analyze(selected!)}
                  style={{ display: "flex", alignItems: "center", gap: 6 }}
                >
                  <RefreshCw size={13} /> Refresh
                </button>
              </div>
            </div>

            {/* Quick stats */}
            <div style={{
              display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 12, marginTop: 20,
              paddingTop: 20, borderTop: "1px solid var(--glass-border)",
            }}>
              {[
                { label: "52W High", value: `₹${quote.week52High?.toLocaleString("en-IN", { maximumFractionDigits: 0 })}` },
                { label: "52W Low", value: `₹${quote.week52Low?.toLocaleString("en-IN", { maximumFractionDigits: 0 })}` },
                { label: "P/E Ratio", value: quote.peRatio?.toFixed(1) || "—" },
                { label: "Mkt Cap", value: fmt(quote.marketCap) },
                { label: "Volume", value: `${(quote.volume / 1e6).toFixed(2)}M` },
                { label: "Avg Volume", value: `${(quote.avgVolume / 1e6).toFixed(2)}M` },
              ].map(({ label, value }) => (
                <div key={label} style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4, fontFamily: "var(--font-body)" }}>
                    {label}
                  </div>
                  <div className="num-display" style={{ fontSize: 14, fontWeight: 700, color: "var(--text)" }}>
                    {value}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ── 4 Behavioral Score Cards ── */}
          <div className="fade-up delay-2" style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
            <MetricCard
              label="Herding Score"
              value={result.herding.herdingDetected ? "Active" : "None"}
              sub={`γ₂ = ${result.herding.gamma2?.toFixed(4)} | R² = ${result.herding.rSquared?.toFixed(3)}`}
              color={result.herding.herdingDetected ? "var(--down)" : "var(--up)"}
              icon={result.herding.herdingDetected
                ? <AlertTriangle size={14} style={{ color: "var(--down)" }} />
                : <CheckCircle2 size={14} style={{ color: "var(--up)" }} />
              }
            />
            <MetricCard
              label="Panic Score"
              value={`${result.panic.panicScore?.toFixed(0)} / 100`}
              sub={result.panic.level}
              color={result.panic.panicScore > 60 ? "var(--down)" : result.panic.panicScore > 35 ? "var(--warn)" : "var(--up)"}
              icon={<Zap size={14} style={{ color: result.panic.panicScore > 60 ? "var(--down)" : result.panic.panicScore > 35 ? "var(--warn)" : "var(--up)" }} />}
            />
            <MetricCard
              label="Behavior Gap"
              value={`${Math.abs(result.behaviorGap.behaviorGap)?.toFixed(2)}% / yr`}
              sub={result.behaviorGap.gapInterpretation || "Annual return lost"}
              color={Math.abs(result.behaviorGap.behaviorGap) > 3 ? "var(--down)" : Math.abs(result.behaviorGap.behaviorGap) > 1 ? "var(--warn)" : "var(--up)"}
              icon={<Target size={14} style={{ color: "var(--accent)" }} />}
            />
            <MetricCard
              label="SIP Advantage"
              value={`${result.monteCarlo.costOfPanic.winRate?.toFixed(0)}%`}
              sub="Probability SIP beats panic"
              color="var(--up)"
              icon={<TrendingUp size={14} style={{ color: "var(--up)" }} />}
            />
          </div>

          {/* ── Price Chart + AI Copilot ── */}
          <div className="fade-up delay-2" style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: 24 }}>

            {/* Price Section */}
            <div className="glass-card">
              <div style={{ padding: "20px 24px 0" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                  <div>
                    <h2 className="section-title">Price Chart</h2>
                    <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2, fontFamily: "var(--font-body)" }}>
                      Last 6 months · {result.priceChart.length} trading days
                    </p>
                  </div>
                  <div className="tab-bar" style={{ minWidth: 160 }}>
                    <button className={`tab-item ${activeTab === "candle" ? "active" : ""}`} onClick={() => setActiveTab("candle")}>
                      Candlestick
                    </button>
                    <button className={`tab-item ${activeTab === "area" ? "active" : ""}`} onClick={() => setActiveTab("area")}>
                      Area
                    </button>
                  </div>
                </div>
              </div>
              <div style={{ padding: "0 12px 8px" }}>
                {activeTab === "candle"
                  ? <CandlestickChart data={result.priceChart} />
                  : <PriceAreaChart data={result.priceChart} />
                }
              </div>
              {/* Volume below candles */}
              <div style={{ padding: "0 12px 16px", borderTop: "1px solid var(--glass-border)" }}>
                <p style={{ fontSize: 10, color: "var(--text-dim)", padding: "8px 12px 4px", fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.08em" }}>Volume</p>
                <VolumeBarChart data={result.priceChart} />
              </div>
            </div>

            {/* AI Copilot */}
            <AICopilotPanel result={result} />
          </div>

          {/* ── Herding + Panic row ── */}
          <div className="fade-up delay-3" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>

            {/* Herding Section */}
            <Section
              title="Herding Behavior (CCK Model)"
              subtitle="Cross-Sectional Absolute Deviation analysis"
              icon={<Brain size={15} style={{ color: "var(--accent)" }} />}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 24, marginBottom: 20 }}>
                <ScoreRing
                  score={result.herding.intensity * 100}
                  label="Intensity"
                  color={result.herding.herdingDetected ? "var(--down-mid)" : "var(--up-mid)"}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ marginBottom: 12 }}>
                    <span className={`badge ${result.herding.herdingDetected ? "badge-down" : "badge-up"}`} style={{ fontSize: 12, padding: "5px 14px" }}>
                      {result.herding.herdingDetected ? "🐑 Herding Detected" : "✅ No Herding"}
                    </span>
                  </div>
                  <StatRow label="γ₂ Coefficient" value={result.herding.gamma2?.toFixed(4) || "—"} color={result.herding.herdingDetected ? "var(--down)" : "var(--up)"} />
                  <StatRow label="γ₁ Coefficient" value={result.herding.gamma1?.toFixed(4) || "—"} />
                  <StatRow label="R-Squared" value={result.herding.rSquared?.toFixed(4) || "—"} />
                  <StatRow label="t-Statistic" value={result.herding.tStat?.toFixed(3) || "—"} />
                  <StatRow label="p-Value" value={result.herding.pValue?.toFixed(4) || "—"} color={result.herding.pValue < 0.05 ? "var(--down)" : "var(--up)"} />
                  <StatRow label="Observations" value={result.herding.observations || "—"} />
                </div>
              </div>

              <div style={{ marginBottom: 16 }}>
                <p style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 8, fontFamily: "var(--font-body)" }}>
                  CSAD vs. |Market Return| — concave curve = herding present
                </p>
                <CSADScatterPlot data={result.herding.csadData} />
              </div>

              <InsightBox
                icon={result.herding.herdingDetected ? "⚠️" : "✅"}
                text={result.herding.herdingDetected
                  ? `Herding is statistically significant (γ₂ = ${result.herding.gamma2?.toFixed(4)}, p = ${result.herding.pValue?.toFixed(4)}). Investors in ${result.herding.sector} are mimicking the crowd — valuations may be distorted by emotion.`
                  : `No herding detected in ${result.herding.sector}. Individual investors appear to be making independent decisions, which generally leads to more efficient pricing.`
                }
                color={result.herding.herdingDetected ? "var(--down-bg)" : "var(--up-bg)"}
                textColor={result.herding.herdingDetected ? "var(--down)" : "var(--up)"}
              />
            </Section>

            {/* Panic Section */}
            <Section
              title="Panic Selling Detection"
              subtitle="Volume anomaly & volatility regime analysis"
              icon={<Zap size={15} style={{ color: "var(--accent)" }} />}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 24, marginBottom: 20 }}>
                <ScoreRing
                  score={result.panic.panicScore}
                  label="Panic Score"
                  color={result.panic.panicScore > 60 ? "var(--down-mid)" : result.panic.panicScore > 35 ? "var(--warn-mid)" : "var(--up-mid)"}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ marginBottom: 12 }}>
                    <span className={`badge ${result.panic.panicScore > 60 ? "badge-down" : result.panic.panicScore > 35 ? "badge-warn" : "badge-up"}`} style={{ fontSize: 12, padding: "5px 14px" }}>
                      {result.panic.level}
                    </span>
                  </div>
                  {Object.entries(result.panic.factors).map(([key, value]) => (
                    <div key={key} style={{ marginBottom: 8 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                        <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-body)" }}>
                          {key.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase())}
                        </span>
                        <span className="num-display" style={{ fontSize: 11, fontWeight: 600, color: "var(--text)" }}>{value?.toFixed(1)}</span>
                      </div>
                      <div className="progress-bar">
                        <div className="progress-bar-fill" style={{
                          width: `${Math.min(100, value)}%`,
                          background: value > 60 ? "var(--down-mid)" : value > 35 ? "var(--warn-mid)" : "var(--up-mid)",
                        }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <p style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 8, fontFamily: "var(--font-body)" }}>
                Daily volume with panic days highlighted
              </p>
              <PanicVolumeChart data={result.panic.volumeData} />

              <InsightBox
                icon={result.panic.panicScore > 60 ? "😰" : result.panic.panicScore > 35 ? "⚠️" : "😌"}
                text={`Panic score: ${result.panic.panicScore.toFixed(0)}/100. Current drawdown: ${result.panic.details.currentDrawdown?.toFixed(1)}%. Volatility is ${result.panic.details.currentVolatility > result.panic.details.avgVolatility * 1.3 ? "elevated" : "normal"} at ${(result.panic.details.currentVolatility * 100).toFixed(2)}% vs avg ${(result.panic.details.avgVolatility * 100).toFixed(2)}%.`}
                color={result.panic.panicScore > 60 ? "var(--down-bg)" : result.panic.panicScore > 35 ? "var(--warn-bg)" : "var(--up-bg)"}
                textColor={result.panic.panicScore > 60 ? "var(--down)" : result.panic.panicScore > 35 ? "var(--warn)" : "var(--up)"}
              />
            </Section>
          </div>

          {/* ── Behavior Gap + Monte Carlo ── */}
          <div className="fade-up delay-4" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>

            {/* Behavior Gap */}
            <Section
              title="Investor Behavior Gap"
              subtitle="What investors earn vs. what the investment returns"
              icon={<Target size={15} style={{ color: "var(--accent)" }} />}
            >
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
                <div className="glass-inset" style={{ padding: "14px 16px", textAlign: "center" }}>
                  <p style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6, fontFamily: "var(--font-body)" }}>Investment CAGR</p>
                  <p className="num-display" style={{ fontSize: 22, fontWeight: 800, color: "var(--up)" }}>{result.behaviorGap.investmentCagr?.toFixed(2)}%</p>
                  <p style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 3, fontFamily: "var(--font-body)" }}>What stock actually returned</p>
                </div>
                <div className="glass-inset" style={{ padding: "14px 16px", textAlign: "center" }}>
                  <p style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6, fontFamily: "var(--font-body)" }}>Investor CAGR</p>
                  <p className="num-display" style={{ fontSize: 22, fontWeight: 800, color: "var(--warn)" }}>{result.behaviorGap.investorCagr?.toFixed(2)}%</p>
                  <p style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 3, fontFamily: "var(--font-body)" }}>What you likely earned</p>
                </div>
              </div>

              <div style={{ textAlign: "center", margin: "16px 0" }}>
                <div className="num-display" style={{ fontSize: 36, fontWeight: 800, color: Math.abs(result.behaviorGap.behaviorGap) > 2 ? "var(--down)" : "var(--warn)" }}>
                  {fmtPct(result.behaviorGap.behaviorGap, 2)} / yr
                </div>
                <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4, fontFamily: "var(--font-body)" }}>
                  Annual behavior gap · {result.behaviorGap.periodYears?.toFixed(1)} year period
                </p>
              </div>

              <StatRow label="Total Investment Return" value={fmtPct(result.behaviorGap.investmentReturn)} color="var(--up)" />
              <StatRow label="Analysis Period" value={`${result.behaviorGap.periodYears?.toFixed(1)} years`} />

              <InsightBox
                icon="💡"
                text={result.behaviorGap.gapInterpretation || `Investors in ${quote.name} underperformed the stock itself by ${Math.abs(result.behaviorGap.behaviorGap).toFixed(2)}% per year due to emotional buying and selling.`}
                color="var(--accent-light)"
                textColor="var(--accent)"
              />

              {/* Missing Best Days */}
              <div style={{ marginTop: 20 }}>
                <p style={{ fontSize: 13, fontWeight: 600, color: "var(--text)", marginBottom: 4, fontFamily: "var(--font-display)" }}>
                  Cost of Missing Best Days
                </p>
                <p style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 12, fontFamily: "var(--font-body)" }}>
                  Impact of being out of market during top trading days
                </p>
                <MissingDaysChart data={result.missingDays} />
              </div>
            </Section>

            {/* Monte Carlo */}
            <Section
              title="Monte Carlo SIP Simulation"
              subtitle="10,000 scenarios — SIP vs. panic selling"
              icon={<BarChart2 size={15} style={{ color: "var(--accent)" }} />}
            >
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
                <div className="glass-inset" style={{ padding: "14px 16px" }}>
                  <p style={{ fontSize: 10, color: "var(--up)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8, fontFamily: "var(--font-body)" }}>✅ Disciplined SIP</p>
                  <StatRow label="Median" value={fmt(result.monteCarlo.sip.median)} />
                  <StatRow label="P10 (pessimistic)" value={fmt(result.monteCarlo.sip.p10)} />
                  <StatRow label="P90 (optimistic)" value={fmt(result.monteCarlo.sip.p90)} />
                </div>
                <div className="glass-inset" style={{ padding: "14px 16px" }}>
                  <p style={{ fontSize: 10, color: "var(--down)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8, fontFamily: "var(--font-body)" }}>😰 Panic Seller</p>
                  <StatRow label="Median" value={fmt(result.monteCarlo.panic.median)} />
                  <StatRow label="P10 (pessimistic)" value={fmt(result.monteCarlo.panic.p10)} />
                  <StatRow label="P90 (optimistic)" value={fmt(result.monteCarlo.panic.p90)} />
                </div>
              </div>

              <MCHistogram data={result.monteCarlo.histogram} />

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginTop: 16 }}>
                {[
                  { label: "Invested Amount", value: fmt(result.monteCarlo.totalInvested), color: "var(--text)" },
                  { label: "Mean Cost of Panic", value: fmt(result.monteCarlo.costOfPanic.meanLoss), color: "var(--down)" },
                  { label: "SIP Win Rate", value: `${result.monteCarlo.costOfPanic.winRate?.toFixed(0)}%`, color: "var(--up)" },
                ].map(({ label, value, color }) => (
                  <div key={label} className="glass-inset" style={{ padding: "10px 12px", textAlign: "center" }}>
                    <p style={{ fontSize: 9, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4, fontFamily: "var(--font-body)" }}>{label}</p>
                    <p className="num-display" style={{ fontSize: 15, fontWeight: 700, color }}>{value}</p>
                  </div>
                ))}
              </div>

              <InsightBox
                icon="💰"
                text={`Over ${result.monteCarlo.years} years, a disciplined SIP investor would beat a panic seller in ${result.monteCarlo.costOfPanic.winRate?.toFixed(0)}% of simulated scenarios. The median cost of panic: ${fmt(result.monteCarlo.costOfPanic.meanLoss)} (${result.monteCarlo.costOfPanic.pctLoss?.toFixed(1)}% of portfolio).`}
                color="var(--up-bg)"
                textColor="var(--up)"
              />
            </Section>
          </div>

          {/* ── CONCLUSION CARD ── */}
          {conclusion && (
            <div className="conclusion-card fade-up delay-5" style={{ padding: "32px 36px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
                <div style={{
                  width: 40, height: 40, borderRadius: 12,
                  background: riskColors[conclusion.riskLevel].bg,
                  border: `1px solid ${riskColors[conclusion.riskLevel].border}`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 20,
                }}>
                  {conclusion.riskLevel === "low" ? "✅" : conclusion.riskLevel === "medium" ? "⚠️" : "🚨"}
                </div>
                <div>
                  <div style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: 22, color: "var(--text)", letterSpacing: "-0.02em" }}>
                    Our Verdict
                  </div>
                  <div style={{ fontSize: 13, color: riskColors[conclusion.riskLevel].text, fontWeight: 600, marginTop: 2, fontFamily: "var(--font-body)" }}>
                    {conclusion.verdict}
                  </div>
                </div>
                <div style={{ marginLeft: "auto" }}>
                  <span className={`badge ${conclusion.riskLevel === "low" ? "badge-up" : conclusion.riskLevel === "medium" ? "badge-warn" : "badge-down"}`} style={{ fontSize: 12, padding: "6px 16px" }}>
                    {conclusion.riskLevel === "low" ? "Low Risk" : conclusion.riskLevel === "medium" ? "Moderate Risk" : "High Risk"}
                  </span>
                </div>
              </div>

              <p style={{ fontSize: 14, color: "var(--text-secondary)", lineHeight: 1.8, marginBottom: 24, fontFamily: "var(--font-body)" }}>
                {conclusion.summary}
              </p>

              <div>
                <p style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12, fontFamily: "var(--font-body)" }}>
                  Recommended Actions
                </p>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {conclusion.actions.map((action, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
                      <div style={{
                        width: 22, height: 22, borderRadius: 6, flexShrink: 0,
                        background: "var(--accent-light)", border: "1px solid rgba(99,102,241,0.15)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700, color: "var(--accent)",
                      }}>
                        {i + 1}
                      </div>
                      <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6, margin: 0, fontFamily: "var(--font-body)" }}>
                        {action}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{
                marginTop: 24, paddingTop: 20, borderTop: "1px solid var(--glass-border)",
                display: "flex", alignItems: "center", justifyContent: "space-between",
              }}>
                <p style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "var(--font-body)" }}>
                  Analysis based on CCK econometric model · Not financial advice
                </p>
                <Link href="/copilot" style={{
                  display: "flex", alignItems: "center", gap: 6, textDecoration: "none",
                  fontSize: 13, fontWeight: 600, color: "var(--accent)", fontFamily: "var(--font-body)",
                }}>
                  <Sparkles size={13} />
                  Ask AI for deeper insights
                  <ChevronRight size={13} />
                </Link>
              </div>
            </div>
          )}

          {/* ── Data Disclaimer ── */}
          <div className="glass-subtle fade-up delay-6" style={{ padding: "14px 20px", display: "flex", alignItems: "center", gap: 10 }}>
            <Info size={14} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
            <p style={{ fontSize: 11, color: "var(--text-muted)", lineHeight: 1.6, fontFamily: "var(--font-body)" }}>
              Data sourced from Yahoo Finance via yfinance. CCK herding model based on Chang, Cheng & Khorana (2000).
              Analysis is for educational purposes only and does not constitute financial advice.
              Past performance does not guarantee future results.
            </p>
          </div>
        </div>
      )}

      {/* ── Empty State (no stock selected) ── */}
      {!loading && !result && !error && (
        <div style={{ maxWidth: 1320, margin: "60px auto", padding: "0 24px", width: "100%", flex: 1 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20, marginBottom: 40 }}>
            {[
              {
                icon: "🐑", title: "Herding Detection",
                desc: "The CCK model measures CSAD (Cross-Sectional Absolute Deviation) against squared market returns. A negative γ₂ coefficient indicates that investors are converging — following the herd instead of independent analysis.",
                badge: "CCK Econometric Model",
              },
              {
                icon: "😰", title: "Panic Score",
                desc: "A composite 0–100 score built from volume anomaly z-scores, price-volume divergence, drawdown severity, and volatility regime. Scores above 60 indicate widespread fear and irrational selling.",
                badge: "Multi-factor Analysis",
              },
              {
                icon: "💰", title: "Monte Carlo SIP",
                desc: "10,000 simulated investment paths compare a disciplined SIP investor against a panic-prone one. The result: the probability and rupee cost of letting emotions drive your portfolio decisions.",
                badge: "10,000 Simulations",
              },
            ].map(({ icon, title, desc, badge }) => (
              <div key={title} className="glass-card" style={{ padding: "24px" }}>
                <div style={{ fontSize: 32, marginBottom: 14 }}>{icon}</div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                  <h3 style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 16, color: "var(--text)", margin: 0 }}>{title}</h3>
                </div>
                <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: 14, fontFamily: "var(--font-body)" }}>{desc}</p>
                <span className="badge badge-info">{badge}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      <Footer />
    </div>
  );
}