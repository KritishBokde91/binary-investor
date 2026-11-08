"use client";

import React from "react";

interface Props {
  activeTab: "dashboard" | "copilot" | "learn";
  onChangeTab: (tab: "dashboard" | "copilot" | "learn") => void;
  onOpenCopilot: () => void;
}

export default function MobileTabBar({
  activeTab,
  onChangeTab,
  onOpenCopilot,
}: Props) {
  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-50 pb-safe bg-surface/90 dark:bg-surface/90 backdrop-blur-xl border-t border-surface-container-high/60 shadow-[0_-1px_12px_rgba(0,0,0,0.04)]">
      <div className="h-16 px-4 flex items-center justify-around">
        <button
          type="button"
          onClick={() => onChangeTab("dashboard")}
          className={`flex flex-col items-center justify-center min-w-[64px] min-h-[44px] gap-0.5 transition-colors touch-manipulation cursor-pointer ${
            activeTab === "dashboard"
              ? "text-primary dark:text-primary-fixed font-semibold"
              : "text-on-surface-variant hover:text-on-surface"
          }`}
        >
          <span className="material-symbols-outlined text-[24px]">dashboard</span>
          <span className="text-[11px] font-medium">Dashboard</span>
        </button>

        <button
          type="button"
          onClick={onOpenCopilot}
          className={`flex flex-col items-center justify-center min-w-[64px] min-h-[44px] gap-0.5 transition-colors touch-manipulation cursor-pointer ${
            activeTab === "copilot"
              ? "text-primary dark:text-primary-fixed font-semibold"
              : "text-on-surface-variant hover:text-on-surface"
          }`}
        >
          <span className="material-symbols-outlined text-[24px]">psychology</span>
          <span className="text-[11px] font-medium">Copilot</span>
        </button>

        <a
          href="#methodology"
          onClick={() => onChangeTab("learn")}
          className={`flex flex-col items-center justify-center min-w-[64px] min-h-[44px] gap-0.5 transition-colors touch-manipulation cursor-pointer ${
            activeTab === "learn"
              ? "text-primary dark:text-primary-fixed font-semibold"
              : "text-on-surface-variant hover:text-on-surface"
          }`}
        >
          <span className="material-symbols-outlined text-[24px]">school</span>
          <span className="text-[11px] font-medium">Learn</span>
        </a>
      </div>
    </nav>
  );
}
