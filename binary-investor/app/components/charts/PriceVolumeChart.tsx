"use client";

import React, { useState } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from "recharts";
import type { PricePoint, VolumePoint } from "@/app/lib/types";

interface Props {
  data: PricePoint[];
  panicVolumeData?: VolumePoint[];
  symbol: string;
}

export default function PriceVolumeChart({
  data,
  panicVolumeData = [],
  symbol,
}: Props) {
  const [mode, setMode] = useState<"area" | "candle">("area");
  const [showHerdEvents, setShowHerdEvents] = useState(true);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-on-surface-variant text-sm">
        No price history available.
      </div>
    );
  }

  // Create panic lookup set by date
  const panicDates = new Set(
    panicVolumeData.filter((v) => v.isPanic).map((v) => v.date)
  );

  const prices = data.map((d) => d.close);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceMargin = (maxPrice - minPrice) * 0.1 || minPrice * 0.05;
  const yDomain = [
    Math.floor((minPrice - priceMargin) / 100) * 100,
    Math.ceil((maxPrice + priceMargin) / 100) * 100,
  ];

  const maxVol = Math.max(...data.map((d) => d.volume), 1);

  // Formatter for tooltip currency
  const fmtCurrency = (n: number) =>
    `₹${n.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;

  const fmtVol = (v: number) => {
    if (v >= 1e7) return `${(v / 1e7).toFixed(2)} Cr`;
    if (v >= 1e5) return `${(v / 1e5).toFixed(1)} L`;
    if (v >= 1e3) return `${(v / 1e3).toFixed(0)} k`;
    return `${v}`;
  };

  return (
    <div className="w-full flex flex-col gap-4">
      {/* Chart Top Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base sm:text-lg font-bold text-on-surface">
              Price &amp; Crowd Dispersion Flow
            </h3>
            <span
              className="material-symbols-outlined text-[18px] text-primary"
              title="Annotated behavioral crowd events"
            >
              candlestick_chart
            </span>
          </div>
          <p className="text-xs text-on-surface-variant mt-0.5">
            NSE: {symbol.replace(".NS", "")} • Historical price trajectory alongside crowd participation anomalies
          </p>
        </div>

        {/* View Mode & Herd Event Controls */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Mode Switcher */}
          <div className="flex items-center bg-surface-container dark:bg-surface-container-low p-0.5 rounded-lg border border-surface-container-high">
            <button
              type="button"
              onClick={() => setMode("area")}
              className={`p-1.5 rounded-md transition-colors ${
                mode === "area"
                  ? "bg-surface-container-lowest text-primary shadow-xs font-semibold"
                  : "text-on-surface-variant hover:text-on-surface"
              }`}
              title="Area Line Chart"
            >
              <span className="material-symbols-outlined text-[16px]">show_chart</span>
            </button>
            <button
              type="button"
              onClick={() => setMode("candle")}
              className={`p-1.5 rounded-md transition-colors ${
                mode === "candle"
                  ? "bg-surface-container-lowest text-primary shadow-xs font-semibold"
                  : "text-on-surface-variant hover:text-on-surface"
              }`}
              title="High-Low Wick View"
            >
              <span className="material-symbols-outlined text-[16px]">bar_chart</span>
            </button>
          </div>

          {/* Herd Events Checkbox Toggle */}
          <label className="flex items-center gap-1.5 bg-surface-container-low hover:bg-surface-container dark:bg-surface-container-low/70 px-2.5 py-1.5 rounded-lg cursor-pointer border border-surface-container-high text-xs font-medium text-on-surface touch-manipulation select-none">
            <input
              type="checkbox"
              checked={showHerdEvents}
              onChange={(e) => setShowHerdEvents(e.target.checked)}
              className="w-3.5 h-3.5 rounded text-primary focus:ring-primary accent-primary cursor-pointer"
            />
            <span className="whitespace-nowrap">Show Herd Events</span>
          </label>
        </div>
      </div>

      {/* Main Chart Graphic Canvas */}
      <div className="w-full bg-[#f8f9ff] dark:bg-surface-container-low/40 rounded-xl p-3 sm:p-4 border border-surface-container-high/70 relative overflow-hidden">
        <div className="flex items-center justify-between text-[11px] text-outline font-semibold mb-2">
          <span>DAILY CLOSE &amp; TRADING VOLUME</span>
          <span className="text-secondary font-medium">
            Max Volume: {fmtVol(maxVol)} Shares
          </span>
        </div>

        <div className="w-full h-[280px] sm:h-[340px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={data}
              margin={{ top: 10, right: 10, bottom: 0, left: 10 }}
            >
              <defs>
                <linearGradient id="priceAreaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#4f46e5" stopOpacity={0.28} />
                  <stop offset="70%" stopColor="#4f46e5" stopOpacity={0.05} />
                  <stop offset="100%" stopColor="#4f46e5" stopOpacity={0} />
                </linearGradient>
              </defs>

              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--surface-container-high)"
                vertical={false}
              />

              <XAxis
                dataKey="date"
                stroke="transparent"
                tick={{ fontSize: 10, fill: "var(--outline)" }}
                interval={Math.floor(data.length / 5)}
              />

              {/* Price Axis (non-zero domain) */}
              <YAxis
                yAxisId="price"
                domain={yDomain}
                orientation="right"
                stroke="transparent"
                tick={{ fontSize: 10, fill: "var(--outline)", fontFamily: "Inter" }}
                tickFormatter={(v) => `₹${Number(v).toLocaleString("en-IN")}`}
              />

              {/* Volume Axis (scaled for bottom 25% height) */}
              <YAxis
                yAxisId="volume"
                domain={[0, maxVol * 4]}
                orientation="left"
                stroke="transparent"
                hide
              />

              <Tooltip
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const pt = payload[0]?.payload as PricePoint;
                  const isPanicEvent = showHerdEvents && panicDates.has(pt?.date);

                  return (
                    <div className="bg-surface-container-lowest dark:bg-surface-container-lowest p-3 rounded-xl shadow-lg border border-surface-container-high text-xs space-y-1.5 min-w-[160px]">
                      <div className="flex items-center justify-between border-b border-surface-container-high pb-1">
                        <span className="font-semibold text-on-surface">{pt?.date}</span>
                        {isPanicEvent && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 border border-red-200">
                            Crowd Anomaly
                          </span>
                        )}
                      </div>
                      <div className="flex justify-between gap-4">
                        <span className="text-on-surface-variant">Close:</span>
                        <span className="font-bold text-on-surface tabular-nums">
                          {fmtCurrency(pt?.close)}
                        </span>
                      </div>
                      <div className="flex justify-between gap-4 text-[11px] text-on-surface-variant">
                        <span>Range:</span>
                        <span className="tabular-nums">
                          {fmtCurrency(pt?.low)} – {fmtCurrency(pt?.high)}
                        </span>
                      </div>
                      <div className="flex justify-between gap-4 text-[11px] text-on-surface-variant">
                        <span>Volume:</span>
                        <span className="tabular-nums">{fmtVol(pt?.volume)}</span>
                      </div>
                    </div>
                  );
                }}
              />

              {/* Volume Bars */}
              <Bar yAxisId="volume" dataKey="volume" radius={[2, 2, 0, 0]} maxBarSize={6}>
                {data.map((entry, idx) => {
                  const isPanic = showHerdEvents && panicDates.has(entry.date);
                  return (
                    <Cell
                      key={idx}
                      fill={isPanic ? "#dc2626" : "var(--surface-container-highest)"}
                      fillOpacity={isPanic ? 0.85 : 0.65}
                    />
                  );
                })}
              </Bar>

              {/* Price Line / Area */}
              <Area
                yAxisId="price"
                type="monotone"
                dataKey="close"
                stroke="var(--primary-container)"
                strokeWidth={2.5}
                fill="url(#priceAreaGradient)"
                dot={false}
                activeDot={{ r: 5, fill: "var(--primary)", stroke: "#ffffff", strokeWidth: 2 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
