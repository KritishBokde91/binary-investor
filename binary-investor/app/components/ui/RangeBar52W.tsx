"use client";

import React from "react";

interface Props {
  currentPrice: number;
  low52W: number;
  high52W: number;
}

export default function RangeBar52W({ currentPrice, low52W, high52W }: Props) {
  const safeLow = low52W > 0 ? low52W : currentPrice * 0.7;
  const safeHigh = high52W > 0 ? high52W : currentPrice * 1.3;
  const spread = Math.max(0.01, safeHigh - safeLow);
  const rawPct = ((currentPrice - safeLow) / spread) * 100;
  const pct = Math.max(3, Math.min(97, rawPct));

  const median = (safeLow + safeHigh) / 2;
  const diffFromHigh = ((currentPrice - safeHigh) / safeHigh) * 100;

  let badgeText = "Mid Cycle";
  if (diffFromHigh >= -3) {
    badgeText = `Near 52W High (${diffFromHigh >= 0 ? "+" : ""}${diffFromHigh.toFixed(1)}% peak)`;
  } else if (rawPct <= 15) {
    badgeText = "Near 52W Low";
  } else if (rawPct >= 70) {
    badgeText = "Upper Quartile";
  } else {
    badgeText = "Mid Cycle Range";
  }

  const fmtCurrency = (n: number) =>
    `₹${n.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;

  return (
    <div className="bg-surface-container-low/70 dark:bg-surface-container-low/40 rounded-xl p-4 sm:p-5 border border-surface-container-high/60 my-5">
      <div className="flex items-center justify-between mb-3 text-xs sm:text-sm">
        <span className="font-semibold text-on-surface">52-Week Range &amp; Historical Cycle</span>
        <span className="inline-flex items-center text-xs font-semibold text-primary bg-indigo-50 border border-indigo-200 dark:bg-indigo-950/60 dark:border-indigo-800 dark:text-indigo-300 px-2.5 py-0.5 rounded-full whitespace-nowrap shadow-xs">
          {badgeText}
        </span>
      </div>

      {/* Progress Bar & Slider Pin */}
      <div className="relative w-full h-2.5 sm:h-3 bg-surface-container-highest rounded-full my-4">
        {/* Fill track */}
        <div
          className="absolute left-0 top-0 h-full bg-gradient-to-r from-indigo-300 via-indigo-500 to-indigo-700 rounded-full"
          style={{ width: `${pct}%` }}
        />
        {/* Median notch */}
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-1 h-3.5 bg-outline rounded-full opacity-60"
          style={{ left: "50%" }}
          title="Cycle Median"
        />
        {/* Active slider pin */}
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 flex flex-col items-center"
          style={{ left: `${pct}%` }}
        >
          <div className="w-4 h-4 rounded-full bg-indigo-600 ring-4 ring-indigo-200 dark:ring-indigo-900 shadow-md flex items-center justify-center">
            <div className="w-1.5 h-1.5 rounded-full bg-surface-container-lowest" />
          </div>
        </div>
      </div>

      {/* 52W Milestones */}
      <div className="grid grid-cols-3 text-xs sm:text-sm pt-1 text-on-surface-variant font-label-sm">
        <div className="text-left flex flex-col">
          <span className="text-[10px] text-on-surface-variant/80 uppercase tracking-wide">52W Low</span>
          <span className="font-bold text-on-surface tabular-nums">{fmtCurrency(safeLow)}</span>
        </div>
        <div className="text-center flex flex-col">
          <span className="text-[10px] text-on-surface-variant/80 uppercase tracking-wide">Cycle Median</span>
          <span className="font-medium text-on-surface-variant tabular-nums">{fmtCurrency(median)}</span>
        </div>
        <div className="text-right flex flex-col">
          <span className="text-[10px] text-on-surface-variant/80 uppercase tracking-wide">52W High</span>
          <span className="font-bold text-on-surface tabular-nums">{fmtCurrency(safeHigh)}</span>
        </div>
      </div>
    </div>
  );
}
