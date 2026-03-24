"use client";

import { useState, useMemo, useRef, useEffect } from "react";
import { Search, ChevronDown, X, TrendingUp } from "lucide-react";
import { STOCK_UNIVERSE } from "@/app/lib/stockUniverse";
import type { StockInfo } from "@/app/lib/types";

interface Props {
  selected: StockInfo | null;
  onSelect: (stock: StockInfo) => void;
}

const SECTOR_ICONS: Record<string, string> = {
  "IT": "💻", "Banking": "🏦", "FMCG": "🛒", "Energy": "⚡",
  "Automobile": "🚗", "Pharma": "💊", "Metals": "⚙️", "Financial Services": "💰",
  "Capital Goods": "🏗️", "Consumer Durables": "📺", "Telecom": "📡",
  "Power": "🔋", "Mining": "⛏️", "Healthcare": "🏥", "Real Estate": "🏢",
  "Internet": "🌐", "Travel": "✈️", "Defence": "🛡️", "Conglomerate": "🏛️",
  "Cement": "🧱",
};

export default function StockSelector({ selected, onSelect }: Props) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

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

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 50);
  }, [open]);

  return (
    <div ref={ref} className="relative w-full max-w-xl">
      {/* Trigger */}
      <button
        onClick={() => setOpen(!open)}
        className="glass w-full flex items-center justify-between gap-3 px-5 py-4 text-left cursor-pointer"
        style={{ borderRadius: 18 }}
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: selected ? "var(--accent-light)" : "rgba(30,20,10,0.05)",
            display: "flex", alignItems: "center", justifyContent: "center",
            flexShrink: 0
          }}>
            {selected
              ? <span style={{ fontSize: 16 }}>{SECTOR_ICONS[selected.sector] || "📈"}</span>
              : <Search size={16} style={{ color: "var(--text-muted)" }} />
            }
          </div>
          {selected ? (
            <div className="truncate">
              <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 15, color: "var(--text)" }}>
                {selected.name}
              </div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)", marginTop: 1 }}>
                {selected.symbol.replace(".NS", "")} · {selected.sector} · {selected.index}
              </div>
            </div>
          ) : (
            <div>
              <div style={{ fontFamily: "var(--font-display)", fontWeight: 600, fontSize: 15, color: "var(--text)" }}>
                Search Indian Stocks
              </div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 1 }}>
                NIFTY 50 + NIFTY NEXT 50 · {STOCK_UNIVERSE.length} stocks
              </div>
            </div>
          )}
        </div>
        <ChevronDown
          size={16}
          style={{
            color: "var(--text-muted)",
            transition: "transform 0.2s ease",
            transform: open ? "rotate(180deg)" : "rotate(0deg)",
            flexShrink: 0,
          }}
        />
      </button>

      {/* Dropdown */}
      {open && (
        <div
          className="glass-card absolute z-50 mt-2 w-full overflow-hidden flex flex-col"
          style={{ maxHeight: 440, borderRadius: 20, boxShadow: "var(--glass-shadow-lg)" }}
        >
          {/* Search Input */}
          <div style={{
            display: "flex", alignItems: "center", gap: 10,
            padding: "12px 18px",
            borderBottom: "1px solid var(--glass-border)"
          }}>
            <Search size={15} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
            <input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Company name, symbol, or sector..."
              style={{
                background: "transparent", border: "none", outline: "none",
                fontSize: 14, color: "var(--text)", flex: 1,
                fontFamily: "var(--font-body)",
              }}
            />
            {query && (
              <button onClick={() => setQuery("")} style={{ cursor: "pointer", lineHeight: 0 }}>
                <X size={14} style={{ color: "var(--text-muted)" }} />
              </button>
            )}
          </div>

          {/* Results */}
          <div style={{ overflowY: "auto", flex: 1 }}>
            {grouped.length === 0 ? (
              <div style={{ padding: "32px 16px", textAlign: "center" }}>
                <div style={{ fontSize: 28, marginBottom: 8 }}>🔍</div>
                <p style={{ fontSize: 13, color: "var(--text-muted)" }}>No stocks matching &ldquo;{query}&rdquo;</p>
              </div>
            ) : (
              grouped.map(([sector, stocks]) => (
                <div key={sector}>
                  {/* Sector Header */}
                  <div style={{
                    padding: "6px 18px",
                    fontSize: 10, fontWeight: 700, textTransform: "uppercase",
                    letterSpacing: "0.12em", color: "var(--text-muted)",
                    background: "rgba(30,20,10,0.02)",
                    borderBottom: "1px solid var(--glass-border)",
                    position: "sticky", top: 0, zIndex: 10,
                    display: "flex", alignItems: "center", gap: 6,
                    fontFamily: "var(--font-body)",
                  }}>
                    <span>{SECTOR_ICONS[sector] || "📊"}</span>
                    <span>{sector}</span>
                    <span style={{ background: "rgba(30,20,10,0.06)", borderRadius: 999, padding: "1px 7px", fontSize: 9 }}>
                      {stocks.length}
                    </span>
                  </div>

                  {stocks.map((s) => {
                    const isSelected = selected?.symbol === s.symbol;
                    return (
                      <button
                        key={s.symbol}
                        onClick={() => { onSelect(s); setOpen(false); setQuery(""); }}
                        style={{
                          width: "100%", textAlign: "left",
                          padding: "10px 18px",
                          display: "flex", alignItems: "center", justifyContent: "space-between",
                          cursor: "pointer", border: "none",
                          background: isSelected ? "var(--accent-light)" : "transparent",
                          transition: "background 0.15s ease",
                          fontFamily: "var(--font-body)",
                        }}
                        onMouseEnter={e => { if (!isSelected) (e.currentTarget as HTMLElement).style.background = "rgba(30,20,10,0.03)"; }}
                        onMouseLeave={e => { if (!isSelected) (e.currentTarget as HTMLElement).style.background = "transparent"; }}
                      >
                        <div>
                          <span style={{ fontSize: 13, fontWeight: 500, color: isSelected ? "var(--accent)" : "var(--text)" }}>
                            {s.name}
                          </span>
                          <span style={{
                            marginLeft: 8, fontSize: 10, color: "var(--text-muted)",
                            background: "rgba(30,20,10,0.05)", borderRadius: 6, padding: "2px 6px",
                          }}>
                            {s.index}
                          </span>
                        </div>
                        <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                          {s.symbol.replace(".NS", "")}
                        </span>
                      </button>
                    );
                  })}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}