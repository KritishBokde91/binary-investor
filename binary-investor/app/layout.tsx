import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SheepOrSleep — AI Behavioral Bias Detector for Indian Stocks",
  description:
    "Detect herding behavior, panic selling, and behavioral gaps in Indian stock markets using the CCK econometric model. Free one-tap comprehensive analysis.",
  keywords: [
    "Indian stocks", "behavioral finance", "herding detection",
    "panic selling", "SIP calculator", "NIFTY 50", "SENSEX",
    "AI copilot", "Monte Carlo",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="h-full antialiased">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}