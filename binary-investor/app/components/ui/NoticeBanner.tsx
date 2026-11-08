"use client";

import React from "react";

interface Props {
  title?: string;
  text: string;
  emotionLabel?: string;
}

export default function NoticeBanner({
  title = "Plain English Behavioral Takeaway",
  text,
  emotionLabel,
}: Props) {
  return (
    <section className="mb-8">
      <div className="bg-gradient-to-r from-indigo-50 via-indigo-50/70 to-surface-container-low dark:from-indigo-950/40 dark:via-surface-container-low dark:to-surface-container-low rounded-2xl p-5 sm:p-7 border border-indigo-200 dark:border-indigo-900 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-5">
        <div className="flex items-start gap-4">
          <div className="w-11 h-11 sm:w-12 sm:h-12 rounded-xl bg-primary-container text-on-primary flex items-center justify-center shrink-0 shadow-sm">
            <span className="material-symbols-outlined text-[24px] sm:text-[26px]">psychology</span>
          </div>
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-base sm:text-lg font-bold text-primary dark:text-primary-fixed">{title}</h3>
              {emotionLabel && (
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-secondary bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
                  <span className="material-symbols-outlined text-[13px]">sentiment_calm</span>
                  <span>{emotionLabel}</span>
                </span>
              )}
            </div>
            <p className="text-xs sm:text-sm md:text-base text-on-surface font-normal leading-relaxed max-w-3xl">
              {text}
            </p>
          </div>
        </div>

        <div className="shrink-0 self-start md:self-center">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-surface-container-lowest dark:bg-surface-container-lowest/80 shadow-xs text-on-surface-variant text-[11px] font-semibold border border-surface-container-high whitespace-nowrap">
            <span className="material-symbols-outlined text-[15px] text-amber-700">info</span>
            <span>Educational insights • Not financial advice</span>
          </span>
        </div>
      </div>
    </section>
  );
}
