"""Compose trust boundary for explicitly authorized GitHub publishing."""
from pathlib import Path


def test_compose_publish_defaults_disabled_and_agent_only():
    text = (Path(__file__).resolve().parents[1] / "compose.yaml").read_text()
    broker = text.split("  sandbox-broker:", 1)[1].split("\n  agent:", 1)[0]
    agent = text.split("  agent:", 1)[1].split("\nvolumes:", 1)[0]
    assert 'KITT_AUTOPILOT_PUBLISH_ENABLED: "${KITT_AUTOPILOT_PUBLISH_ENABLED:-false}"' in agent
    assert "KITT_AUTOPILOT_GITHUB_TOKEN_FILE" in agent
    assert "KITT_AUTOPILOT_GITHUB_TOKEN_FILE" not in broker
    assert "/var/run/docker.sock" not in agent
    assert "/var/run/docker.sock:/var/run/docker.sock" in broker
