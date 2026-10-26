"""Inspect Compose privilege boundaries for the autonomous Agent profile."""
from pathlib import Path


def test_compose_agent_does_not_mount_docker_socket():
    compose = (Path(__file__).resolve().parents[1] / "compose.yaml").read_text()
    broker = compose.split("  sandbox-broker:", 1)[1].split("\n  agent:", 1)[0]
    agent = compose.split("  agent:", 1)[1].split("\nvolumes:", 1)[0]
    assert "/var/run/docker.sock:/var/run/docker.sock" in broker
    assert "/var/run/docker.sock" not in agent
    assert "kitt-sandbox-socket:/run/kitt-broker" in broker
    assert "kitt-sandbox-socket:/run/kitt-broker" in agent
    assert 'network_mode: "none"' in broker
    assert "condition: service_healthy" in agent
