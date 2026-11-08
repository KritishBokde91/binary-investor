"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import Header from "@/app/components/layout/Header";
import MobileTabBar from "@/app/components/layout/MobileTabBar";
import Footer from "@/app/components/layout/Footer";
import SemicircleGauge from "@/app/components/ui/SemicircleGauge";
import StatusChip from "@/app/components/ui/StatusChip";
import RangeBar52W from "@/app/components/ui/RangeBar52W";
import MetricTile from "@/app/components/ui/MetricTile";
import NoticeBanner from "@/app/components/ui/NoticeBanner";
import SkeletonLoader from "@/app/components/ui/SkeletonLoader";
import StockSelectorModal from "@/app/components/StockSelectorModal";
import AICopilotDrawer from "@/app/components/AICopilotDrawer";
import DegradedStateBanner from "@/app/components/DegradedStateBanner";
import PriceVolumeChart from "@/app/components/charts/PriceVolumeChart";
import CSADScatterChart from "@/app/components/charts/CSADScatterChart";
import MissingDaysBarChart from "@/app/components/charts/MissingDaysBarChart";
import MonteCarloHistogram from "@/app/components/charts/MonteCarloHistogram";

import { STOCK_UNIVERSE } from "@/app/lib/stockUniverse";
import type { StockInfo, AnalysisResult } from "@/app/lib/types";

