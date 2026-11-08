"use client";

import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from "recharts";
import type { MissingDayScenario } from "@/app/lib/types";

interface Props {
  data: MissingDayScenario[];
}

export default function MissingDaysBarChart({ data }: Props) {
  if (!data || data.length === 0) {
    return (
      <div className="h-56 flex items-center justify-center text-on-surface-variant text-xs">
        Missing days analysis unavailable.
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
          layout="vertical"
          margin={{ top: 4, right: 16, bottom: 0, left: 8 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--surface-container-high)"
            horizontal={false}
          />
          <XAxis
            type="number"
            stroke="transparent"
            tick={{ fontSize: 10, fill: "var(--outline)", fontFamily: "Inter" }}
            tickFormatter={fmtCurrency}
          />
          <YAxis
            type="category"
            dataKey="scenario"
            stroke="transparent"
            tick={{ fontSize: 10, fill: "var(--on-surface-variant)", fontFamily: "Inter" }}
            width={130}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const d = payload[0]?.payload as MissingDayScenario;
              return (
                <div className="bg-surface-container-lowest p-3 rounded-xl shadow-lg border border-surface-container-high text-xs space-y-1.5 min-w-[170px]">
                  <p className="font-bold text-on-surface border-b border-surface-container-high pb-1">
                    {d.scenario}
                  </p>
                  <div className="flex justify-between gap-4">
                    <span className="text-on-surface-variant">Final Value:</span>
                    <span className="font-bold tabular-nums text-on-surface">
                      ₹{Math.round(d.finalValue).toLocaleString("en-IN")}
                    </span>
                  </div>
                  <div className="flex justify-between gap-4">
                    <span className="text-on-surface-variant">CAGR:</span>
                    <span className="font-semibold tabular-nums text-primary">
                      {d.cagr?.toFixed(2)}% p.a.
                    </span>
                  </div>
                  {d.reduction > 0 && (
                    <div className="flex justify-between gap-4 text-error">
                      <span>Wealth Reduction:</span>
                      <span className="font-bold tabular-nums">-{d.reduction?.toFixed(1)}%</span>
                    </div>
                  )}
                </div>
              );
            }}
          />
          <Bar dataKey="finalValue" radius={[0, 6, 6, 0]} barSize={20}>
            {data.map((_, i) => (
              <Cell
                key={i}
                fill={i === 0 ? "#006c4a" : "#dc2626"}
                fillOpacity={i === 0 ? 0.85 : Math.max(0.3, 0.75 - i * 0.08)}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
