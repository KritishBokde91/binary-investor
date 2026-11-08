"use client";

import React, { useState } from "react";
import Link from "next/link";
import type { StockInfo } from "@/app/lib/types";

interface Props {
  selectedStock: StockInfo | null;
  onOpenStockSelector: () => void;
  onOpenCopilot: () => void;
  asOfDate?: string | null;
}

export default function Header({
  selectedStock,
  onOpenStockSelector,
  onOpenCopilot,
  asOfDate,
}: Props) {
  const [isDark, setIsDark] = useState(() =>
    typeof document !== "undefined"
      ? document.documentElement.classList.contains("dark")
      : false
  );

  const toggleTheme = () => {
    const nextDark = !isDark;
    setIsDark(nextDark);
    if (typeof document !== "undefined") {
      if (nextDark) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    }
  };

  const formattedDate = asOfDate
    ? new Date(asOfDate).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      }) + ", 3:30 PM IST"
    : "8 Nov 2026, 3:30 PM IST";

  return (
    <header className="fixed top-0 left-0 right-0 z-40 bg-surface-container-lowest/95 dark:bg-surface/95 backdrop-blur-md shadow-xs border-b border-surface-container-high/60 transition-colors">
      <div className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Logo & Search Selector */}
        <div className="flex items-center gap-4 sm:gap-6 shrink-0">
          <Link
            href="/"
            className="flex items-center gap-2.5 text-on-surface hover:opacity-90 transition-opacity whitespace-nowrap"
          >
            <div className="w-8 h-8 rounded-lg bg-primary-container text-on-primary flex items-center justify-center shadow-xs shrink-0">
              <span className="material-symbols-outlined text-[20px]">psychology</span>
            </div>
            <div className="flex flex-col">
              <span className="font-headline text-lg sm:text-xl font-bold tracking-tight text-on-surface leading-tight">
                SheepOrSleep
              </span>
              <span className="text-[10px] text-on-surface-variant hidden sm:inline leading-none font-medium">
                Calm Behavioral Fintech
              </span>
            </div>
          </Link>

          {/* Stock Search Pill Trigger */}
          <button
            type="button"
            onClick={onOpenStockSelector}
            className="flex items-center gap-2 bg-surface-container hover:bg-surface-container-high dark:bg-surface-container-low dark:hover:bg-surface-container px-3 py-1.5 rounded-lg transition-colors cursor-pointer border border-transparent hover:border-outline-variant text-left touch-manipulation min-h-[38px]"
          >
            <span className="material-symbols-outlined text-on-surface-variant text-[18px]">
              search
            </span>
            <div className="flex items-center gap-1.5 text-xs sm:text-sm whitespace-nowrap">
              <span className="font-bold text-on-surface">
                {selectedStock ? selectedStock.symbol.replace(".NS", "") : "Search"}
              </span>
              <span className="text-outline hidden sm:inline">|</span>
              <span className="text-on-surface-variant hidden sm:inline max-w-[120px] md:max-w-[180px] truncate">
                {selectedStock ? selectedStock.name : "Select Indian Stock"}
              </span>
              {selectedStock?.sector && (
                <span className="bg-surface-container-highest text-on-surface-variant text-[10px] font-semibold px-1.5 py-0.5 rounded">
                  {selectedStock.sector}
                </span>
              )}
            </div>
            <span className="material-symbols-outlined text-outline text-[16px] ml-1">
              unfold_more
            </span>
          </button>
        </div>

        {/* Center: Desktop Nav Links */}
        <nav className="hidden lg:flex items-center gap-1.5 shrink-0">
          <Link
            href="/"
            className="px-3.5 py-2 text-xs sm:text-sm font-semibold rounded-lg bg-primary-container text-on-primary shadow-xs transition-colors whitespace-nowrap"
          >
            Dashboard
          </Link>
          <button
            type="button"
            onClick={onOpenCopilot}
            className="px-3.5 py-2 text-xs sm:text-sm font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors rounded-lg whitespace-nowrap cursor-pointer"
          >
            AI Copilot
          </button>
          <a
            href="#methodology"
            className="px-3.5 py-2 text-xs sm:text-sm font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors rounded-lg whitespace-nowrap"
          >
            How it works
          </a>
        </nav>

        {/* Right: Theme Toggle & Actions */}
        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          {/* Light / Dark Mode Toggle Pill */}
          <div className="flex items-center bg-surface-container p-0.5 rounded-full border border-surface-container-high">
            <button
              type="button"
              onClick={toggleTheme}
              aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
              className={`w-7 h-7 rounded-full flex items-center justify-center transition-all ${
                !isDark
                  ? "bg-surface-container-lowest text-on-surface shadow-xs"
                  : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              <span className="material-symbols-outlined text-[15px]">
                {isDark ? "dark_mode" : "light_mode"}
              </span>
            </button>
          </div>

          {/* Stock selector button on mobile */}
          <button
            type="button"
            onClick={onOpenStockSelector}
            className="sm:hidden w-8 h-8 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container transition-colors"
            title="Search stocks"
          >
            <span className="material-symbols-outlined text-[20px]">manage_search</span>
          </button>

          {/* Live System Indicator */}
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-container text-xs font-semibold text-secondary">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
            <span className="text-[11px]">Calm Mode</span>
          </div>
        </div>
      </div>

      {/* Sub-header Market Status Strip */}
      <div className="bg-surface-container-low dark:bg-surface-container-low/70 border-t border-surface-container/60 h-8 sm:h-9 flex items-center text-[11px] sm:text-xs text-on-surface-variant">
        <div className="max-w-[1280px] w-full mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between whitespace-nowrap">
          <div className="flex items-center gap-2 overflow-hidden">
            <span className="font-medium text-on-surface-variant">End-of-day data, delayed</span>
            <span className="text-outline">•</span>
            <span className="truncate">As of {formattedDate}</span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="bg-surface-container-highest text-on-surface-variant px-2 py-0.5 rounded text-[10px] font-bold">
              NSE / BSE
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
