import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SheepOrSleep — Calm Behavioral Fintech for Indian Stocks",
  description:
    "Detect herding behavior, panic selling, and behavioral gaps in Indian stock picks using the CCK econometric model. Statistical clarity designed to remove emotional bias.",
  keywords: [
    "Indian stocks", "behavioral finance", "herding detection",
    "panic selling", "SIP calculator", "NIFTY 50", "SENSEX",
    "AI copilot", "Monte Carlo", "CCK model",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="h-full antialiased" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-full flex flex-col font-sans bg-surface text-on-surface antialiased selection:bg-primary-fixed selection:text-on-primary-fixed">
        {children}
      </body>
    </html>
  );
}
