"use client";

import React, { useState, useMemo, useRef, useEffect } from "react";
import { STOCK_UNIVERSE } from "@/app/lib/stockUniverse";
import type { StockInfo } from "@/app/lib/types";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  selected: StockInfo | null;
  onSelect: (stock: StockInfo) => void;
}

export default function StockSelectorModal({
  isOpen,
  onClose,
  selected,
  onSelect,
}: Props) {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery("");
    }
  }, [isOpen]);

  const filtered = useMemo(() => {
    const q = query.toLowerCase().trim();
    if (!q) return STOCK_UNIVERSE;
    return STOCK_UNIVERSE.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        s.symbol.toLowerCase().includes(q) ||
        s.sector.toLowerCase().includes(q)
    );
  }, [query]);

  const grouped = useMemo(() => {
    const map: Record<string, StockInfo[]> = {};
    for (const s of filtered) {
      (map[s.sector] ??= []).push(s);
    }
    return Object.entries(map).sort(([a], [b]) => a.localeCompare(b));
  }, [filtered]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-on-surface/40 backdrop-blur-xs"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-xl max-h-[85vh] bg-surface-container-lowest dark:bg-surface rounded-2xl shadow-2xl border border-surface-container-high flex flex-col overflow-hidden z-10 animate-in fade-in zoom-in-95 duration-150">
        {/* Header & Search Input */}
        <div className="p-4 border-b border-surface-container-high flex items-center gap-3 bg-surface-container-low dark:bg-surface-container-low/70">
          <span className="material-symbols-outlined text-outline text-[22px]">search</span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search company name, symbol, or sector..."
            className="flex-1 bg-transparent text-sm sm:text-base text-on-surface placeholder:text-outline outline-none"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery("")}
              className="text-outline hover:text-on-surface p-1 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">close</span>
            </button>
          )}
          <button
            type="button"
            onClick={onClose}
            className="text-outline hover:text-on-surface p-1 rounded-md cursor-pointer ml-1"
          >
            <span className="material-symbols-outlined text-[20px]">cancel</span>
          </button>
        </div>

        {/* Results List */}
        <div className="flex-1 overflow-y-auto p-2 divide-y divide-surface-container-high/40">
          {grouped.length === 0 ? (
            <div className="p-8 text-center text-on-surface-variant text-sm">
              No Indian stocks matching &ldquo;{query}&rdquo;
            </div>
          ) : (
            grouped.map(([sector, stocks]) => (
              <div key={sector} className="py-2">
                <div className="px-3 py-1 text-[10px] font-bold text-outline uppercase tracking-wider flex items-center justify-between">
                  <span>{sector}</span>
                  <span className="bg-surface-container px-1.5 py-0.5 rounded text-[9px]">
                    {stocks.length}
                  </span>
                </div>
                <div className="grid grid-cols-1 gap-0.5 mt-1">
                  {stocks.map((stock) => {
                    const isSelected = selected?.symbol === stock.symbol;
                    return (
                      <button
                        key={stock.symbol}
                        type="button"
                        onClick={() => {
                          onSelect(stock);
                          onClose();
                        }}
                        className={`w-full text-left px-3 py-2.5 rounded-xl flex items-center justify-between transition-colors cursor-pointer ${
                          isSelected
                            ? "bg-primary-container text-on-primary font-semibold"
                            : "hover:bg-surface-container-low text-on-surface"
                        }`}
                      >
                        <div className="flex items-center gap-2.5 min-w-0">
                          <span className="text-xs sm:text-sm font-bold truncate">
                            {stock.name}
                          </span>
                          <span
                            className={`text-[10px] px-1.5 py-0.5 rounded ${
                              isSelected
                                ? "bg-white/20 text-white"
                                : "bg-surface-container text-on-surface-variant"
                            }`}
                          >
                            {stock.index}
                          </span>
                        </div>
                        <span
                          className={`font-mono text-xs ${
                            isSelected ? "text-white/90" : "text-outline"
                          }`}
                        >
                          {stock.symbol.replace(".NS", "")}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2.5 bg-surface-container-low dark:bg-surface-container-low/70 border-t border-surface-container-high flex items-center justify-between text-[11px] text-outline">
          <span>NIFTY 50 + NIFTY NEXT 50 • 54 Stocks</span>
          <span>Press ESC to close</span>
        </div>
      </div>
    </div>
  );
}
