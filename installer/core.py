from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .catalog import EcosystemCatalog, ModuleSpec, Resolution
from .platforms import CommandInfo, PlatformAdapter


class InstallerError(RuntimeError):
    pass


_GENERATED_ARTIFACTS = {
    "protocol": ("sdk/python/build",),
    "toolbox": ("Cargo.lock",),
    "assistant": ("packages/kitt-assistant-runtime/build",),
    "ai-workers": (
        "build",
        "packages/kitt-evals/build",
        "packages/kitt-evolution/build",
    ),
}


@dataclass(frozen=True)
class InstallerOptions:
    root: Path
    bin_dir: Path
    force: bool = False
    ref: str | None = None
    channel: str = "edge"
    component_refs: dict[str, str] | None = None
    with_ai_workers: bool = False
    portable: bool = False
    dry_run: bool = False
    start_services: bool = True
    auto_prerequisites: bool = False


@dataclass(frozen=True)
class PrerequisiteReport:
    python: CommandInfo | None
    missing: tuple[str, ...]
    found: dict[str, str]


class EcosystemInstaller:
    """Shared installer invariants used by the source-free runtime installer."""

    def __init__(
        self,
        catalog: EcosystemCatalog,
        platform: PlatformAdapter,
        options: InstallerOptions,
    ) -> None:
        self.catalog = catalog
        self.platform = platform
        self.options = options
        self._created_repos: list[Path] = []
        self._previous_revisions: dict[Path, str] = {}
        self._resolved_revisions: dict[str, str] = {}
        self._python: CommandInfo | None = None
        self._venv_final: Path | None = None
        self._venv_backup: Path | None = None
        self._launcher_backups: dict[Path, bytes | None] = {}

    def uninstall(self) -> None:
        if self.options.dry_run:
            print(f"Would remove {self.options.root}")
            return
        launchers = self._state_launchers()
        for value in launchers:
            path = Path(value)
            try:
                if path.exists() or path.is_symlink():
                    path.unlink()
            except OSError:
                pass
        if self.options.root.exists():
            shutil.rmtree(self.options.root)
        print("K.I.T.T. ecosystem removed.")

    def _validate_platforms(self, modules: Iterable[ModuleSpec]) -> None:
        unsupported = [
            module.id
            for module in modules
            if not self.platform.supports(module.platforms)
        ]
        if unsupported:
            raise InstallerError(
                f"platform {self.platform.name!r} is not declared for modules: {', '.join(unsupported)}"
            )

    @staticmethod
    def _parse_requirement(requirement: str) -> tuple[str, tuple[int, ...]]:
        match = re.fullmatch(r"([a-zA-Z0-9_-]+)(?:>=(\d+(?:\.\d+)*))?", requirement)
        if not match:
            raise InstallerError(f"invalid prerequisite declaration: {requirement}")
        version = tuple(int(part) for part in (match.group(2) or "").split(".") if part)
        return match.group(1).lower(), version

    def _check_prerequisites(self, modules: Iterable[ModuleSpec]) -> PrerequisiteReport:
        requested: dict[str, tuple[int, ...]] = {}
        for module in modules:
            for declaration in module.prerequisites:
                name, minimum = self._parse_requirement(declaration)
                if self.options.portable and name == "rust":
                    continue
                current = requested.get(name, ())
                if minimum > current:
                    requested[name] = minimum
                else:
                    requested.setdefault(name, current)

        rust_minimum = requested.get("rust", ())
        if "rust" in requested:
            minimum = requested.pop("rust")
            requested["cargo"] = minimum
            requested["rustc"] = minimum

        found: dict[str, str] = {}
        missing: list[str] = []
        python: CommandInfo | None = None
        for name, minimum in sorted(requested.items()):
            if name == "python":
                minimum2 = (minimum + (0, 0))[:2] if minimum else (3, 12)
                info = self.platform.find_python(minimum2)
                python = info
            else:
                info = self.platform.command_info(name)
            if info is None:
                missing.append("rust" if name in {"cargo", "rustc"} else name)
                continue
            if minimum and info.version and info.version < minimum:
                label = "rust" if name in {"cargo", "rustc"} else name
                missing.append(f"{label}>={'.'.join(map(str, minimum))}")
                continue
            found[name] = info.version_text or "found"

        if any(value == "rust" or value.startswith("rust>=") for value in missing):
            missing = [
                value
                for value in missing
                if not value.startswith("cargo") and not value.startswith("rustc")
            ]
            missing = [value for value in missing if not value.startswith("rust")]
            label = "rust"
            if rust_minimum:
                label += ">=" + ".".join(map(str, rust_minimum))
            missing.append(label)
        return PrerequisiteReport(
            python=python,
            missing=tuple(dict.fromkeys(missing)),
            found=found,
        )

    @staticmethod
    def _missing_rust_minimum(missing: Iterable[str]) -> tuple[int, ...] | None:
        minimum: tuple[int, ...] | None = None
        for item in missing:
            if item == "rust":
                candidate = (1, 85)
            elif item.startswith("rust>="):
                try:
                    candidate = tuple(int(part) for part in item.split(">=", 1)[1].split("."))
                except ValueError:
                    continue
            else:
                continue
            if minimum is None or candidate > minimum:
                minimum = candidate
        return minimum

    def _prepare_prerequisites(self, modules: Iterable[ModuleSpec]) -> PrerequisiteReport:
        modules = tuple(modules)
        report = self._check_prerequisites(modules)
        self._python = report.python
        if not report.missing or not self.options.auto_prerequisites or self.options.dry_run:
            return report

        rust_minimum = self._missing_rust_minimum(report.missing)
        if rust_minimum is not None:
            wanted = ".".join(map(str, rust_minimum))
            print(f"\nBootstrap Rust >={wanted} with user-local rustup")
            try:
                info = self.platform.install_rust(rust_minimum)
            except RuntimeError as exc:
                raise InstallerError(f"automatic Rust bootstrap failed: {exc}") from exc
            print(f"    Rust ready: {info.version_text}")
            report = self._check_prerequisites(modules)
            self._python = report.python
        return report

    def _print_plan(self, resolution: Resolution, report: PrerequisiteReport) -> None:
        print(f"\nK.I.T.T. installation plan ({self.platform.name})")
        print(f"Root: {self.options.root}")
        print(f"Bin:  {self.options.bin_dir}")
        print("Requested: " + ", ".join(resolution.requested))
        print("Resolved modules:")
        requested = set(resolution.requested)
        for module in resolution.modules:
            if module.id in requested:
                reason = "selected"
            else:
                parents = ", ".join(resolution.auto_selected_by.get(module.id, ()))
                reason = f"automatic via {parents}" if parents else "automatic"
            ref = self.catalog.resolve_ref(
                module, self.options.ref, self.options.component_refs
            )
            print(f"  - {module.name:<22} {reason:<28} {ref[:12]}")
        if self.options.with_ai_workers and "ai-workers" in resolution.ids:
            print("  - AI/STT worker extras      enabled")
        if self.options.portable:
            print("  - Native Rust build         explicitly disabled (--portable)")
        if report.found:
            print("Prerequisites detected:")
            for name, version in sorted(report.found.items()):
                print(f"  - {name}: {version}")

    def _repo_dir(self, module: ModuleSpec) -> Path:
        return self.options.root / module.repository.split("/", 1)[1]

    def _run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        quiet: bool = False,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        display = " ".join(str(value) for value in argv)
        if not quiet:
            print(f"    $ {display}")
        proc = subprocess.run(
            [str(value) for value in argv],
            cwd=str(cwd) if cwd else None,
            env=env,
            text=True,
            stdout=subprocess.PIPE if quiet else None,
            stderr=subprocess.STDOUT if quiet else None,
            check=False,
        )
        if check and proc.returncode != 0:
            output = (proc.stdout or "").strip() if quiet else ""
            suffix = f"\n{output}" if output else ""
            raise InstallerError(f"command failed ({proc.returncode}): {display}{suffix}")
        return proc

    def _capture(self, argv: Sequence[str], *, cwd: Path | None = None) -> str:
        proc = self._run(argv, cwd=cwd, quiet=True)
        return (proc.stdout or "").strip()

    def _rollback_repositories(self) -> None:
        if not self._created_repos and not self._previous_revisions:
            return
        print("\nInstallation failed; restoring repository revisions...")
        for path, revision in reversed(list(self._previous_revisions.items())):
            try:
                self._run(["git", "checkout", "--detach", "--force", revision], cwd=path, quiet=True)
                self._run(["git", "clean", "-ffd"], cwd=path, quiet=True)
            except Exception:
                pass
        for path in reversed(self._created_repos):
            try:
                shutil.rmtree(path)
            except OSError:
                pass

    def _playwright_binary(self, proxy: Path) -> Path:
        base = proxy / "node_modules" / ".bin"
        return base / ("playwright.cmd" if self.platform.name == "windows" else "playwright")

    def _has_browser(self) -> bool:
        names = (
            "chrome", "msedge", "google-chrome", "google-chrome-stable",
            "chromium", "chromium-browser",
        )
        return any(shutil.which(name) for name in names)

    def _venv_python(self, venv: Path) -> Path:
        if self.platform.name == "windows":
            return venv / "Scripts" / "python.exe"
        return venv / "bin" / "python"

    def _needs_python_env(self, resolution: Resolution) -> bool:
        return bool({"agent-cli", "ai-workers", "toolbox"} & set(resolution.ids))

    def _commit_python_stack(self, staging: Path | None) -> Path | None:
        if staging is None:
            return None
        final = self.options.root / ".venv-agent"
        backup = self.options.root / ".staging" / "venv-previous"
        if backup.exists():
            shutil.rmtree(backup)
        if final.exists():
            final.rename(backup)
            self._venv_backup = backup
        try:
            staging.rename(final)
        except Exception:
            if backup.exists() and not final.exists():
                backup.rename(final)
                self._venv_backup = None
            raise
        self._venv_final = final
        return final

    def _launcher_path(self, name: str) -> Path:
        suffix = ".cmd" if self.platform.name == "windows" else ""
        return self.options.bin_dir / f"{name}{suffix}"

    def _write_launcher(self, name: str, argv: Sequence[str]) -> Path:
        path = self._launcher_path(name)
        if path not in self._launcher_backups:
            self._launcher_backups[path] = path.read_bytes() if path.is_file() else None
        return self.platform.write_launcher(self.options.bin_dir, name, argv)

    def _smoke_test(self, resolution: Resolution, venv: Path | None) -> None:
        selected = set(resolution.ids)
        print("\nSmoke tests")
        if "agent-cli" in selected:
            if venv is None:
                raise InstallerError("Agent CLI runtime missing")
            python = self._venv_python(venv)
            self._run([str(python), "-m", "kitt.cli.main", "--help"], quiet=True)
            guard_contract = (
                "from pathlib import Path\n"
                "from types import SimpleNamespace\n"
                "from kitt.core.completion_guard import install_completion_guard\n"
                "from kitt.core.execution_request import ExecutionRequest\n"
                "class P:\n"
                "    def _execute_tool_loop(self, cmd, request, exe_profile, exe_client, workspace_id, security_context):\n"
                "        assert request.agent_route == 'code-generation', request.agent_route\n"
                "        yield None, 'ok', list(request.messages)\n"
                "p = P()\n"
                "class R:\n"
                "    root_path = Path('.')\n"
                "install_completion_guard(p, R())\n"
                "request = ExecutionRequest(system_prompt='test', messages=[{'role':'user','content':'hello'}], enabled_tools=[], agent_route='code-generation')\n"
                "cmd = SimpleNamespace(prompt='hello', mode='ask')\n"
                "list(p._execute_tool_loop(cmd, request, object(), object(), 'workspace', object()))\n"
            )
            self._run([str(python), "-c", guard_contract], quiet=True)
            imports = []
            if "assistant" in selected:
                imports.extend(["kitt.daemon.client", "kitt.remote.server"])
            if "ai-workers" in selected:
                imports.extend(["kitt_workers"])
                if "agent-cli" in selected:
                    imports.extend(["kitt.evolution", "kitt.evals.corpus"])
            if imports:
                script = ";".join(f"import {name}" for name in imports)
                self._run([str(python), "-c", script], quiet=True)
            if "toolbox" in selected and not self.options.portable:
                script = (
                    "from kitt.native.bridge import NativeCodeEngine;"
                    f"s=NativeCodeEngine(r'{self._repo_dir(self.catalog.modules['agent-cli'])}').status;"
                    "print(s.backend)"
                )
                backend = self._capture([str(python), "-c", script])
                print(f"    Agent code engine: {backend}")

        if "reverse-proxy" in selected:
            proxy = self._repo_dir(self.catalog.modules["reverse-proxy"])
            node = self.platform.command_info("node")
            if node is None:
                raise InstallerError("Node.js disappeared during installation")
            self._run([*node.argv, str(proxy / "dist" / "cli.js"), "--help"], quiet=True)

    def _rollback_runtime(self) -> None:
        for path, previous in reversed(list(self._launcher_backups.items())):
            try:
                if previous is None:
                    path.unlink(missing_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(previous)
                    if self.platform.name != "windows":
                        path.chmod(0o755)
            except OSError:
                pass
        self._launcher_backups.clear()
        if self._venv_final and self._venv_final.exists():
            shutil.rmtree(self._venv_final, ignore_errors=True)
        if self._venv_backup and self._venv_backup.exists():
            self._venv_backup.rename(self.options.root / ".venv-agent")
        self._venv_final = None
        self._venv_backup = None

    def _finalize_runtime(self) -> None:
        if self._venv_backup and self._venv_backup.exists():
            shutil.rmtree(self._venv_backup, ignore_errors=True)
        self._venv_backup = None
        self._venv_final = None
        self._launcher_backups.clear()

    def _cleanup_generated_artifacts(self, resolution: Resolution) -> None:
        for module in resolution.modules:
            root = self._repo_dir(module)
            for relative in _GENERATED_ARTIFACTS.get(module.id, ()):
                artifact = root / relative
                if artifact.is_symlink() or artifact.is_file():
                    artifact.unlink()
                elif artifact.is_dir():
                    shutil.rmtree(artifact)

    def _write_state(self, resolution: Resolution, launchers: list[Path]) -> None:
        payload = {
            "schema_version": 1,
            "installed_at": time.time(),
            "platform": self.platform.name,
            "requested_modules": list(resolution.requested),
            "resolved_modules": list(resolution.ids),
            "repositories": dict(sorted(self._resolved_revisions.items())),
            "with_ai_workers": self.options.with_ai_workers,
            "portable": self.options.portable,
            "launchers": [str(path) for path in launchers],
        }
        target = self.options.root / "installed-state.json"
        temporary = target.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temporary, target)

    def _state_launchers(self) -> list[str]:
        state = self.options.root / "installed-state.json"
        if not state.is_file():
            return []
        try:
            payload = json.loads(state.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        values = payload.get("launchers") or []
        return [str(value) for value in values if isinstance(value, str)]

    def _cleanup_staging(self) -> None:
        staging = self.options.root / ".staging"
        if not staging.exists():
            return
        try:
            for child in staging.iterdir():
                if child.name.startswith("venv-") or child.name == "toolbox-native":
                    if child.is_dir():
                        shutil.rmtree(child, ignore_errors=True)
                    else:
                        child.unlink(missing_ok=True)
            if not any(staging.iterdir()):
                staging.rmdir()
        except OSError:
            pass
