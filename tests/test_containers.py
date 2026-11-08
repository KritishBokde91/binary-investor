"""Tests for Container configurations: multi-stage Dockerfiles and docker-compose stack.

Phase 1 Step 6: Containers
"""

import os
from pathlib import Path


def test_api_dockerfile():
    """Verify Dockerfile.api exists, is multi-stage, non-root, and has healthcheck."""
    dockerfile_path = Path("Dockerfile.api")
    assert dockerfile_path.exists(), "Dockerfile.api must exist"

    content = dockerfile_path.read_text()
    # Pinned base image
    assert "FROM python:3.12-slim" in content
    # Multi-stage
    assert " AS build" in content or " AS builder" in content
    # Non-root user
    assert "useradd" in content
    assert "USER 10001" in content or "USER app" in content
    # Healthcheck hitting /healthz
    assert "HEALTHCHECK" in content
    assert "/healthz" in content


def test_web_dockerfile():
    """Verify Dockerfile.web exists, is multi-stage, non-root, and has healthcheck."""
    dockerfile_path = Path("binary-investor/Dockerfile")
    if not dockerfile_path.exists():
        dockerfile_path = Path("Dockerfile.web")
    assert dockerfile_path.exists(), "Dockerfile.web or binary-investor/Dockerfile must exist"

    content = dockerfile_path.read_text()
    # Multi-stage
    assert " AS deps" in content or " AS build" in content or " AS builder" in content
    # Non-root user
    assert "USER nextjs" in content or "USER node" in content or "USER 10001" in content
    # Healthcheck
    assert "HEALTHCHECK" in content


def test_docker_compose_stack():
    """Verify docker-compose.yml defines postgres, redis, api, and web services."""
    compose_path = Path("docker-compose.yml")
    assert compose_path.exists(), "docker-compose.yml must exist"

    content = compose_path.read_text()
    assert "postgres:" in content
    assert "redis:" in content
    assert "api:" in content
    assert "web:" in content
    assert "timescale/timescaledb" in content
    assert "redis:7-alpine" in content
    assert "depends_on:" in content
