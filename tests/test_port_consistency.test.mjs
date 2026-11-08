import assert from "node:assert";
import fs from "node:fs";

// 1. Read files
const serverPy = fs.readFileSync("server.py", "utf8");
const readme = fs.readFileSync("README.md", "utf8");
const pageTsx = fs.readFileSync("binary-investor/app/page.tsx", "utf8");
const aiCopilotTsx = fs.readFileSync("binary-investor/app/components/AICopilot.tsx", "utf8");
const copilotPageTsx = fs.readFileSync("binary-investor/app/copilot/page.tsx", "utf8");

// 2. copilot/page.tsx must NOT have 8001 and must have 8000
assert(
  !copilotPageTsx.includes("8001"),
  "binary-investor/app/copilot/page.tsx must not default to port 8001"
);
assert(
  copilotPageTsx.includes("8000"),
  "binary-investor/app/copilot/page.tsx must default to port 8000"
);

// 3. page.tsx and AICopilot.tsx must agree on NEXT_PUBLIC_API_URL and 8000
assert(pageTsx.includes("process.env.NEXT_PUBLIC_API_URL || \"http://localhost:8000\""));
assert(aiCopilotTsx.includes("process.env.NEXT_PUBLIC_API_URL || \"http://localhost:8000\""));
assert(copilotPageTsx.includes("process.env.NEXT_PUBLIC_API_URL || \"http://localhost:8000\""));

// 4. server.py must support PORT env var and default to 8000
assert(serverPy.includes("os.getenv(\"PORT\"") || serverPy.includes("os.environ.get(\"PORT\""));
assert(serverPy.includes("8000"));

// 5. README must agree on 8000 (not 8001)
assert(!readme.includes("8001"), "README.md must not reference port 8001");
assert(readme.includes("8000"), "README.md must reference port 8000");

console.log("Verified: Port consistency across all backend, frontend, and doc files.");
