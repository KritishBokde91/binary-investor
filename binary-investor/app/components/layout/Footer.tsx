"use client";

import React from "react";

export default function Footer() {
  return (
    <footer className="w-full bg-surface-container-lowest dark:bg-surface/80 border-t border-surface-container-high/80 py-8 mt-auto">
      <div className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-md bg-primary-container text-on-primary flex items-center justify-center text-xs">
            <span className="material-symbols-outlined text-[16px]">psychology</span>
          </div>
          <span className="font-headline text-base font-bold text-on-surface">SheepOrSleep</span>
        </div>

        <p className="text-xs text-on-surface-variant text-center md:text-left font-medium max-w-md">
          SheepOrSleep is an educational tool and does not provide investment advice.
        </p>

        <div className="flex items-center gap-5 text-xs text-on-surface-variant font-medium">
          <a
            href="#compliance"
            onClick={(e) => {
              e.preventDefault();
              alert(
                "Compliance Notice: SheepOrSleep computes econometric models (Chang, Cheng & Khorana, 2000) for research and educational purposes. Past performance does not guarantee future results."
              );
            }}
            className="hover:text-primary transition-colors"
          >
            Compliance Disclaimers
          </a>
          <span>•</span>
          <span className="text-[11px] text-outline">CCK Behavioral Research</span>
        </div>
      </div>
    </footer>
  );
}
