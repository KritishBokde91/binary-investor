"use client";

import { useState, useRef, useEffect } from "react";
import {
  Send, Sparkles, Loader2, ArrowLeft, MessageCircle, RotateCcw,
} from "lucide-react";
import type { ChatMessage } from "@/app/lib/types";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

const STARTERS = [
  { icon: "🐑", cat: "Behavior", label: "What is herd mentality in stock markets?", detail: "Explain with Indian market examples." },
  { icon: "😰", cat: "Psychology", label: "How do I avoid panic selling?", detail: "Give me a practical framework." },
  { icon: "💰", cat: "Strategy", label: "Why is SIP better than lump sum?", detail: "Show me the math." },
  { icon: "📊", cat: "Research", label: "Explain the CCK herding model", detail: "Keep it simple but accurate." },
  { icon: "🧠", cat: "Biases", label: "What cognitive biases affect stock investing?", detail: "And how to overcome them." },
  { icon: "📉", cat: "Crisis", label: "How to stay calm during a market crash?", detail: "Step-by-step mental framework." },
  { icon: "🎯", cat: "Strategy", label: "What is the behavior gap?", detail: "How much does it cost the average Indian investor?" },
  { icon: "🔬", cat: "Research", label: "Explain CSAD and cross-sectional dispersion", detail: "In plain English." },
];

