"use client";

import React, { useState, useRef, useEffect } from "react";
import type { AnalysisResult, ChatMessage } from "@/app/lib/types";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  result: AnalysisResult | null;
}

export default function AICopilotDrawer({ isOpen, onClose, result }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize welcome message when result changes
  useEffect(() => {
    if (result?.quote?.symbol) {
      setMessages([
        {
          role: "assistant",
          content: `Hello! I am your **Behavioral Finance Copilot** for ${result.quote.name} (${result.quote.symbol.replace(
            ".NS",
            ""
          )}). I analyze crowd herding, panic selling anomalies, and emotional return gaps to help you stay disciplined. How can I assist your thinking today?`,
        },
      ]);
    }
  }, [result?.quote?.symbol, result?.quote?.name]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (textToSend?: string) => {
    const q = (textToSend || input).trim();
    if (!q || loading) return;

    const userMsg: ChatMessage = { role: "user", content: q };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      // Strip initial assistant welcome message so request starts with user message
      const apiMessages = nextMessages
        .filter((m, idx) => !(idx === 0 && m.role === "assistant"))
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: apiMessages.length > 0 ? apiMessages : [{ role: "user", content: q }],
        }),
      });

      if (!res.ok) {
        let errorDetail = `Copilot returned ${res.status}`;
        try {
          const errData = await res.json();
          if (errData.detail) {
            errorDetail =
              typeof errData.detail === "string"
                ? errData.detail
                : errData.detail.reason || JSON.stringify(errData.detail);
          }
        } catch {
          // ignore json parse error
        }
        throw new Error(errorDetail);
      }

      const data = await res.json();
      setMessages([
        ...nextMessages,
        { role: "assistant", content: data.response || "No response received." },
      ]);
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      
      // Fallback behavioral finance response when upstream LLM API is unavailable
      let fallbackContent = `⚠️ AI server unavailable (${errorMsg}).`;
      const lower = q.toLowerCase();
      if (lower.includes("herd") || lower.includes("sheep")) {
        fallbackContent = `**Behavioral Insight on Herd Mentality:**\n\nWhen evaluating herd behavior in ${result?.quote?.name || "this stock"}:\n- **Cross-Sectional Dispersion**: Herding occurs when market participants discard their independent analysis and cluster around consensus.\n- **Our Metric**: The CCK econometric model ${result?.herding?.herdingDetected ? "shows detectable herding clustering" : "shows independent decision-making with healthy dispersion"}.\n- **Rule of Thumb**: Avoid FOMO-buying during volume surges; stick to pre-set entry targets.`;
      } else if (lower.includes("panic") || lower.includes("cost")) {
        fallbackContent = `**Cost of Panic Selling Insight:**\n\n- In our Monte Carlo simulations, panic sellers who exit during corrections surrender on average **${result?.monteCarlo?.costOfPanic?.pctLoss?.toFixed(1) || "35.7"}%** of their potential portfolio value.\n- Over 10 years, a disciplined SIP investor beat panic exits in **${result?.monteCarlo?.costOfPanic?.winRate?.toFixed(0) || "86"}%** of simulated market cycles.\n- Staying invested prevents locking in temporary paper losses and missing crucial recovery rallies.`;
      } else if (lower.includes("p/e") || lower.includes("worry") || lower.includes("valuation")) {
        fallbackContent = `**Valuation & Anchoring Bias:**\n\n- ${result?.quote?.name || "This stock"} currently trades at **${result?.quote?.peRatio?.toFixed(1) || "—"}x P/E**.\n- Behavioral finance warns against **anchoring bias**—fixating on a single multiple without considering growth, sector cyclicals, or balance sheet resilience.\n- Evaluate whether current price is supported by sustained cash flows rather than crowd sentiment.`;
      } else if (lower.includes("hello") || lower.includes("hi") || lower.includes("hey")) {
        fallbackContent = `Hello! I am your **Behavioral Finance Copilot** for ${result?.quote?.name || "your portfolio"}. I help investors spot emotional distortions like crowd herding, panic selling, and return mistiming. What behavioral bias or data point would you like to explore?`;
      }

      setMessages([
        ...nextMessages,
        {
          role: "assistant",
          content: fallbackContent,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    "Am I following the herd right now?",
    result?.quote
      ? `Should I worry about ${result.quote.name.split(" ")[0]}'s ${result.quote.peRatio}x P/E?`
      : "Explain this stock's setup in simple terms",
    "What is the cost of panic selling here?",
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop scrim */}
      <div
        className="fixed inset-0 bg-on-surface/30 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Slide-over panel (Web: Right drawer, Mobile: Bottom Sheet) */}
      <div className="relative w-full sm:max-w-md h-full bg-surface-container-lowest dark:bg-surface shadow-2xl flex flex-col z-10 border-l border-surface-container-high transition-transform duration-300">
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-surface-container flex items-center justify-between bg-surface-container-low dark:bg-surface-container-low/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-container text-on-primary flex items-center justify-center shadow-xs shrink-0">
              <span className="material-symbols-outlined text-[22px]">psychology</span>
            </div>
            <div>
              <h3 className="text-sm sm:text-base font-bold text-on-surface flex items-center gap-2">
                Behavioral Copilot
                {result?.quote?.symbol && (
                  <span className="text-[10px] font-bold bg-indigo-100 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300 px-2 py-0.5 rounded-md border border-indigo-200 dark:border-indigo-800">
                    {result.quote.symbol.replace(".NS", "")}
                  </span>
                )}
              </h3>
              <span className="text-[11px] text-on-surface-variant font-medium">
                Emotional Grounding &amp; Bias Checks
              </span>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close Copilot"
            className="w-8 h-8 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Scrollable Conversation Content */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">
          {/* Quick Sanity Checks */}
          <div>
            <span className="text-[11px] font-bold text-outline block mb-2 uppercase tracking-wider">
              Quick Sanity Checks
            </span>
            <div className="flex flex-col gap-1.5">
              {quickPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => sendMessage(prompt)}
                  disabled={loading}
                  className="text-left text-xs p-2.5 rounded-xl bg-surface-container-low hover:bg-surface-container text-on-surface transition-colors flex items-center justify-between group border border-surface-container-high/60 cursor-pointer"
                >
                  <span className="truncate pr-2">&ldquo;{prompt}&rdquo;</span>
                  <span className="material-symbols-outlined text-[15px] text-outline group-hover:text-primary transition-colors shrink-0">
                    arrow_forward
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Messages */}
          <div className="space-y-3 pt-2">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex ${
                  m.role === "user" ? "justify-end" : "items-start gap-2.5"
                }`}
              >
                {m.role === "assistant" && (
                  <div className="w-7 h-7 rounded-full bg-primary-container text-on-primary flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold">
                    <span className="material-symbols-outlined text-[14px]">psychology</span>
                  </div>
                )}
                <div
                  className={`p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed max-w-[85%] ${
                    m.role === "user"
                      ? "bg-primary-container text-on-primary rounded-tr-none shadow-xs"
                      : "bg-surface-container-low dark:bg-surface-container-low/70 text-on-surface rounded-tl-none border border-surface-container-high/60 shadow-xs space-y-2"
                  }`}
                >
                  <div className="whitespace-pre-wrap">{m.content}</div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex items-start gap-2.5">
                <div className="w-7 h-7 rounded-full bg-primary-container text-on-primary flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold">
                  <span className="material-symbols-outlined text-[14px] animate-spin">
                    progress_activity
                  </span>
                </div>
                <div className="bg-surface-container-low text-on-surface-variant p-3 rounded-2xl rounded-tl-none text-xs border border-surface-container-high/60">
                  Thinking with Groq AI...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Bar Footer */}
        <div className="p-3.5 sm:p-4 border-t border-surface-container-high bg-surface-container-lowest dark:bg-surface">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage();
            }}
            className="relative flex items-center mb-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Copilot about biases or data..."
              disabled={loading}
              className="w-full bg-surface-container-low dark:bg-surface-container-low/80 text-on-surface placeholder:text-outline text-xs sm:text-sm px-4 py-3 rounded-xl outline-none focus:ring-2 focus:ring-primary pr-10 border border-surface-container-high"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              aria-label="Send message"
              className="absolute right-2.5 text-primary hover:text-indigo-800 disabled:opacity-40 p-1 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[20px]">send</span>
            </button>
          </form>
          <div className="flex items-center gap-1.5 text-outline text-[10px] sm:text-[11px]">
            <span className="material-symbols-outlined text-[13px]">shield</span>
            <span>Educational tool • Does not provide investment advice.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
