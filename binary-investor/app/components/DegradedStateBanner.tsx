"use client";

import React from "react";

interface Props {
  reason?: string | null;
  onRetry?: () => void;
}

export default function DegradedStateBanner({ reason, onRetry }: Props) {
  return (
    <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800/60 rounded-2xl p-6 sm:p-7 shadow-sm my-6">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/60 text-amber-800 dark:text-amber-300 flex items-center justify-center shrink-0 border border-amber-300">
            <span className="material-symbols-outlined text-[24px]">warning</span>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-amber-950 dark:text-amber-200">
                Incomplete Market Data • Verdict Suppressed
              </h3>
              <span className="bg-amber-200 dark:bg-amber-900 text-amber-900 dark:text-amber-200 text-[10px] font-bold px-2 py-0.5 rounded uppercase">
                Degraded
              </span>
            </div>
            <p className="text-xs sm:text-sm text-amber-900/90 dark:text-amber-300/90 leading-relaxed max-w-2xl">
              Market data feeds for this stock or its sector peers are currently degraded or incomplete
              {reason ? ` (${reason})` : ""}. To maintain strict empirical integrity and avoid generating false-positive signals on partial inputs, behavioral verdicts and calibrated gauges are temporarily suspended.
            </p>
          </div>
        </div>

        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="self-start sm:self-center px-4 py-2 rounded-xl bg-amber-200 dark:bg-amber-900 hover:bg-amber-300 text-amber-950 dark:text-amber-100 text-xs font-bold transition-colors shadow-xs cursor-pointer whitespace-nowrap"
          >
            Retry Analysis
          </button>
        )}
      </div>
    </div>
  );
}
