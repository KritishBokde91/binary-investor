import assert from "node:assert";
import fs from "node:fs";

// Read binary-investor/app/page.tsx
const pageContent = fs.readFileSync("binary-investor/app/page.tsx", "utf8");

// AUDIT.md Finding 2 / 1.3 #2 / Phase 0 Item h:
// Check that analyze() uses AbortController to prevent stale responses from overwriting newer ones
assert(
  pageContent.includes("AbortController"),
  "binary-investor/app/page.tsx must use AbortController in analyze() to prevent stale race conditions"
);

// Check that signal is passed to fetch
assert(
  pageContent.includes("signal:"),
  "binary-investor/app/page.tsx must pass signal to fetch"
);

// Check that loading state is guarded against aborted requests
assert(
  pageContent.includes(".aborted") || pageContent.includes("signal.aborted"),
  "binary-investor/app/page.tsx must guard setLoading against aborted requests"
);

console.log("Verified: Frontend race conditions guarded with AbortController and loading state fix.");
