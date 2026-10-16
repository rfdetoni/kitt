"""Installer delegates to the one Agent CLI provisioner, not a parallel Docker path."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from installer import re_lab_delegate as delegate
from installer.re_lab import ReLabError


def test_declines_without_windows_license_or_explicit_install(tmp_path, monkeypatch):
    monkeypatch.setattr(delegate, "check_re_lab", lambda **kw: None)
    for yes, license in [(False, False), (True, False), (False, True)]:
        with pytest.raises(ReLabError, match="--yes and --accept-windows-license"):
            delegate.provision_with_agent(tmp_path, runtime="docker", profile="full",
                                          windows="dockurr", version="11",
                                          yes=yes, accept_license=license)


def test_uses_agent_canonical_entrypoint_not_legacy_provisioner(tmp_path, monkeypatch):
    python = tmp_path / ".venv-agent" / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.touch()
    monkeypatch.setattr(delegate, "check_re_lab", lambda **kw: None)
    requests = []
    def run(args, **kw):
        requests.append(args)
        assert "--state-root" in args and str(tmp_path / "re-lab") in args
        assert args[3:6] == ["re", "lab", "setup"]
        return SimpleNamespace(returncode=0, stdout=json.dumps({
            "status": "PROVISIONING", "oracle_ready": False}), stderr="")
    monkeypatch.setattr(delegate.subprocess, "run", run)
    result = delegate.provision_with_agent(
        tmp_path, runtime="docker", profile="full", windows="dockurr",
        version="11", yes=True, accept_license=True)
    assert result["oracle_ready"] is False
    assert len(requests) == 1
    assert "docker" not in requests[0][:3]


def test_failed_child_does_not_claim_ready(tmp_path, monkeypatch):
    python = tmp_path / ".venv-agent" / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.touch()
    monkeypatch.setattr(delegate, "check_re_lab", lambda **kw: None)
    monkeypatch.setattr(delegate.subprocess, "run", lambda *a, **k:
                        SimpleNamespace(returncode=2, stdout="", stderr="secret"))
    with pytest.raises(ReLabError, match="did not succeed"):
        delegate.provision_with_agent(tmp_path, runtime="docker", profile="full",
                                      windows="dockurr", version="11",
                                      yes=True, accept_license=True)