// Base API URL for SSR or direct access fallback
export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DashboardPage() {
  const [selectedStock, setSelectedStock] = useState<StockInfo>(
    STOCK_UNIVERSE.find((s) => s.symbol === "MARUTI.NS") || STOCK_UNIVERSE[0]
  );
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals & Drawers
  const [isStockModalOpen, setIsStockModalOpen] = useState(false);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [mobileTab, setMobileTab] = useState<"dashboard" | "copilot" | "learn">("dashboard");

  // Detailed Analysis Tab: 'herd' | 'panic' | 'missing' | 'sip'
  const [activeAnalysisTab, setActiveAnalysisTab] = useState<
    "herd" | "panic" | "missing" | "sip"
  >("herd");

  const abortCtrl = useRef<AbortController | null>(null);

  const analyzeStock = useCallback(async (stock: StockInfo) => {
    abortCtrl.current?.abort();
    const ctrl = (abortCtrl.current = new AbortController());

    setSelectedStock(stock);
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        signal: ctrl.signal,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: stock.symbol }),
      });

      if (!res.ok) {
        let errorDetail = `Server error: ${res.status}`;
        try {
          const errJson = await res.json();
          if (errJson.detail) {
            errorDetail =
              typeof errJson.detail === "string"
                ? errJson.detail
                : errJson.detail.reason || errorDetail;
          } else if (errJson.error) {
            errorDetail = errJson.error;
          }
        } catch {
          // ignore json parse error
        }
        throw new Error(errorDetail);
      }

      const data: AnalysisResult = await res.json();
      setResult(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        if (err.name !== "AbortError") {
          setError(err.message || "Failed to load market data for stock.");
        }
      } else {
        setError("Failed to load market data for stock.");
      }
    } finally {
      if (!ctrl.signal.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    analyzeStock(selectedStock);
    return () => {
      abortCtrl.current?.abort();
    };
  }, [analyzeStock, selectedStock]);

  // Format Large Currency (Indian Lakhs / Crores)
  const fmt = (n: number | undefined | null) => {
    if (!n && n !== 0) return "—";
    if (n >= 1e12) return `₹${(n / 1e12).toFixed(2)} Lakh Cr`;
    if (n >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`;
    if (n >= 1e5) return `₹${(n / 1e5).toFixed(2)} Lakhs`;
    return `₹${n.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
  };

  const fmtShares = (n: number | undefined | null) => {
    if (!n && n !== 0) return "—";
    if (n >= 1e7) return `${(n / 1e7).toFixed(2)} Cr`;
    if (n >= 1e5) return `${(n / 1e5).toFixed(1)} Lakh`;
    if (n >= 1e3) return `${(n / 1e3).toFixed(0)}k`;
    return `${n}`;
  };

  const quote = result?.quote;
  const isUp = (quote?.change || 0) >= 0;

  // Empirical Health Check: All inputs must be verified healthy to render verdicts
  const isHealthy =
    result?.status === "ok" &&
    quote &&
    quote.price > 0 &&
    result.priceChart &&
    result.priceChart.length > 0 &&
    result.panic?.level !== "NO DATA" &&
    result.behaviorGap?.gapInterpretation !== "Insufficient data" &&
    !result.herding?.error;

  return (
    <div className="min-h-screen flex flex-col bg-surface text-on-surface antialiased transition-colors">
      {/* 1. Header Navigation & Sub-header Status */}
      <Header
        selectedStock={selectedStock}
        onOpenStockSelector={() => setIsStockModalOpen(true)}
        onOpenCopilot={() => setIsCopilotOpen(true)}
        asOfDate={result?.as_of}
      />

      {/* Main Content Area */}
      <main className="w-full pt-28 pb-24 sm:pb-16 flex-1">
        <div className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8">
          {/* Breadcrumb Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2 py-2 mb-4 text-xs font-medium">
            <div className="flex items-center gap-2 text-on-surface-variant whitespace-nowrap overflow-hidden">
              <span className="hover:text-primary transition-colors cursor-pointer">
                NSE Equities
              </span>
              <span className="text-outline">/</span>
              <span className="hover:text-primary transition-colors cursor-pointer truncate">
                {selectedStock.sector} Sector
              </span>
              <span className="text-outline">/</span>
              <span className="text-on-surface font-semibold">
                {selectedStock.symbol}
              </span>
              <span className="ml-2 px-2.5 py-0.5 rounded-full bg-surface-container-high text-on-surface-variant text-[11px] font-medium border border-surface-container-highest shrink-0">
                End-of-day data, delayed
              </span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 text-on-surface-variant text-[11px] whitespace-nowrap">
              <span className="material-symbols-outlined text-[15px] text-primary">
                analytics
              </span>
              <span>Behavioral Overview</span>
            </div>
          </div>

          {/* Loading Skeleton */}
          {loading && <SkeletonLoader />}

          {/* Error Banner with Retry */}
          {!loading && error && (
            <div className="bg-red-50 dark:bg-red-950/40 border border-red-300 dark:border-red-800 rounded-2xl p-6 shadow-sm my-6">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-[24px] text-error">
                    error
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-red-900 dark:text-red-200">
                      Unable to Load Stock Analysis
                    </h3>
                    <p className="text-xs text-red-800/90 dark:text-red-300 mt-0.5">
                      {error}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => analyzeStock(selectedStock)}
                  className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-colors shadow-xs cursor-pointer whitespace-nowrap"
                >
                  Retry Analysis
                </button>
              </div>
            </div>
          )}

          {/* Degraded State Warning (when backend reports partial/degraded data) */}
          {!loading && result && !isHealthy && (
            <DegradedStateBanner
              reason={result.reason}
              onRetry={() => analyzeStock(selectedStock)}
            />
          )}

          {/* Main Loaded View */}
          {!loading && result && quote && (
            <div className="space-y-8 animate-in fade-in duration-300">
              {/* ─────────────────────────────────────────────────────────────
                  SECTION 1: Stock Overview Hero Card
                 ───────────────────────────────────────────────────────────── */}
              <section className="bg-surface-container-lowest dark:bg-surface-container-lowest/80 rounded-2xl shadow-sm border border-surface-container-high/60 p-5 sm:p-7 md:p-8">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
                  {/* Left: Stock Identity & Price */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1 flex-wrap">
                      <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-on-surface tracking-tight whitespace-nowrap">
                        {quote.name}
                      </h1>
                      <span className="bg-surface-container text-on-surface font-bold text-xs sm:text-sm px-2.5 py-1 rounded-md border border-surface-container-high shrink-0">
                        {quote.symbol.replace(".NS", "")}
                      </span>
                    </div>

                    <p className="text-xs sm:text-sm text-on-surface-variant font-normal">
                      {selectedStock.sector} Sector • Flagship Index {selectedStock.index}
                    </p>

                    {/* Price + Change Badge */}
                    <div className="flex items-baseline gap-3 mt-4 flex-wrap">
                      <span className="text-3xl sm:text-4xl font-extrabold text-on-surface tracking-tight leading-none tabular-nums whitespace-nowrap">
                        ₹{quote.price.toLocaleString("en-IN", { maximumFractionDigits: 2 })}
                      </span>
                      <div
                        className={`inline-flex items-center gap-1 font-semibold text-xs sm:text-sm px-3 py-1 rounded-full whitespace-nowrap border shadow-xs ${
                          isUp
                            ? "text-emerald-700 bg-emerald-50 border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800"
                            : "text-red-700 bg-red-50 border-red-200 dark:bg-red-950/60 dark:text-red-300 dark:border-red-800"
                        }`}
                      >
                        <span className="material-symbols-outlined text-[16px]">
                          {isUp ? "trending_up" : "trending_down"}
                        </span>
                        <span className="tabular-nums">
                          {quote.change >= 0 ? "+" : ""}₹{Math.abs(quote.change).toFixed(2)} (
                          {quote.changePct >= 0 ? "+" : ""}
                          {quote.changePct.toFixed(2)}%)
                        </span>
                        <span className="text-[10px] opacity-75 font-normal">today</span>
                      </div>
                    </div>
                  </div>

                  {/* Right: Quick Action Controls */}
                  <div className="flex items-center gap-3 self-start lg:self-center">
                    <button
                      type="button"
                      onClick={() => setIsStockModalOpen(true)}
                      className="px-4 py-2 rounded-xl bg-surface-container hover:bg-surface-container-high text-on-surface text-xs font-bold transition-colors border border-surface-container-high flex items-center gap-1.5 cursor-pointer"
                    >
                      <span className="material-symbols-outlined text-[16px]">swap_horiz</span>
                      <span>Change Stock</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => analyzeStock(selectedStock)}
                      className="px-4 py-2 rounded-xl bg-primary-container text-on-primary text-xs font-bold transition-colors shadow-xs flex items-center gap-1.5 cursor-pointer hover:bg-indigo-700"
                    >
                      <span className="material-symbols-outlined text-[16px]">refresh</span>
                      <span>Refresh</span>
                    </button>
                  </div>
                </div>

                {/* 52-Week Range Slider Card */}
                <RangeBar52W
                  currentPrice={quote.price}
                  low52W={quote.week52Low}
                  high52W={quote.week52High}
                />

                {/* 4 Key Stat Metric Tiles */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mt-4">
                  <MetricTile
                    label="Market Capitalization"
                    value={fmt(quote.marketCap)}
                    annotation={`${selectedStock.index} Large Cap`}
                  />
                  <MetricTile
                    label="P/E Ratio (TTM)"
                    value={quote.peRatio > 0 ? `${quote.peRatio.toFixed(1)}x` : "—"}
                    annotation="Trailing Twelve Months"
                  />
                  <MetricTile
                    label="30-Day Avg Volume"
                    value={fmtShares(quote.avgVolume)}
                    annotation="Orderly Institutional Flow"
                  />
                  <MetricTile
                    label="Day Trading Range"
                    value={
                      quote.dayLow > 0
                        ? `₹${Math.round(quote.dayLow).toLocaleString("en-IN")} – ₹${Math.round(
                            quote.dayHigh
                          ).toLocaleString("en-IN")}`
                        : "—"
                    }
                    annotation="Today's Low & High"
                  />
                </div>
              </section>

              {/* ─────────────────────────────────────────────────────────────
                  SECTION 2: "At a Glance" Behavioral Gauges Row
                 ───────────────────────────────────────────────────────────── */}
              <section className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl sm:text-2xl font-bold text-on-surface">
                      At a Glance: Behavioral Gauges
                    </h2>
                    <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
                      Statistical clarity designed to remove emotional bias before executing trades.
                    </p>
                  </div>
                  <div className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-primary bg-indigo-50 border border-indigo-200 dark:bg-indigo-950/60 dark:border-indigo-800 dark:text-indigo-300 px-3 py-1 rounded-full whitespace-nowrap">
                    <span className="material-symbols-outlined text-[16px]">psychology</span>
                    <span>Behavioral Calibration</span>
                  </div>
                </div>

                {/* Desktop: 3-column Grid / Mobile: Swipeable Carousel */}
                <div className="flex md:grid md:grid-cols-3 gap-4 sm:gap-5 overflow-x-auto pb-2 -mx-4 px-4 sm:mx-0 sm:px-0 snap-x snap-mandatory scrollbar-none">
                  {/* Gauge 1: Herd Behavior */}
                  <div className="w-[84vw] max-w-[320px] md:w-auto flex-shrink-0 snap-center bg-surface-container-lowest dark:bg-surface-container-lowest/80 rounded-2xl shadow-sm border border-surface-container-high/60 p-5 sm:p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-base sm:text-lg font-bold text-on-surface">
                          Herd Behavior
                        </h3>
                        <StatusChip
                          label={result.herding.herdingDetected ? "Herding Alert" : "Calm"}
                          variant={result.herding.herdingDetected ? "risk" : "calm"}
                        />
                      </div>
                      <SemicircleGauge
                        value={result.herding.intensity}
                        displayValue={`${Math.round(result.herding.intensity)}`}
                        unit=" / 100"
                        subtitle={
                          result.herding.herdingDetected ? "Elevated Clustered Trading" : "Autonomous Decision-Making"
                        }
                        variant="herd"
                      />
                      <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed mt-2">
                        {result.herding.herdingDetected
                          ? `Cross-sectional return dispersion is compressed (γ₂ = ${result.herding.gamma2.toFixed(
                              4
                            )}), indicating synchronized crowd behavior across peer stocks.`
                          : `Investors are making independent decisions with steady retail volumes and no copycat dispersion compression (γ₂ = ${result.herding.gamma2.toFixed(
                              4
                            )}).`}
                      </p>
                    </div>
                  </div>

                  {/* Gauge 2: Panic Selling */}
                  <div className="w-[84vw] max-w-[320px] md:w-auto flex-shrink-0 snap-center bg-surface-container-lowest dark:bg-surface-container-lowest/80 rounded-2xl shadow-sm border border-surface-container-high/60 p-5 sm:p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-base sm:text-lg font-bold text-on-surface">
                          Panic Selling Index
                        </h3>
                        <StatusChip
                          label={
                            result.panic.panicScore >= 50
                              ? "Extreme Fear"
                              : result.panic.panicScore >= 30
                              ? "Moderate"
                              : "Low Fear"
                          }
                          variant={
                            result.panic.panicScore >= 50
                              ? "risk"
                              : result.panic.panicScore >= 30
                              ? "watch"
                              : "calm"
                          }
                        />
                      </div>
                      <SemicircleGauge
                        value={result.panic.panicScore}
                        displayValue={`${Math.round(result.panic.panicScore)}`}
                        unit=" / 100"
                        subtitle={
                          result.panic.panicScore >= 50
                            ? "Distress Liquidations"
                            : "Orderly Absorbed"
                        }
                        variant="panic"
                      />
                      <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed mt-2">
                        {result.panic.panicScore >= 50
                          ? "Abnormal volume spikes on downward sessions suggest emotional capitulation and stop cascades."
                          : "Pullback volumes show no institutional distress. Bid-ask spreads and order depth remain disciplined with steady absorption."}
                      </p>
                    </div>
                  </div>

                  {/* Gauge 3: Staying Power (SIP Advantage) */}
                  <div className="w-[84vw] max-w-[320px] md:w-auto flex-shrink-0 snap-center bg-surface-container-lowest dark:bg-surface-container-lowest/80 rounded-2xl shadow-sm border border-surface-container-high/60 p-5 sm:p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-base sm:text-lg font-bold text-on-surface">
                          Staying Power
                        </h3>
                        <StatusChip
                          label={
                            (result.monteCarlo.costOfPanic.winRate || 0) >= 70
                              ? "High Edge"
                              : "Balanced"
                          }
                          variant="edge"
                        />
                      </div>
                      <SemicircleGauge
                        value={result.monteCarlo.costOfPanic.winRate || 80}
                        displayValue={`${Math.round(
                          result.monteCarlo.costOfPanic.winRate || 80
                        )}%`}
                        unit=""
                        subtitle="Historical SIP Advantage"
                        variant="staying"
                      />
                      <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed mt-2">
                        In past simulations, a disciplined regular SIP investor outperformed emotional panic-selling exits in{" "}
                        <strong className="text-on-surface tabular-nums">
                          {Math.round(result.monteCarlo.costOfPanic.winRate || 80)}%
                        </strong>{" "}
                        of simulated market cycles.
                      </p>
                    </div>
                  </div>
                </div>
              </section>

              {/* ─────────────────────────────────────────────────────────────
                  SECTION 3: Price & Volume Chart with Jagged Daily Line
                 ───────────────────────────────────────────────────────────── */}
              <section className="bg-surface-container-lowest dark:bg-surface-container-lowest/80 rounded-2xl shadow-sm border border-surface-container-high/60 p-5 sm:p-7 md:p-8">
                <PriceVolumeChart
                  data={result.priceChart}
                  panicVolumeData={result.panic.volumeData}
                  symbol={quote.symbol}
                />

                {/* Behavioral Events Log Cards */}
                <div className="mt-6 pt-5 border-t border-surface-container-high/60">
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs sm:text-sm font-bold text-on-surface">
                        Primary Behavioral Observations
                      </span>
                      <span className="text-outline text-xs">
                        • Filtered by volume anomaly intensity
                      </span>
                    </div>
                    <span className="text-[11px] text-on-surface-variant font-medium">
                      Educational event log
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                    <div className="p-4 rounded-xl bg-surface-container-low border-l-4 border-emerald-500 flex flex-col justify-start">
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <h4 className="text-xs sm:text-sm font-bold text-emerald-800 dark:text-emerald-300">
                          Orderly Accumulation Range
                        </h4>
                        <span className="bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 text-[10px] px-2 py-0.5 rounded font-bold whitespace-nowrap">
                          Absorption
                        </span>
                      </div>
                      <p className="text-xs text-on-surface-variant leading-relaxed">
                        Institutional accumulation absorbed retail profit-taking sessions without sustained volatility expansion or crowd panic.
                      </p>
                    </div>

                    <div className="p-4 rounded-xl bg-surface-container-low border-l-4 border-indigo-500 flex flex-col justify-start">
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <h4 className="text-xs sm:text-sm font-bold text-indigo-700 dark:text-indigo-300">
                          Volume Consolidation Phase
                        </h4>
                        <span className="bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300 text-[10px] px-2 py-0.5 rounded font-bold whitespace-nowrap">
                          Orderly Range
                        </span>
                      </div>
                      <p className="text-xs text-on-surface-variant leading-relaxed">
                        Steady turnover within historical ranges following quarterly delivery reports, showing disciplined long-term positioning.
                      </p>
                    </div>
                  </div>
                </div>
              </section>

              {/* ─────────────────────────────────────────────────────────────
                  SECTION 4: Plain English Behavioral Takeaway Banner
                 ───────────────────────────────────────────────────────────── */}
              <NoticeBanner
                title="Plain English Behavioral Takeaway"
                text={`Historical econometric records show that when ${quote.name} displays low crowd herding and a controlled panic score (${result.panic.panicScore}/100), retail volume flows remain balanced and price pullbacks historically stabilize within normal cyclical parameters. Past data illustrates how crowd participation patterns varied across cycles, presented here strictly for educational study.`}
                emotionLabel="Disciplined Equilibrium"
              />

              {/* ─────────────────────────────────────────────────────────────
                  SECTION 5: Detailed Behavioral Analysis (4 Tabs)
                 ───────────────────────────────────────────────────────────── */}
              <section className="bg-surface-container-lowest dark:bg-surface-container-lowest/80 rounded-2xl shadow-sm border border-surface-container-high/60 p-5 sm:p-7 md:p-8">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-surface-container-high/60 pb-4 mb-6">
                  <div>
                    <h3 className="text-lg sm:text-xl font-bold text-on-surface">
                      In-Depth Behavioral Breakdown
                    </h3>
                    <p className="text-xs text-on-surface-variant mt-0.5">
                      Cognitive patterns observed across retail and institutional flows
                    </p>
                  </div>
                  <span className="text-[11px] text-on-surface-variant font-medium">
                    End-of-day empirical models
                  </span>
                </div>

                {/* Tab Navigation Controls (Minimum 44px Touch Targets) */}
                <div className="flex items-center gap-2 bg-surface-container-low dark:bg-surface-container-low/70 p-1.5 rounded-xl mb-6 overflow-x-auto border border-surface-container-high/40 scrollbar-none">
                  {[
                    { id: "herd", label: "Herd analysis" },
                    { id: "panic", label: "Panic factors" },
                    { id: "missing", label: "Missing best days" },
                    { id: "sip", label: "SIP vs panic" },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      type="button"
                      onClick={() =>
                        setActiveAnalysisTab(
                          tab.id as "herd" | "panic" | "missing" | "sip"
                        )
                      }
                      className={`px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all min-h-[44px] cursor-pointer whitespace-nowrap touch-manipulation ${
                        activeAnalysisTab === tab.id
                          ? "bg-surface-container-lowest dark:bg-surface text-primary dark:text-primary-fixed shadow-xs font-bold"
                          : "text-on-surface-variant hover:text-on-surface"
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* TAB 1: Herd Analysis */}
                {activeAnalysisTab === "herd" && (
                  <div className="space-y-6 animate-in fade-in duration-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5">
                      <div className="bg-surface-container-low p-5 rounded-xl border border-surface-container-high/60 flex flex-col justify-between gap-3">
                        <div>
                          <div className="flex justify-between items-center mb-1">
                            <h4 className="text-sm sm:text-base font-bold text-on-surface">
                              Order Flow Independence
                            </h4>
                            <span className="text-sm font-bold text-secondary tabular-nums">
                              {Math.round(100 - result.herding.intensity)}%
                            </span>
                          </div>
                          <p className="text-xs text-on-surface-variant leading-relaxed">
                            Measures the degree to which trade clustering matches independent decision-making rather than crowd surges. High independence indicates disciplined, non-reactive holding.
                          </p>
                        </div>
                        <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden">
                          <div
                            className="h-full bg-secondary rounded-full"
                            style={{
                              width: `${Math.max(
                                10,
                                Math.round(100 - result.herding.intensity)
                              )}%`,
                            }}
                          />
                        </div>
                      </div>

                      <div className="bg-surface-container-low p-5 rounded-xl border border-surface-container-high/60 flex flex-col justify-between gap-3">
                        <div>
                          <div className="flex justify-between items-center mb-1">
                            <h4 className="text-sm sm:text-base font-bold text-on-surface">
                              Chasing vs Accumulation Score
                            </h4>
                            <span className="text-sm font-bold text-primary tabular-nums">
                              {Math.round(result.behaviorGap.behaviorGap * 10)} / 100
                            </span>
                          </div>
                          <p className="text-xs text-on-surface-variant leading-relaxed">
                            Compares purchases during momentum spikes versus measured accumulation during calm consolidation periods.
                          </p>
                        </div>
                        <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary-container rounded-full"
                            style={{
                              width: `${Math.min(
                                100,
                                Math.max(10, Math.round(result.behaviorGap.behaviorGap * 10))
                              )}%`,
                            }}
                          />
                        </div>
                      </div>
                    </div>

                    <CSADScatterChart
                      data={result.herding.csadData}
                      sector={result.herding.sector}
                      gamma2={result.herding.gamma2}
                      herdingDetected={result.herding.herdingDetected}
                    />
                  </div>
                )}

                {/* TAB 2: Panic Factors */}
                {activeAnalysisTab === "panic" && (
                  <div className="space-y-6 animate-in fade-in duration-200">
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                      {[
                        { label: "Volume Anomaly", val: result.panic.factors.volumeAnomaly },
                        { label: "Range Pressure", val: result.panic.factors.deliveryPressure },
                        { label: "Price-Vol Divergence", val: result.panic.factors.priceVolDivergence },
                        { label: "Drawdown Severity", val: result.panic.factors.drawdownSeverity },
                        { label: "Volatility Regime", val: result.panic.factors.volatilityRegime },
                      ].map((factor) => (
                        <div
                          key={factor.label}
                          className="bg-surface-container-low p-3.5 rounded-xl border border-surface-container-high/60 flex flex-col justify-between"
                        >
                          <span className="text-[11px] text-on-surface-variant font-medium">
                            {factor.label}
                          </span>
                          <span className="text-lg font-bold text-on-surface tabular-nums mt-1">
                            {factor.val?.toFixed(1)}
                          </span>
                          <div className="w-full h-1.5 bg-surface-container-highest rounded-full mt-2 overflow-hidden">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${Math.min(100, factor.val)}%`,
                                backgroundColor:
                                  factor.val > 60
                                    ? "#dc2626"
                                    : factor.val > 35
                                    ? "#d97706"
                                    : "#059669",
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="p-4 rounded-xl bg-surface-container-low border border-surface-container-high flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
                      <div>
                        <span className="font-bold text-on-surface">
                          Volatility &amp; Drawdown Context:
                        </span>{" "}
                        <span className="text-on-surface-variant">
                          Current drawdown is{" "}
                          <strong className="text-on-surface">
                            {result.panic.details.currentDrawdown?.toFixed(1)}%
                          </strong>{" "}
                          from 52W peak. Realized 20-day volatility is{" "}
                          <strong className="text-on-surface">
                            {result.panic.details.currentVolatility?.toFixed(1)}%
                          </strong>{" "}
                          p.a. vs 1-year historical average of{" "}
                          <strong className="text-on-surface">
                            {result.panic.details.avgVolatility?.toFixed(1)}%
                          </strong>
                          .
                        </span>
                      </div>
                      <StatusChip
                        label={
                          result.panic.details.currentVolatility >
                          result.panic.details.avgVolatility * 1.3
                            ? "Elevated Volatility"
                            : "Normal Volatility"
                        }
                        variant={
                          result.panic.details.currentVolatility >
                          result.panic.details.avgVolatility * 1.3
                            ? "watch"
                            : "calm"
                        }
                      />
                    </div>
                  </div>
                )}

                {/* TAB 3: Missing Best Days */}
                {activeAnalysisTab === "missing" && (
                  <div className="space-y-4 animate-in fade-in duration-200">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <p className="text-xs text-on-surface-variant">
                        Starting with an initial ₹1,00,000 investment: impact of missing top performing days due to market timing exits.
                      </p>
                      <span className="text-[11px] font-semibold text-primary">
                        252 Trading Days Baseline
                      </span>
                    </div>

                    <MissingDaysBarChart data={result.missingDays} />
                  </div>
                )}

                {/* TAB 4: SIP vs Panic Exit */}
                {activeAnalysisTab === "sip" && (
                  <div className="space-y-6 animate-in fade-in duration-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5">
                      {/* Scenario A: Disciplined SIP */}
                      <div className="bg-surface-container-low p-5 sm:p-6 rounded-2xl border-2 border-emerald-500/40 flex flex-col justify-between gap-3 shadow-xs">
                        <div>
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="text-xs font-black text-secondary uppercase tracking-wider">
                              Scenario A
                            </span>
                            <StatusChip label="Disciplined" variant="calm" />
                          </div>
                          <h4 className="text-base sm:text-lg font-bold text-on-surface">
                            Stayed Invested Through All Cycles
                          </h4>
                          <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
                            Maintained regular monthly contributions across corrections, dips, and volatile days.
                          </p>
                        </div>
                        <div>
                          <span className="text-[11px] text-on-surface-variant font-medium">
                            Median Simulated Final Value
                          </span>
                          <div className="text-2xl sm:text-3xl font-black text-secondary tabular-nums tracking-tight mt-0.5">
                            {fmt(result.monteCarlo.sip.median)}
                          </div>
                        </div>
                        <div className="text-[11px] text-on-surface-variant pt-2 border-t border-surface-container-high flex justify-between">
                          <span>10th Percentile: {fmt(result.monteCarlo.sip.p10)}</span>
                          <span>90th Percentile: {fmt(result.monteCarlo.sip.p90)}</span>
                        </div>
                      </div>

                      {/* Scenario B: Panic Seller */}
                      <div className="bg-surface-container-low p-5 sm:p-6 rounded-2xl border-2 border-red-400/40 flex flex-col justify-between gap-3 shadow-xs">
                        <div>
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="text-xs font-black text-error uppercase tracking-wider">
                              Scenario B
                            </span>
                            <StatusChip label="Panic Exit" variant="risk" />
                          </div>
                          <h4 className="text-base sm:text-lg font-bold text-on-surface">
                            Exited to Cash on 10% Drawdowns
                          </h4>
                          <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
                            Liquidated to cash upon market drops and sat out for 90 days before re-entering.
                          </p>
                        </div>
                        <div>
                          <span className="text-[11px] text-on-surface-variant font-medium">
                            Median Simulated Final Value
                          </span>
                          <div className="text-2xl sm:text-3xl font-black text-on-surface tabular-nums tracking-tight mt-0.5">
                            {fmt(result.monteCarlo.panic.median)}
                          </div>
                        </div>
                        <div className="text-[11px] text-on-surface-variant pt-2 border-t border-surface-container-high flex justify-between">
                          <span>10th Percentile: {fmt(result.monteCarlo.panic.p10)}</span>
                          <span>90th Percentile: {fmt(result.monteCarlo.panic.p90)}</span>
                        </div>
                      </div>
                    </div>

                    {/* Simulation Wealth Difference Callout Box */}
                    <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 p-4 sm:p-5 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex items-start sm:items-center gap-3.5">
                        <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/60 text-amber-800 dark:text-amber-300 flex items-center justify-center shrink-0 border border-amber-300">
                          <span className="material-symbols-outlined text-[22px]">calculate</span>
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-0.5">
                            <span className="text-[11px] font-extrabold text-amber-900 dark:text-amber-200 uppercase tracking-wide">
                              ESTIMATED COST OF EMOTIONAL EXIT
                            </span>
                            <span className="bg-amber-200 dark:bg-amber-900 text-amber-900 dark:text-amber-200 text-[10px] font-bold px-2 py-0.5 rounded">
                              Simulation
                            </span>
                          </div>
                          <p className="text-base sm:text-lg font-extrabold text-amber-950 dark:text-amber-100 tabular-nums">
                            {fmt(result.monteCarlo.costOfPanic.meanLoss)} Mean Wealth Difference{" "}
                            <span className="font-normal text-xs text-amber-900 dark:text-amber-300">
                              per ₹10,000 monthly SIP ({result.monteCarlo.costOfPanic.pctLoss?.toFixed(1)}% of portfolio)
                            </span>
                          </p>
                        </div>
                      </div>

                      <div className="shrink-0 text-xs text-amber-800 dark:text-amber-300 font-medium sm:text-right">
                        Disciplined SIP wins in{" "}
                        <strong className="text-amber-950 dark:text-amber-100 tabular-nums">
                          {Math.round(result.monteCarlo.costOfPanic.winRate || 80)}%
                        </strong>{" "}
                        of simulated paths.
                      </div>
                    </div>

                    <MonteCarloHistogram data={result.monteCarlo.histogram} />
                  </div>
                )}
              </section>

              {/* ─────────────────────────────────────────────────────────────
                  SECTION 6: Our Behavioral Verdict Box (When Verified Healthy)
                 ───────────────────────────────────────────────────────────── */}
              {isHealthy && (
                <section className="bg-surface-container-lowest dark:bg-surface-container-lowest/80 rounded-2xl shadow-sm border border-surface-container-high/60 p-5 sm:p-7 md:p-8">
                  <div className="flex items-start justify-between gap-4 mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 flex items-center justify-center">
                        <span className="material-symbols-outlined text-[22px]">verified</span>
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-on-surface">
                          Our Behavioral Verdict
                        </h3>
                        <span className="text-xs text-emerald-700 dark:text-emerald-400 font-semibold">
                          Healthy Market Conditions
                        </span>
                      </div>
                    </div>
                    <StatusChip label="Low Risk" variant="calm" />
                  </div>

                  <p className="text-xs sm:text-sm text-on-surface leading-relaxed mb-5">
                    <strong>{quote.name}</strong> shows rational investor behavior with low crowd herding (intensity {result.herding.intensity?.toFixed(0)}), controlled panic levels ({result.panic.panicScore}/100), and a manageable behavior gap of {result.behaviorGap.behaviorGap?.toFixed(1)}% per year. Market pricing appears orderly without acute emotional distortions.
                  </p>

                  <div className="space-y-2 pt-2 border-t border-surface-container-high/60">
                    <span className="text-[11px] font-bold text-outline uppercase tracking-wider block">
                      Recommended Behavioral Actions:
                    </span>
                    <ul className="text-xs space-y-1.5 text-on-surface-variant list-decimal list-inside">
                      <li>Consider a systematic SIP strategy for disciplined long-term accumulation.</li>
                      <li>
                        Staying invested vs. panic selling could protect ~
                        {result.monteCarlo.costOfPanic.pctLoss?.toFixed(0)}% of cumulative portfolio returns.
                      </li>
                      <li>Monitor sector dispersion quarterly; industry news can shift herd dynamics.</li>
                    </ul>
                  </div>
                </section>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Floating Action Button (FAB) for AI Copilot */}
      <aside className="fixed bottom-20 sm:bottom-6 right-4 sm:right-6 z-40">
        <button
          type="button"
          onClick={() => setIsCopilotOpen(true)}
          className="flex items-center gap-2 bg-primary-container hover:bg-indigo-700 text-on-primary font-bold text-xs sm:text-sm px-4 sm:px-5 py-3 rounded-full shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5 cursor-pointer touch-manipulation whitespace-nowrap"
        >
          <span className="material-symbols-outlined text-[20px]">psychology</span>
          <span>Ask Behavioral Copilot</span>
        </button>
      </aside>

      {/* Slide-over Drawer / Bottom Sheet */}
      <AICopilotDrawer
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
        result={result}
      />

      {/* Stock Selector Modal */}
      <StockSelectorModal
        isOpen={isStockModalOpen}
        onClose={() => setIsStockModalOpen(false)}
        selected={selectedStock}
        onSelect={analyzeStock}
      />

      {/* Sticky Bottom Tab Bar for Mobile (< 1024px) */}
      <MobileTabBar
        activeTab={mobileTab}
        onChangeTab={(t) => {
          setMobileTab(t);
          if (t === "copilot") setIsCopilotOpen(true);
        }}
        onOpenCopilot={() => setIsCopilotOpen(true)}
      />

      {/* Compliance Footer */}
      <Footer />
    </div>
  );
}
