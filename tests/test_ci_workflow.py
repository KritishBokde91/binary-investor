"""Tests for CI workflow configuration and Phase 1 end-to-end integration requirements.

Phase 1 Step 7: CI & Verification
"""

from pathlib import Path


def test_ci_workflow_structure():
    """Verify GitHub Actions CI workflow runs all required linters, type checks, and services."""
    ci_path = Path(".github/workflows/ci.yml")
    assert ci_path.exists(), ".github/workflows/ci.yml must exist"

    content = ci_path.read_text()

    # Pinned actions
    assert "actions/checkout@v4" in content
    assert "actions/setup-python@v5" in content
    assert "actions/setup-node@v4" in content

    # Services
    assert "timescale/timescaledb" in content
    assert "redis:7-alpine" in content

    # Tools
    assert "ruff" in content
    assert "pytest" in content
    assert "eslint" in content or "npm run lint" in content
    assert "tsc" in content
    assert "npm run build" in content
    assert "pip-audit" in content
    assert "gitleaks" in content
