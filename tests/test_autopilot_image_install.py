"""Trusted installer preflights a sandbox image without unsafe fallbacks."""
from types import SimpleNamespace
from unittest.mock import patch

from installer.cli import prepare_autopilot_image


def test_no_docker_is_explicit():
    with patch("installer.cli.shutil.which", return_value=None):
        assert prepare_autopilot_image()["status"] == "unavailable"


def test_existing_docker_image_does_not_pull():
    calls = []

    def run(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    with patch("installer.cli.shutil.which", return_value="/usr/bin/docker"), (
        patch("installer.cli.subprocess.run", side_effect=run)
    ):
        result = prepare_autopilot_image()

    assert result["status"] == "ready" and result["source"] == "cache"
    assert not any("pull" in x for x in calls)


def test_image_pull_failure_is_not_silently_ignored():
    codes = [0, 1, 1]

    def run(_argv, **_kwargs):
        code = codes.pop(0)
        return SimpleNamespace(returncode=code, stdout="", stderr="network failure")

    with patch("installer.cli.shutil.which", return_value="/usr/bin/docker"), (
        patch("installer.cli.subprocess.run", side_effect=run)
    ):
        result = prepare_autopilot_image()

    assert result["status"] == "failed"
    assert "network failure" in result["reason"]
