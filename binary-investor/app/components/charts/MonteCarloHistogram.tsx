"use client";

import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import type { HistogramBin } from "@/app/lib/types";

interface Props {
  data: HistogramBin[];
}

export default function MonteCarloHistogram({ data }: Props) {
  if (!data || data.length === 0) {
    return (
      <div className="h-56 flex items-center justify-center text-on-surface-variant text-xs">
        Monte Carlo simulation data unavailable.
      </div>
    );
  }

  const fmtCurrency = (v: number) => {
    if (v >= 1e7) return `₹${(v / 1e7).toFixed(1)}Cr`;
    if (v >= 1e5) return `₹${(v / 1e5).toFixed(1)}L`;
    if (v >= 1e3) return `₹${(v / 1e3).toFixed(0)}k`;
    return `₹${v}`;
  };

  return (
    <div className="w-full h-[280px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          barGap={1}
          margin={{ top: 8, right: 12, bottom: 0, left: 4 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--surface-container-high)"
            vertical={false}
          />
          <XAxis
            dataKey="binStart"
            stroke="transparent"
            tick={{ fontSize: 9, fill: "var(--outline)", fontFamily: "Inter" }}
            tickFormatter={fmtCurrency}
            interval={Math.floor(data.length / 5)}
          />
          <YAxis
            stroke="transparent"
            tick={{ fontSize: 9, fill: "var(--outline)" }}
            label={{
              value: "Simulations",
              angle: -90,
              position: "insideLeft",
              fontSize: 9,
              fill: "var(--outline)",
            }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const d = payload[0]?.payload as HistogramBin;
              return (
                <div className="bg-surface-container-lowest p-3 rounded-xl shadow-lg border border-surface-container-high text-xs space-y-1.5 min-w-[170px]">
                  <p className="font-bold text-on-surface border-b border-surface-container-high pb-1">
                    Range: {fmtCurrency(d.binStart)} – {fmtCurrency(d.binEnd)}
                  </p>
                  <div className="flex justify-between gap-4 text-secondary font-semibold">
                    <span>Disciplined SIP:</span>
                    <span className="tabular-nums">{d.sip} runs</span>
                  </div>
                  <div className="flex justify-between gap-4 text-error font-semibold">
                    <span>Panic Seller:</span>
                    <span className="tabular-nums">{d.panic} runs</span>
                  </div>
                </div>
              );
            }}
          />
          <Legend
            wrapperStyle={{
              fontSize: 11,
              paddingTop: 8,
              fontFamily: "Inter",
            }}
            iconType="circle"
            iconSize={8}
          />
          <Bar
            dataKey="sip"
            name="Disciplined SIP"
            fill="#006c4a"
            fillOpacity={0.7}
            radius={[2, 2, 0, 0]}
          />
          <Bar
            dataKey="panic"
            name="Panic Seller"
            fill="#dc2626"
            fillOpacity={0.7}
            radius={[2, 2, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
