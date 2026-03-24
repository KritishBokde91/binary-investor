"use client";

import {
  ComposedChart, Bar, Line, Area, AreaChart,
  BarChart, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, Legend, ReferenceLine,
  ScatterChart, Scatter,
} from "recharts";
import type {
  PricePoint, CSADPoint, VolumePoint,
  HistogramBin, MissingDayScenario,
} from "@/app/lib/types";

const ACCENT = "#3730A3";
const ACCENT2 = "#6366F1";
const UP = "#059669";
const DOWN = "#DC2626";
const MUTED = "#8C7B65";
const GRID = "rgba(30,20,10,0.05)";
const AMBER = "#D97706";

/* ─── Shared Tooltip ──────────────────────────────── */
function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="custom-tooltip" style={{ fontFamily: "var(--font-body)" }}>
      <p style={{ fontSize: 11, fontWeight: 600, color: "var(--text)", marginBottom: 6, fontFamily: "var(--font-mono)" }}>
        {label}
      </p>
      {payload.map((p: any, i: number) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
          <span style={{
            display: "inline-block", width: 8, height: 8, borderRadius: 2,
            background: p.color || p.fill || p.stroke
          }} />
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{p.name}:</span>
          <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text)", fontFamily: "var(--font-mono)" }}>
            {typeof p.value === "number"
              ? p.name?.toLowerCase().includes("₹") || p.name?.toLowerCase().includes("value") || p.name?.toLowerCase().includes("price") || p.name?.toLowerCase().includes("close") || p.name?.toLowerCase().includes("open") || p.name?.toLowerCase().includes("high") || p.name?.toLowerCase().includes("low")
                ? `₹${p.value.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`
                : p.value.toLocaleString("en-IN", { maximumFractionDigits: 4 })
              : p.value}
          </span>
        </div>
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════ */
/* Dynamic Candlestick Chart                           */
/* ═══════════════════════════════════════════════════ */

// Custom candlestick shape rendered via SVG
function CandlestickShape(props: any) {
  const { x, y, width, height, payload } = props;
  if (!payload) return null;

  const { open, close, high, low } = payload;
  const isUp = close >= open;
  const color = isUp ? UP : DOWN;

  // We need to know the chart's Y scale to draw correctly
  // This shape receives plotted coordinates, so we use them directly
  // The bar represents the body; we need to draw wicks separately
  // Since recharts gives us y/height for the bar range we specify,
  // we handle this with custom computed values passed as payload

  if (!payload._yScale) return null;
  const yScale = payload._yScale;

  const bodyTop = yScale(Math.max(open, close));
  const bodyBottom = yScale(Math.min(open, close));
  const bodyH = Math.max(bodyBottom - bodyTop, 1);
  const wickX = x + width / 2;
  const wickTop = yScale(high);
  const wickBottom = yScale(low);

  return (
    <g>
      {/* Wick */}
      <line x1={wickX} y1={wickTop} x2={wickX} y2={wickBottom}
        stroke={color} strokeWidth={1.5} strokeOpacity={0.7} />
      {/* Body */}
      <rect
        x={x + 1} y={bodyTop} width={Math.max(width - 2, 2)} height={bodyH}
        fill={color} fillOpacity={isUp ? 0.85 : 0.9}
        rx={2} ry={2}
      />
    </g>
  );
}

export function CandlestickChart({ data }: { data: PricePoint[] }) {
  if (!data || data.length === 0) return (
    <div style={{ height: 360, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <span style={{ color: "var(--text-muted)", fontSize: 13 }}>No price data available</span>
    </div>
  );

  // Compute domain
  const allLows = data.map(d => d.low);
  const allHighs = data.map(d => d.high);
  const minPrice = Math.min(...allLows) * 0.998;
  const maxPrice = Math.max(...allHighs) * 1.002;

  // Build candle data with a placeholder "range" field for the bar
  const candleData = data.map(d => ({
    ...d,
    // barBase: the lower of open/close (for stacked approach)
    bodyBase: Math.min(d.open, d.close),
    bodySize: Math.max(Math.abs(d.close - d.open), 0.01),
    isUp: d.close >= d.open,
  }));

  // We use a composed chart with a custom tick
  return (
    <ResponsiveContainer width="100%" height={360}>
      <ComposedChart data={candleData} margin={{ top: 8, right: 12, bottom: 4, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID} vertical={false} />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 10, fill: MUTED, fontFamily: "var(--font-mono)" }}
          stroke="transparent"
          tickFormatter={(v) => {
            const parts = v.split(" ");
            return parts[0] || v;
          }}
          interval={Math.floor(candleData.length / 8)}
        />
        <YAxis
          domain={[minPrice, maxPrice]}
          tick={{ fontSize: 10, fill: MUTED, fontFamily: "var(--font-mono)" }}
          stroke="transparent"
          tickFormatter={(v) => `₹${Number(v).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`}
          width={72}
        />
        <Tooltip
          content={({ active, payload, label }) => {
            if (!active || !payload?.length) return null;
            const d = payload[0]?.payload;
            if (!d) return null;
            const isUp = d.close >= d.open;
            return (
              <div className="custom-tooltip">
                <p style={{ fontSize: 11, fontWeight: 700, color: "var(--text)", marginBottom: 6, fontFamily: "var(--font-mono)" }}>{label}</p>
                {[
                  ["Open", d.open],
                  ["High", d.high],
                  ["Low", d.low],
                  ["Close", d.close],
                ].map(([k, v]) => (
                  <div key={k as string} style={{ display: "flex", justifyContent: "space-between", gap: 16, marginBottom: 2 }}>
                    <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{k}</span>
                    <span style={{ fontSize: 11, fontWeight: 600, color: k === "Close" ? (isUp ? UP : DOWN) : "var(--text)", fontFamily: "var(--font-mono)" }}>
                      ₹{Number(v).toLocaleString("en-IN", { maximumFractionDigits: 2 })}
                    </span>
                  </div>
                ))}
                <div style={{ display: "flex", justifyContent: "space-between", gap: 16, marginTop: 4, paddingTop: 4, borderTop: "1px solid var(--glass-border)" }}>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Volume</span>
                  <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text)", fontFamily: "var(--font-mono)" }}>
                    {Number(d.volume).toLocaleString("en-IN")}
                  </span>
                </div>
              </div>
            );
          }}
        />

        {/* Invisible bar for the body base (to anchor the stack) */}
        <Bar dataKey="bodyBase" stackId="candle" fill="transparent" stroke="transparent" barSize={8} legendType="none" />

        {/* Colored body bar */}
        <Bar dataKey="bodySize" stackId="candle" barSize={8} name="Price Body" legendType="none" radius={[1, 1, 1, 1]}>
          {candleData.map((d, i) => (
            <Cell key={i} fill={d.isUp ? UP : DOWN} fillOpacity={0.88} />
          ))}
        </Bar>

        {/* Close line overlay for trend */}
        <Line
          type="monotone"
          dataKey="close"
          stroke={ACCENT2}
          strokeWidth={1.2}
          dot={false}
          name="Close"
          strokeOpacity={0.35}
          legendType="none"
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

/* ═══════════════════════════════════════════════════ */
/* Volume Chart (bars below candles)                   */
/* ═══════════════════════════════════════════════════ */
export function VolumeBarChart({ data }: { data: PricePoint[] }) {
  if (!data || data.length === 0) return null;
  return (
    <ResponsiveContainer width="100%" height={80}>
      <BarChart data={data} margin={{ top: 0, right: 12, bottom: 0, left: 8 }}>
        <XAxis dataKey="date" hide />
        <YAxis hide />
        <Bar dataKey="volume" barSize={6}>
          {data.map((d, i) => (
            <Cell key={i} fill={d.close >= d.open ? UP : DOWN} fillOpacity={0.4} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

/* ═══════════════════════════════════════════════════ */
/* Price Area Chart (mini)                             */
/* ═══════════════════════════════════════════════════ */
export function PriceAreaChart({ data }: { data: PricePoint[] }) {
  if (!data || data.length === 0) return null;
  const minP = Math.min(...data.map(d => d.close)) * 0.997;
  const maxP = Math.max(...data.map(d => d.close)) * 1.003;
  const isUp = data[data.length - 1]?.close >= data[0]?.close;
  const color = isUp ? UP : DOWN;

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 4 }}>
        <defs>
          <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.15} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID} vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 9, fill: MUTED, fontFamily: "var(--font-mono)" }} stroke="transparent"
          tickFormatter={(v) => v.split(" ")[0]} interval="preserveStartEnd" />
        <YAxis domain={[minP, maxP]} tick={{ fontSize: 9, fill: MUTED, fontFamily: "var(--font-mono)" }} stroke="transparent"
          tickFormatter={(v) => `₹${Number(v).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`} width={64} />
        <Tooltip content={<ChartTooltip />} />
        <Area type="monotone" dataKey="close" stroke={color} fill="url(#areaGrad)"
          strokeWidth={2} dot={false} name="Close Price" />
      </AreaChart>
    </ResponsiveContainer>
  );
}

/* ═══════════════════════════════════════════════════ */
/* CSAD Scatter Plot (Herding)                         */
/* ═══════════════════════════════════════════════════ */
export function CSADScatterPlot({ data }: { data: CSADPoint[] }) {
  if (!data || data.length === 0) return (
    <div style={{ height: 300, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <span style={{ color: "var(--text-muted)", fontSize: 13 }}>Insufficient data</span>
    </div>
  );
  const sorted = [...data].sort((a, b) => a.absReturn - b.absReturn);
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart data={sorted} margin={{ top: 8, right: 12, bottom: 8, left: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
        <XAxis
          dataKey="absReturn"
          tick={{ fontSize: 10, fill: MUTED, fontFamily: "var(--font-mono)" }}
          stroke="transparent"
          tickFormatter={(v) => `${(v * 100).toFixed(1)}%`}
          type="number"
          label={{ value: "|Market Return|", position: "insideBottom", offset: -2, fontSize: 10, fill: MUTED }}
        />
        <YAxis
          tick={{ fontSize: 10, fill: MUTED, fontFamily: "var(--font-mono)" }}
          stroke="transparent"
          tickFormatter={(v) => `${(v * 100).toFixed(2)}%`}
          label={{ value: "CSAD", angle: -90, position: "insideLeft", offset: 10, fontSize: 10, fill: MUTED }}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (!active || !payload?.length) return null;
            const d = payload[0]?.payload;
            return (
              <div className="custom-tooltip">
                <div style={{ display: "flex", justifyContent: "space-between", gap: 16, marginBottom: 2 }}>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>|Mkt Return|</span>
                  <span style={{ fontSize: 11, fontWeight: 600, fontFamily: "var(--font-mono)" }}>{(d?.absReturn * 100).toFixed(3)}%</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>CSAD</span>
                  <span style={{ fontSize: 11, fontWeight: 600, fontFamily: "var(--font-mono)" }}>{(d?.csad * 100).toFixed(3)}%</span>
                </div>
              </div>
            );
          }}
        />
        <Scatter name="Daily Observations" dataKey="csad" fill={ACCENT2} fillOpacity={0.4} r={3} />
        <Line type="monotone" dataKey="fitted" stroke={DOWN} strokeWidth={2.5} dot={false}
          name="CCK Fitted Line" strokeDasharray="6 3" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

/* ═══════════════════════════════════════════════════ */
/* Panic Volume Chart                                  */
/* ═══════════════════════════════════════════════════ */
export function PanicVolumeChart({ data }: { data: VolumePoint[] }) {
  if (!data || data.length === 0) return null;
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID} vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 9, fill: MUTED, fontFamily: "var(--font-mono)" }} stroke="transparent"
          interval={Math.floor(data.length / 8)} />
        <YAxis tick={{ fontSize: 9, fill: MUTED, fontFamily: "var(--font-mono)" }} stroke="transparent"
          tickFormatter={(v) => `${(v / 1e6).toFixed(1)}M`} />
        <Tooltip
          content={({ active, payload, label }) => {
            if (!active || !payload?.length) return null;
            const d = payload[0]?.payload;
            return (
              <div className="custom-tooltip">
                <p style={{ fontSize: 11, fontWeight: 700, marginBottom: 4, fontFamily: "var(--font-mono)" }}>{label}</p>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 16, marginBottom: 2 }}>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Volume</span>
                  <span style={{ fontSize: 11, fontWeight: 600, fontFamily: "var(--font-mono)" }}>{Number(d?.volume).toLocaleString("en-IN")}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 16, marginBottom: 2 }}>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Z-Score</span>
                  <span style={{ fontSize: 11, fontWeight: 600, fontFamily: "var(--font-mono)", color: d?.isPanic ? DOWN : "var(--text)" }}>{d?.zscore?.toFixed(2)}</span>
                </div>
                {d?.isPanic && <div style={{ marginTop: 4, fontSize: 11, fontWeight: 600, color: DOWN }}>⚠ Panic detected</div>}
              </div>
            );
          }}
        />
        <ReferenceLine y={0} stroke={GRID} />
        <Bar dataKey="volume" name="Volume" radius={[3, 3, 0, 0]} barSize={6}>
          {data.map((entry, i) => (
            <Cell key={i} fill={entry.isPanic ? DOWN : ACCENT2} fillOpacity={entry.isPanic ? 0.80 : 0.35} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

/* ═══════════════════════════════════════════════════ */
/* Z-Score Line Chart                                  */
/* ═══════════════════════════════════════════════════ */
export function ZScoreChart({ data }: { data: VolumePoint[] }) {
  if (!data || data.length === 0) return null;
  return (
    <ResponsiveContainer width="100%" height={160}>
      <ComposedChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID} vertical={false} />
        <XAxis dataKey="date" hide />
        <YAxis tick={{ fontSize: 9, fill: MUTED, fontFamily: "var(--font-mono)" }} stroke="transparent" />
        <Tooltip content={<ChartTooltip />} />
        <ReferenceLine y={2} stroke={AMBER} strokeDasharray="4 2" strokeWidth={1.5} label={{ value: "Panic Zone (+2σ)", fontSize: 9, fill: AMBER }} />
        <ReferenceLine y={-2} stroke={ACCENT2} strokeDasharray="4 2" strokeWidth={1.5} />
        <ReferenceLine y={0} stroke={GRID} />
        <Line type="monotone" dataKey="zscore" stroke={ACCENT} strokeWidth={1.5} dot={false} name="Volume Z-Score">
          {data.map((d, i) => (
            <Cell key={i} fill={d.zscore > 2 ? DOWN : d.zscore < -2 ? ACCENT : "transparent"} />
          ))}
        </Line>
        <Bar dataKey={(d: VolumePoint) => d.isPanic ? d.zscore : null} fill={DOWN} fillOpacity={0.15} barSize={4} name="Panic" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

/* ═══════════════════════════════════════════════════ */
/* Monte Carlo Histogram                               */
/* ═══════════════════════════════════════════════════ */
export function MCHistogram({ data }: { data: HistogramBin[] }) {
  if (!data || data.length === 0) return null;
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} barGap={1} margin={{ top: 4, right: 8, bottom: 0, left: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID} vertical={false} />
        <XAxis
          dataKey="binStart"
          tick={{ fontSize: 9, fill: MUTED, fontFamily: "var(--font-mono)" }}
          stroke="transparent"
          tickFormatter={(v) => v >= 1e7 ? `₹${(v / 1e7).toFixed(1)}Cr` : `₹${(v / 1e5).toFixed(0)}L`}
          interval={Math.floor(data.length / 6)}
        />
        <YAxis tick={{ fontSize: 9, fill: MUTED, fontFamily: "var(--font-mono)" }} stroke="transparent" label={{ value: "Simulations", angle: -90, position: "insideLeft", fontSize: 9, fill: MUTED }} />
        <Tooltip content={<ChartTooltip />} />
        <Legend wrapperStyle={{ fontSize: 11, color: MUTED, paddingTop: 8, fontFamily: "var(--font-body)" }} iconType="square" iconSize={8} />
        <Bar dataKey="sip" name="Disciplined SIP" fill={UP} fillOpacity={0.6} radius={[2, 2, 0, 0]} />
        <Bar dataKey="panic" name="Panic Seller" fill={DOWN} fillOpacity={0.6} radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

/* ═══════════════════════════════════════════════════ */
/* Missing Best Days Bar Chart                         */
/* ═══════════════════════════════════════════════════ */
export function MissingDaysChart({ data }: { data: MissingDayScenario[] }) {
  if (!data || data.length === 0) return null;
  const formatted = data.map(d => ({ ...d, label: d.scenario }));
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={formatted} layout="vertical" margin={{ top: 4, right: 16, bottom: 0, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID} horizontal={false} />
        <XAxis
          type="number"
          tick={{ fontSize: 10, fill: MUTED, fontFamily: "var(--font-mono)" }}
          stroke="transparent"
          tickFormatter={(v) => v >= 1e7 ? `₹${(v / 1e7).toFixed(1)}Cr` : `₹${(v / 1e5).toFixed(0)}L`}
        />
        <YAxis
          type="category"
          dataKey="scenario"
          tick={{ fontSize: 10, fill: MUTED, fontFamily: "var(--font-body)" }}
          stroke="transparent"
          width={140}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (!active || !payload?.length) return null;
            const d = payload[0]?.payload;
            return (
              <div className="custom-tooltip">
                <p style={{ fontSize: 11, fontWeight: 700, marginBottom: 6, color: "var(--text)" }}>{d?.scenario}</p>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 16, marginBottom: 2 }}>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Final Value</span>
                  <span style={{ fontSize: 11, fontWeight: 600, fontFamily: "var(--font-mono)" }}>₹{Number(d?.finalValue).toLocaleString("en-IN")}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 16, marginBottom: 2 }}>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Total Return</span>
                  <span style={{ fontSize: 11, fontWeight: 600, fontFamily: "var(--font-mono)", color: d?.totalReturn >= 0 ? UP : DOWN }}>{d?.totalReturn?.toFixed(1)}%</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>CAGR</span>
                  <span style={{ fontSize: 11, fontWeight: 600, fontFamily: "var(--font-mono)" }}>{d?.cagr?.toFixed(1)}% p.a.</span>
                </div>
              </div>
            );
          }}
        />
        <Bar dataKey="finalValue" name="Final Value (₹)" radius={[0, 6, 6, 0]} barSize={22}>
          {data.map((entry, i) => (
            <Cell key={i}
              fill={i === 0 ? UP : DOWN}
              fillOpacity={i === 0 ? 0.75 : Math.min(0.3 + i * 0.08, 0.75)}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}