export default function AICopilotPage() {
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
      const res = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: updated.map((m) => ({ role: m.role, content: m.content })),
          context: "",
        }),
      });
      const data = await res.json();
      setMessages([...updated, { role: "assistant", content: data.response }]);
    } catch {
      setMessages([
        ...updated,
        { role: "assistant", content: "Could not reach AI server. Please ensure the Python backend is running." },
      ]);
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Navbar */}
      <nav className="navbar" style={{ padding: "0 24px" }}>
        <div style={{ maxWidth: 1000, margin: "0 auto", height: 60, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Link href="/" style={{ display: "flex", alignItems: "center", gap: 8, textDecoration: "none" }}>
            <ArrowLeft size={16} style={{ color: "var(--text-muted)" }} />
            <span style={{ fontSize: 13, color: "var(--text-secondary)", fontFamily: "var(--font-body)", fontWeight: 500 }}>
              Dashboard
            </span>
          </Link>

          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 28, height: 28, borderRadius: 8, background: "var(--accent-light)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Sparkles size={14} style={{ color: "var(--accent)" }} />
            </div>
            <div>
              <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 15, color: "var(--text)" }}>AI Copilot</span>
              <span style={{ fontSize: 10, color: "var(--text-muted)", marginLeft: 6, fontFamily: "var(--font-mono)" }}>llama-3.3-70b</span>
            </div>
          </div>

          {messages.length > 0 && (
            <button
              className="btn-ghost"
              onClick={() => setMessages([])}
              style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12 }}
            >
              <RotateCcw size={12} /> Clear
            </button>
          )}
          {messages.length === 0 && <div style={{ width: 80 }} />}
        </div>
      </nav>

      {/* Main content */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", maxWidth: 800, margin: "0 auto", width: "100%", padding: "0 24px" }}>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", padding: "32px 0 16px", display: "flex", flexDirection: "column", gap: 14 }}>

          {/* Empty State */}
          {messages.length === 0 && (
            <div className="fade-up" style={{ paddingTop: 16 }}>
              <div style={{ textAlign: "center", marginBottom: 40 }}>
                <div style={{
                  width: 64, height: 64, borderRadius: 20, background: "var(--accent-light)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  margin: "0 auto 16px",
                }}>
                  <Sparkles size={28} style={{ color: "var(--accent)" }} />
                </div>
                <h1 style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: 28, color: "var(--text)", letterSpacing: "-0.02em", marginBottom: 10 }}>
                  Ask me anything
                </h1>
                <p style={{ fontSize: 14, color: "var(--text-secondary)", maxWidth: 480, margin: "0 auto", lineHeight: 1.7, fontFamily: "var(--font-body)" }}>
                  Your personal behavioral finance advisor for Indian stock markets. I can explain biases, analyze strategy, or answer any investing question.
                </p>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                {STARTERS.map((s) => (
                  <button
                    key={s.label}
                    onClick={() => send(s.label)}
                    className="glass"
                    style={{
                      textAlign: "left", padding: "14px 18px", cursor: "pointer",
                      border: "1px solid var(--glass-border)", background: "var(--glass)",
                      transition: "all 0.15s ease", fontFamily: "var(--font-body)",
                    }}
                    onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = "var(--accent-faint)"; (e.currentTarget as HTMLElement).style.borderColor = "rgba(99,102,241,0.2)"; }}
                    onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = "var(--glass)"; (e.currentTarget as HTMLElement).style.borderColor = "var(--glass-border)"; }}
                  >
                    <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
                      <span style={{ fontSize: 20, flexShrink: 0 }}>{s.icon}</span>
                      <div>
                        <div style={{ fontSize: 8, fontWeight: 700, color: "var(--accent)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 3, fontFamily: "var(--font-body)" }}>
                          {s.cat}
                        </div>
                        <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text)", lineHeight: 1.4 }}>{s.label}</div>
                        <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>{s.detail}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Message Bubbles */}
          {messages.map((m, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: m.role === "user" ? "flex-end" : "flex-start",
              }}
            >
              {m.role === "assistant" && (
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                  <div style={{ width: 22, height: 22, borderRadius: 6, background: "var(--accent-light)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <Sparkles size={11} style={{ color: "var(--accent)" }} />
                  </div>
                  <span style={{ fontSize: 10, fontWeight: 700, color: "var(--accent)", textTransform: "uppercase", letterSpacing: "0.08em", fontFamily: "var(--font-body)" }}>
                    AI Copilot
                  </span>
                </div>
              )}
              <div
                className={m.role === "user" ? "chat-user" : "chat-ai"}
                style={{
                  padding: "14px 18px",
                  fontSize: 14,
                  lineHeight: 1.7,
                  maxWidth: "80%",
                  fontFamily: "var(--font-body)",
                }}
              >
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
            </div>
          ))}

          {loading && (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                <div style={{ width: 22, height: 22, borderRadius: 6, background: "var(--accent-light)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Sparkles size={11} style={{ color: "var(--accent)" }} />
                </div>
                <span style={{ fontSize: 10, fontWeight: 700, color: "var(--accent)", textTransform: "uppercase", letterSpacing: "0.08em", fontFamily: "var(--font-body)" }}>
                  AI Copilot
                </span>
              </div>
              <div className="chat-ai" style={{ padding: "14px 18px", display: "flex", alignItems: "center", gap: 10 }}>
                <Loader2 size={14} className="spin-slow" style={{ color: "var(--accent)" }} />
                <span style={{ fontSize: 13, color: "var(--text-muted)", fontFamily: "var(--font-body)" }}>Thinking...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input Area */}
        <div style={{ padding: "16px 0 32px", borderTop: "1px solid var(--glass-border)" }}>
          <div style={{ display: "flex", gap: 10, alignItems: "flex-end" }}>
            <div style={{ flex: 1, position: "relative" }}>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    send(input);
                  }
                }}
                placeholder="Ask about investing biases, stock strategies, or behavioral finance..."
                className="glass"
                rows={1}
                style={{
                  width: "100%", padding: "14px 18px", fontSize: 14,
                  color: "var(--text)", outline: "none", resize: "none",
                  fontFamily: "var(--font-body)", lineHeight: 1.6,
                  border: "1px solid transparent",
                  transition: "border-color 0.15s ease",
                  borderRadius: 16,
                  maxHeight: 120,
                  overflow: "auto",
                }}
                onFocus={e => (e.currentTarget.style.borderColor = "rgba(99,102,241,0.25)")}
                onBlur={e => (e.currentTarget.style.borderColor = "transparent")}
              />
            </div>
            <button
              onClick={() => send(input)}
              disabled={!input.trim() || loading}
              className="btn-primary"
              style={{ padding: "14px 20px", borderRadius: 14, flexShrink: 0, display: "flex", alignItems: "center", gap: 6 }}
            >
              <Send size={15} />
            </button>
          </div>
          <p style={{ fontSize: 10, color: "var(--text-dim)", textAlign: "center", marginTop: 10, fontFamily: "var(--font-body)" }}>
            Powered by Groq · llama-3.3-70b-versatile · Educational use only · Not financial advice
          </p>
        </div>
      </div>
    </div>
  );
}