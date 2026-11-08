"""Tests for universal run.sh startup script."""

import os
from pathlib import Path


def test_run_script_attributes_and_content():
    """Verify run.sh is executable and contains both Docker and native fallback execution paths."""
    run_sh = Path("run.sh")
    assert run_sh.exists(), "run.sh must exist"
    assert os.access(run_sh, os.X_OK), "run.sh must be executable"

    content = run_sh.read_text()

    # Shebang
    assert content.startswith("#!/usr/bin/env bash")

    # Docker execution path
    assert "docker compose" in content or "COMPOSE_CMD" in content

    # Native distro fallback path
    assert "python3" in content
    assert "uvicorn" in content
    assert "npm" in content

    # Clean signal trapping
    assert "trap cleanup" in content

    # Target ports
    assert "8000" in content
    assert "3000" in content
