"use client";

import React from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Scatter,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import type { CSADPoint } from "@/app/lib/types";

interface Props {
  data: CSADPoint[];
  sector: string;
  gamma2: number;
  herdingDetected: boolean;
}

export default function CSADScatterChart({
  data,
  sector,
  gamma2,
  herdingDetected,
}: Props) {
  if (!data || data.length === 0) {
    return (
      <div className="h-56 flex items-center justify-center text-on-surface-variant text-xs">
        Insufficient cross-sectional peer data to compute CSAD dispersion.
      </div>
    );
  }

  // Sort by absReturn for continuous smooth fitted line rendering
  const sorted = [...data].sort((a, b) => a.absReturn - b.absReturn);

  return (
    <div className="w-full flex flex-col gap-3">
      <div className="flex items-center justify-between text-xs text-on-surface-variant font-medium">
        <span>CSAD vs |Market Return| (Concave curve = herding present)</span>
        <span
          className={`font-semibold ${
            herdingDetected ? "text-error" : "text-secondary"
          }`}
        >
          {herdingDetected ? "Concave: Crowd Herding" : "Convex: Independent Decisions"}
        </span>
      </div>

      <div className="w-full h-[260px] bg-surface-container-low/40 rounded-xl p-2 border border-surface-container-high/60">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={sorted} margin={{ top: 10, right: 10, bottom: 20, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--surface-container-high)" />
            <XAxis
              dataKey="absReturn"
              type="number"
              domain={["dataMin", "dataMax"]}
              stroke="transparent"
              tick={{ fontSize: 9, fill: "var(--outline)" }}
              tickFormatter={(v) => `${(v * 100).toFixed(1)}%`}
              label={{
                value: "|Market Return| (|Rm|)",
                position: "insideBottom",
                offset: -10,
                fontSize: 10,
                fill: "var(--outline)",
              }}
            />
            <YAxis
              dataKey="csad"
              type="number"
              domain={["dataMin", "dataMax"]}
              stroke="transparent"
              tick={{ fontSize: 9, fill: "var(--outline)" }}
              tickFormatter={(v) => `${(v * 100).toFixed(2)}%`}
              label={{
                value: "CSAD Return Dispersion",
                angle: -90,
                position: "insideLeft",
                offset: 10,
                fontSize: 10,
                fill: "var(--outline)",
              }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const d = payload[0]?.payload as CSADPoint;
                return (
                  <div className="bg-surface-container-lowest p-2.5 rounded-lg shadow-md border border-surface-container-high text-xs space-y-1">
                    <p className="font-semibold text-on-surface">Daily Cross-Section</p>
                    <p className="text-[11px] text-on-surface-variant">
                      |Rm|: <span className="font-bold tabular-nums">{(d.absReturn * 100).toFixed(2)}%</span>
                    </p>
                    <p className="text-[11px] text-on-surface-variant">
                      Observed CSAD: <span className="font-bold tabular-nums">{(d.csad * 100).toFixed(3)}%</span>
                    </p>
                    <p className="text-[11px] text-primary">
                      Fitted Curve: <span className="font-bold tabular-nums">{(d.fitted * 100).toFixed(3)}%</span>
                    </p>
                  </div>
                );
              }}
            />
            {/* Observed Cross-Sectional Dispersion Points */}
            <Scatter
              name="Daily CSAD"
              dataKey="csad"
              fill="#6366f1"
              fillOpacity={0.45}
            />
            {/* Quadratic Fitted Regression Line */}
            <Line
              type="monotone"
              dataKey="fitted"
              stroke="#dc2626"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={false}
              activeDot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="flex items-center justify-between text-[11px] text-on-surface-variant pt-1 px-1">
        <span>Sector: <strong>{sector}</strong></span>
        <span>γ₂ Coefficient: <strong className="tabular-nums">{gamma2.toFixed(4)}</strong></span>
      </div>
    </div>
  );
}
