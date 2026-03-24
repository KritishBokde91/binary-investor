"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Loader2, ExternalLink } from "lucide-react";
import type { ChatMessage, AnalysisResult } from "@/app/lib/types";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  result: AnalysisResult | null;
}

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AICopilotPanel({ result }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: ChatMessage = { role: "user", content: text.trim() };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const context = result
        ? `Analyzing: ${result.quote.name} (${result.quote.symbol})
Price: ₹${result.quote.price} | Change: ${result.quote.changePct?.toFixed(2)}%
Herding: ${result.herding.herdingDetected ? "DETECTED" : "NOT detected"} | Intensity: ${result.herding.intensity?.toFixed(2)}
Panic Score: ${result.panic.panicScore?.toFixed(1)} (${result.panic.level})
Behavior Gap: ${result.behaviorGap.behaviorGap?.toFixed(2)}% per year
P/E Ratio: ${result.quote.peRatio} | Market Cap: ₹${result.quote.marketCap}`
        : "";

      const res = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: updated.map((m) => ({ role: m.role, content: m.content })),
          context,
        }),
      });
      const data = await res.json();
      setMessages([...updated, { role: "assistant", content: data.response }]);
    } catch {
      setMessages([...updated, { role: "assistant", content: "⚠️ Could not reach AI server." }]);
    }
    setLoading(false);
  };

  const quickActions = result ? [
    { label: "🐑 Am I being a sheep?", prompt: `I'm looking at ${result.quote.name}. The herding score is ${result.herding.intensity?.toFixed(2)}. Am I falling into herd mentality?` },
    { label: "😰 Should I worry?", prompt: `${result.quote.name} has a panic score of ${result.panic.panicScore?.toFixed(1)} (${result.panic.level}). What should I do?` },
    { label: "💡 Explain the gap", prompt: `My behavior gap for ${result.quote.name} is ${result.behaviorGap.behaviorGap?.toFixed(2)}% per year. What does this mean in rupees?` },
  ] : [
    { label: "🐑 What is herd mentality?", prompt: "Explain herd mentality in Indian stock markets with examples." },
    { label: "😰 How to avoid panic?", prompt: "How do I avoid panic selling during a market crash?" },
    { label: "💰 Why SIP beats timing?", prompt: "Why does SIP beat market timing for most Indian investors?" },
  ];

  return (
    <div className="glass-card flex flex-col" style={{ height: 460 }}>
      {/* Header */}
      <div style={{
        padding: "14px 18px",
        borderBottom: "1px solid var(--glass-border)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 8,
            background: "var(--accent-light)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <Sparkles size={14} style={{ color: "var(--accent)" }} />
          </div>
          <div>
            <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 13, color: "var(--text)" }}>
              AI Copilot
            </div>
            <div style={{ fontSize: 10, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
              llama-3.3-70b
            </div>
          </div>
        </div>
        <Link href="/copilot" style={{ display: "flex", alignItems: "center", gap: 4, textDecoration: "none" }}>
          <span style={{ fontSize: 11, color: "var(--accent)", fontWeight: 500 }}>Full Chat</span>
          <ExternalLink size={11} style={{ color: "var(--accent)" }} />
        </Link>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "14px 16px 8px", display: "flex", flexDirection: "column", gap: 10 }}>
        {messages.length === 0 && (
          <div style={{ textAlign: "center", paddingTop: 16 }}>
            <Sparkles size={24} style={{ color: "var(--accent)", margin: "0 auto 10px", opacity: 0.5 }} />
            <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 12, lineHeight: 1.5 }}>
              {result ? `Ask about ${result.quote.name}` : "Select a stock to get personalized insights"}
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {quickActions.map((a) => (
                <button
                  key={a.label}
                  onClick={() => send(a.prompt)}
                  className="glass-subtle"
                  style={{
                    padding: "8px 12px", cursor: "pointer", border: "1px solid var(--glass-border)",
                    textAlign: "left", fontSize: 12, color: "var(--text-secondary)",
                    transition: "all 0.15s ease", fontFamily: "var(--font-body)",
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = "var(--accent-faint)")}
                  onMouseLeave={e => (e.currentTarget.style.background = "")}
                >
                  {a.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={m.role === "user" ? "chat-user" : "chat-ai"}
            style={{
              padding: "10px 14px",
              fontSize: 12,
              lineHeight: 1.6,
              maxWidth: "90%",
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              fontFamily: "var(--font-body)",
            }}
          >
            {m.role === "assistant" && (
              <div style={{ display: "flex", alignItems: "center", gap: 5, marginBottom: 4 }}>
                <Sparkles size={10} style={{ color: "var(--accent)" }} />
                <span style={{ fontSize: 10, fontWeight: 700, color: "var(--accent)", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                  AI Copilot
                </span>
              </div>
            )}
            {m.role === "assistant" ? (
              <div className="markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {m.content}
                </ReactMarkdown>
              </div>
            ) : (
              <div style={{ whiteSpace: "pre-wrap" }}>{m.content}</div>
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-ai" style={{ padding: "10px 14px", display: "flex", alignItems: "center", gap: 8, alignSelf: "flex-start" }}>
            <Loader2 size={12} className="spin-slow" style={{ color: "var(--accent)" }} />
            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Thinking...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ padding: "10px 14px", borderTop: "1px solid var(--glass-border)" }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send(input)}
            placeholder="Ask anything..."
            className="glass-inset"
            style={{
              flex: 1, padding: "9px 14px", fontSize: 12,
              color: "var(--text)", outline: "none", border: "1px solid transparent",
              fontFamily: "var(--font-body)",
              transition: "border-color 0.15s ease",
            }}
            onFocus={e => (e.currentTarget.style.borderColor = "rgba(99,102,241,0.3)")}
            onBlur={e => (e.currentTarget.style.borderColor = "transparent")}
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className="btn-primary"
            style={{ padding: "9px 14px", borderRadius: 10, flexShrink: 0 }}
          >
            <Send size={13} />
          </button>
        </div>
      </div>
    </div>
  );
}