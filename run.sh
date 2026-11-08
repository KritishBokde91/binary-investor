#!/usr/bin/env bash
# ==============================================================================
# SheepOrSleep (binary-investor) — One-Click Setup & Launch Script
# Target: Linux (Ubuntu, Debian, Fedora, Arch, Alpine, CentOS, openSUSE, etc.)
# ==============================================================================

set -e

# ANSI color codes
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}"
echo "=================================================================="
echo "         🐑 SheepOrSleep (binary-investor) Setup & Run            "
echo "=================================================================="
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}ℹ .env not found. Creating from .env.example...${NC}"
        cp .env.example .env
    else
        echo -e "${YELLOW}ℹ Creating default .env...${NC}"
        cat <<EOF > .env
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
EOF
    fi
fi

# Detect whether Docker daemon is active and responsive
HAS_DOCKER=false
if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        HAS_DOCKER=true
    fi
fi

# ------------------------------------------------------------------------------
# MODE A: DOCKER COMPOSE DEPLOYMENT (Recommended when Docker is active)
# ------------------------------------------------------------------------------
if [ "$HAS_DOCKER" = true ]; then
    echo -e "${GREEN}✔ Docker daemon detected.${NC}"
    echo -e "${BLUE}▶ Launching complete stack with Docker Compose (Postgres, Redis, API, Web)...${NC}"
    
    COMPOSE_CMD="docker compose"
    if ! docker compose version >/dev/null 2>&1; then
        if command -v docker-compose >/dev/null 2>&1; then
            COMPOSE_CMD="docker-compose"
        else
            echo -e "${YELLOW}⚠ Docker Compose plugin not found. Falling back to native local mode...${NC}"
            HAS_DOCKER=false
        fi
    fi
fi

if [ "$HAS_DOCKER" = true ]; then
    $COMPOSE_CMD up --build -d

    echo -e "${GREEN}✔ Containers launched successfully in background.${NC}"
    echo ""
    echo -e "${BOLD}Services are live at:${NC}"
    echo -e "  🌐 Frontend Web UI:  ${BOLD}${GREEN}http://localhost:3000${NC}"
    echo -e "  ⚡ Backend REST API: ${BOLD}${BLUE}http://localhost:8000${NC}"
    echo -e "  🩺 Healthcheck:      ${BOLD}http://localhost:8000/healthz${NC}"
    echo -e "  📊 Metrics Endpoint: ${BOLD}http://localhost:8000/api/metrics${NC}"
    echo ""
    echo -e "To view live logs:    ${YELLOW}$COMPOSE_CMD logs -f${NC}"
    echo -e "To stop all services: ${YELLOW}$COMPOSE_CMD down${NC}"
    echo ""

    # Attempt to open browser if running in desktop graphical session
    if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
        if command -v xdg-open >/dev/null 2>&1; then
            echo -e "${BLUE}Opening browser at http://localhost:3000 ...${NC}"
            xdg-open "http://localhost:3000" >/dev/null 2>&1 || true
        fi
    fi
    exit 0
fi

# ------------------------------------------------------------------------------
# MODE B: NATIVE LOCAL DEPLOYMENT (Universal Linux Distro Fallback)
# ------------------------------------------------------------------------------
echo -e "${YELLOW}▶ Docker not active or unavailable. Initializing native local environment...${NC}"

# Check for Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}✘ Error: python3 is required. Please install python3 on your system.${NC}"
    exit 1
fi

# Check for Node & npm
if ! command -v npm >/dev/null 2>&1; then
    echo -e "${RED}✘ Error: npm is required to run the frontend web UI. Please install Node.js and npm.${NC}"
    exit 1
fi

# 1. Setup Python Virtual Environment
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}▶ Creating Python virtual environment at .venv ...${NC}"
    python3 -m venv "$VENV_DIR" || {
        echo -e "${RED}✘ Failed to create virtual environment. Ensure 'python3-venv' is installed.${NC}"
        exit 1
    }
fi

echo -e "${BLUE}▶ Installing Python dependencies ...${NC}"
"$VENV_DIR/bin/pip" install --upgrade pip >/dev/null 2>&1
"$VENV_DIR/bin/pip" install -r requirements.txt

# 2. Setup Frontend Dependencies
echo -e "${BLUE}▶ Installing Frontend Node dependencies ...${NC}"
cd "$SCRIPT_DIR/binary-investor"
if [ ! -d "node_modules" ]; then
    npm install
fi
cd "$SCRIPT_DIR"

# 3. Process management trap to cleanly terminate background services on exit
API_PID=""
WEB_PID=""

cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping SheepOrSleep services...${NC}"
    if [ -n "$API_PID" ] && kill -0 "$API_PID" 2>/dev/null; then
        kill "$API_PID" 2>/dev/null || true
    fi
    if [ -n "$WEB_PID" ] && kill -0 "$WEB_PID" 2>/dev/null; then
        kill "$WEB_PID" 2>/dev/null || true
    fi
    echo -e "${GREEN}✔ All processes stopped cleanly.${NC}"
}
trap cleanup INT TERM EXIT

# 4. Start Backend API
echo -e "${GREEN}▶ Starting FastAPI Backend on http://localhost:8000 ...${NC}"
"$VENV_DIR/bin/uvicorn" server:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait briefly for backend port to be responsive
sleep 2

# 5. Start Frontend Next.js app
echo -e "${GREEN}▶ Starting Next.js Frontend on http://localhost:3000 ...${NC}"
cd "$SCRIPT_DIR/binary-investor"
npm run dev -- -p 3000 &
WEB_PID=$!
cd "$SCRIPT_DIR"

sleep 3

echo ""
echo -e "${BOLD}${GREEN}=================================================================="
echo -e "  🎉 SheepOrSleep is running!"
echo -e "  🌐 Open Website:     ${BOLD}http://localhost:3000${NC}"
echo -e "  ⚡ API Documentation: http://localhost:8000/docs"
echo -e "  🩺 API Health:        http://localhost:8000/healthz"
echo -e "${BOLD}${GREEN}=================================================================="
echo -e "${NC}"
echo -e "${YELLOW}Press [Ctrl+C] to stop all services.${NC}"

# Open browser if graphical environment is available
if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:3000" >/dev/null 2>&1 || true
    fi
fi

# Keep script running and wait for background jobs
wait "$API_PID" "$WEB_PID"
