import pytest
from pathlib import Path


def test_requirements_pinned_and_unused_removed():
    """
    AUDIT.md Finding 1.2 row 79 & Phase 0 Item j:
    Pin Python dependencies in requirements.txt and remove unused ones
    (scikit-learn, beautifulsoup4).
    """
    req_path = Path("requirements.txt")
    assert req_path.exists(), "requirements.txt must exist"

    lines = [
        line.strip()
        for line in req_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

    # Verify scikit-learn and beautifulsoup4 are removed
    for line in lines:
        assert "scikit-learn" not in line.lower(), "scikit-learn must be removed from requirements.txt"
        assert "beautifulsoup4" not in line.lower(), "beautifulsoup4 must be removed from requirements.txt"

    # Verify all dependencies are pinned with '=='
    for line in lines:
        assert "==" in line, f"Dependency '{line}' in requirements.txt must be pinned with '=='"
