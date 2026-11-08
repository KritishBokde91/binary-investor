"use client";

import React from "react";

export type ChipVariant = "calm" | "watch" | "risk" | "edge" | "neutral";

interface Props {
  label: string;
  variant?: ChipVariant;
  icon?: string;
  className?: string;
}

export default function StatusChip({
  label,
  variant = "calm",
  icon,
  className = "",
}: Props) {
  const styles: Record<ChipVariant, { bg: string; iconDefault: string }> = {
    calm: {
      bg: "bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800/50",
      iconDefault: "check_circle",
    },
    watch: {
      bg: "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800/50",
      iconDefault: "warning",
    },
    risk: {
      bg: "bg-red-100 text-red-800 border-red-200 dark:bg-red-950/60 dark:text-red-300 dark:border-red-800/50",
      iconDefault: "error",
    },
    edge: {
      bg: "bg-indigo-100 text-indigo-800 border-indigo-200 dark:bg-indigo-950/60 dark:text-indigo-300 dark:border-indigo-800/50",
      iconDefault: "military_tech",
    },
    neutral: {
      bg: "bg-surface-container text-on-surface-variant border-surface-container-high",
      iconDefault: "info",
    },
  };

  const current = styles[variant] || styles.neutral;
  const iconName = icon || current.iconDefault;

  return (
    <span
      className={`inline-flex items-center gap-1 text-xs font-bold px-2.5 py-0.5 rounded-full border whitespace-nowrap shadow-xs ${current.bg} ${className}`}
    >
      {iconName && <span className="material-symbols-outlined text-[13px]">{iconName}</span>}
      <span>{label}</span>
    </span>
  );
}
