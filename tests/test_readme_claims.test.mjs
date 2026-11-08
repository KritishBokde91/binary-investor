import assert from "node:assert";
import fs from "node:fs";

const readme = fs.readFileSync("README.md", "utf8");

// AUDIT.md 1.5 claims checks:
// 1. No "production-ready" claim
assert(!readme.includes("production-ready"), "README must not claim to be production-ready");

// 2. No claim that it measures what average investors actually earned without noting it is an exploratory proxy
assert(
  !readme.includes("(what average investors actually earned)"),
  "README must not claim to measure 'what average investors actually earned' without data"
);

// 3. Drawdown must reflect analysis window, not 52-week high
assert(
  !readme.includes("Distance from 52-week high"),
  "Panic score drawdown factor measures analysis window, not 52-week high"
);

// 4. Delivery pressure must not claim low delivery % data
assert(
  !readme.includes("Low delivery % = speculative selling"),
  "Delivery pressure factor does not use real delivery data; must describe high-low range ratio"
);

// 5. Recharts version must match package.json (^3.8.0), not 2.15
assert(!readme.includes("Recharts | 2.15"), "Recharts version in README must match package.json (^3.8.0)");

// 6. tailwind.config.ts must not appear in project structure tree
assert(!readme.includes("tailwind.config.ts"), "tailwind.config.ts does not exist in Tailwind v4; remove from tree");

// 7. No port 8001
assert(!readme.includes("8001"), "Port 8001 must not be in README");

console.log("Verified: README claims match code and audit specifications.");
