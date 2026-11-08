"use client";

import React from "react";

interface Props {
  label: string;
  value: string | number;
  annotation?: string;
  className?: string;
}

export default function MetricTile({
  label,
  value,
  annotation,
  className = "",
}: Props) {
  return (
    <div
      className={`bg-surface-container-low dark:bg-surface-container-low/50 p-3.5 sm:p-4 rounded-xl border border-surface-container-high/60 flex flex-col justify-between ${className}`}
    >
      <span className="text-[11px] sm:text-xs text-on-surface-variant font-medium truncate">
        {label}
      </span>
      <span className="text-base sm:text-lg lg:text-xl font-bold text-on-surface mt-1 tabular-nums tracking-tight">
        {value}
      </span>
      {annotation && (
        <span className="text-[10px] text-on-surface-variant/75 mt-0.5 truncate">
          {annotation}
        </span>
      )}
    </div>
  );
}
