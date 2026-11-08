"use client";

import React from "react";

interface Props {
  value: number; // 0 to 100
  displayValue?: string; // e.g. "34", "18", "86%"
  unit?: string; // e.g. " / 100"
  subtitle?: string; // e.g. "Autonomous", "Orderly Absorbed", "Historical Baseline"
  variant?: "herd" | "panic" | "staying";
}

export default function SemicircleGauge({
  value,
  displayValue,
  unit = " / 100",
  subtitle,
  variant = "herd",
}: Props) {
  const clamped = Math.max(0, Math.min(100, value));
  // Map 0..100 to angle: -90 deg (left) to +90 deg (right), or radius on 180 deg arch
  // Center is (80, 80), radius is 64
  const angle = (clamped / 100) * 180; // 0 to 180
  const needleLength = 48;
  const targetX = 80 - needleLength * Math.cos((angle * Math.PI) / 180);
  const targetY = 80 - needleLength * Math.sin((angle * Math.PI) / 180);

  // Active arc end point for simple SVG arc
  const arcRadius = 64;
  const arcX = 80 - arcRadius * Math.cos((angle * Math.PI) / 180);
  const arcY = 80 - arcRadius * Math.sin((angle * Math.PI) / 180);
  const largeArcFlag = angle > 180 ? 1 : 0;

  // Determine needle/active color
  let activeColor = "#006c4a"; // Green
  if (variant === "staying") {
    activeColor = "#4f46e5"; // Indigo
  } else if (clamped > 60) {
    activeColor = "#ba1a1a"; // Red
  } else if (clamped > 35) {
    activeColor = "#934e00"; // Amber
  }

  const shownText = displayValue !== undefined ? displayValue : `${Math.round(clamped)}`;

  return (
    <div className="flex flex-col items-center justify-center my-3 relative">
      <svg className="w-44 h-24 overflow-visible" viewBox="0 0 160 88" fill="none">
        {/* Background track (180 deg) */}
        <path
          d="M 16 80 A 64 64 0 0 1 144 80"
          stroke="var(--surface-container)"
          strokeWidth="12"
          strokeLinecap="round"
        />

        {/* Multi-band calibration tracks */}
        {variant !== "staying" ? (
          <>
            {/* Low Band (Green) */}
            <path
              d="M 16 80 A 64 64 0 0 1 65 24"
              stroke="#68dba9"
              strokeWidth="12"
              strokeLinecap="round"
            />
            {/* Mid Band (Amber) */}
            <path
              d="M 65 24 A 64 64 0 0 1 115 34"
              stroke="#ffdcc3"
              strokeWidth="12"
            />
            {/* High Band (Red) */}
            <path
              d="M 115 34 A 64 64 0 0 1 144 80"
              stroke="#ffdad6"
              strokeWidth="12"
              strokeLinecap="round"
            />
          </>
        ) : (
          /* Staying power single indigo active band */
          <path
            d={`M 16 80 A 64 64 0 ${largeArcFlag} 1 ${arcX} ${arcY}`}
            stroke="var(--primary-container)"
            strokeWidth="12"
            strokeLinecap="round"
          />
        )}

        {/* Needle indicator */}
        <g>
          <line
            x1="80"
            y1="80"
            x2={targetX}
            y2={targetY}
            stroke={activeColor}
            strokeWidth="3.5"
            strokeLinecap="round"
          />
          <circle cx="80" cy="80" r="5" fill={activeColor} />
        </g>
      </svg>

      <div className="flex flex-col items-center -mt-5">
        <div className="font-headline text-2xl font-black text-on-surface tabular-nums leading-none">
          {shownText}
          {unit && <span className="text-xs text-outline font-semibold">{unit}</span>}
        </div>
        {subtitle && (
          <span
            className="text-[11px] font-medium tracking-wide mt-1"
            style={{ color: activeColor }}
          >
            {subtitle}
          </span>
        )}
      </div>
    </div>
  );
}
