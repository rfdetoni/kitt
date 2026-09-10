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


@dataclass(frozen=True)
class InstallerOptions:
    root: Path
    bin_dir: Path
    force: bool = False
    ref: str | None = None
    with_ai_workers: bool = False
    portable: bool = False
    dry_run: bool = False
    start_services: bool = True


@dataclass(frozen=True)
class PrerequisiteReport:
    python: CommandInfo | None
    missing: tuple[str, ...]
    found: dict[str, str]


class EcosystemInstaller:
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

    def install(self, resolution: Resolution) -> None:
        if not resolution.modules:
            raise InstallerError("no modules selected")
        self._validate_platforms(resolution.modules)
        report = self._check_prerequisites(resolution.modules)
        self._python = report.python
        self._print_plan(resolution, report)
        if report.missing:
            hint = self.platform.prerequisite_hint(report.missing)
            detail = f"\nSuggested setup:\n{hint}" if hint else ""
            raise InstallerError(
                "missing or incompatible prerequisites: "
                + ", ".join(report.missing)
                + detail
            )
        if self.options.dry_run:
            print("\nDry run: no changes were made.")
            return

        root = self.options.root
        root.mkdir(parents=True, exist_ok=True)
        self.options.bin_dir.mkdir(parents=True, exist_ok=True)
        staging = root / ".staging"
        staging.mkdir(parents=True, exist_ok=True)

        try:
            for module in resolution.modules:
                self._sync_repository(module)

            self._build_native_components(resolution)
            self._build_assistant_ui(resolution)
            self._build_reverse_proxy(resolution)
            staged_venv = self._install_python_stack(resolution)
            self._smoke_test(resolution, staged_venv)
            venv = self._commit_python_stack(staged_venv)
            launchers = self._install_launchers(resolution, venv)
            self._write_state(resolution, launchers)
            self._start_services(resolution)
            self._finalize_runtime()
        except Exception:
            self._rollback_runtime()
            self._rollback_repositories()
            raise
        finally:
            self._cleanup_staging()

        path_ready = self.platform.ensure_user_path(self.options.bin_dir)
        print(f"\nK.I.T.T. ecosystem installed at {self.options.root}")
        print("Installed modules: " + ", ".join(module.name for module in resolution.modules))
        if not path_ready:
            print(f"Add {self.options.bin_dir} to PATH to use the installed commands globally.")
        if "agent-cli" in resolution.ids:
            print("Run: kitt")

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

        if any("rust" in value for value in missing):
            missing = [value for value in missing if not value.startswith("cargo") and not value.startswith("rustc")]
            if not any(value.startswith("rust") for value in missing):
                missing.append("rust>=1.85")
        return PrerequisiteReport(
            python=python,
            missing=tuple(dict.fromkeys(missing)),
            found=found,
        )

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
            ref = self.catalog.locked_ref(module, self.options.ref)
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

    @staticmethod
    def _has_blocking_toolbox_changes(status: str) -> bool:
        return any(line != "?? Cargo.lock" for line in status.splitlines())

    def _sync_repository(self, module: ModuleSpec) -> None:
        path = self._repo_dir(module)
        ref = self.catalog.locked_ref(module, self.options.ref)
        url = f"https://github.com/{module.repository}.git"
        print(f"\nSync {module.name} -> {ref}")
        if (path / ".git").is_dir():
            status = self._capture(["git", "status", "--porcelain"], cwd=path)
            dirty = (
                self._has_blocking_toolbox_changes(status)
                if module.strategy == "toolbox"
                else bool(status)
            )
            if dirty and not self.options.force:
                raise InstallerError(
                    f"{module.repository} has local changes at {path}; commit/stash them or use --force"
                )
            current = self._capture(["git", "rev-parse", "HEAD"], cwd=path)
            self._previous_revisions[path] = current
            if dirty and self.options.force:
                self._run(["git", "reset", "--hard", "HEAD"], cwd=path)
        else:
            if path.exists():
                shutil.rmtree(path)
            self._run(["git", "clone", "--filter=blob:none", "--no-checkout", url, str(path)])
            self._created_repos.append(path)

        self._run(["git", "-C", str(path), "remote", "set-url", "origin", url])
        self._run(["git", "-C", str(path), "fetch", "--force", "--depth", "1", "origin", ref])
        self._run(["git", "-C", str(path), "checkout", "--detach", "--force", "FETCH_HEAD"])
        self._run(["git", "-C", str(path), "clean", "-ffd"])
        actual = self._capture(["git", "rev-parse", "HEAD"], cwd=path)
        self._resolved_revisions[module.repository] = actual
        print(f"    resolved {actual[:12]}")

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

    def _cargo_build(self, path: Path) -> None:
        lock = path / "Cargo.lock"
        generated_lock = not lock.exists()
        command = ["cargo", "build", "--release"]
        if not generated_lock:
            command.append("--locked")
        try:
            self._run(command, cwd=path)
        finally:
            if generated_lock:
                lock.unlink(missing_ok=True)

    def _build_native_components(self, resolution: Resolution) -> None:
        if self.options.portable:
            return
        native_strategies = {"protocol", "rust", "toolbox", "assistant"}
        for module in resolution.modules:
            if module.strategy not in native_strategies:
                continue
            path = self._repo_dir(module)
            if not (path / "Cargo.toml").is_file():
                raise InstallerError(f"{module.repository} has no Cargo.toml for strategy {module.strategy}")
            print(f"\nBuild native {module.name}")
            self._cargo_build(path)

    def _build_assistant_ui(self, resolution: Resolution) -> None:
        if "assistant" not in resolution.ids:
            return
        assistant = self._repo_dir(self.catalog.modules["assistant"])
        hud = assistant / "apps" / "kitt-hud"
        if not hud.is_dir():
            return
        if self.platform.command_info("node") is None or self.platform.command_info("npm") is None:
            print("Assistant HUD skipped because Node/npm are unavailable.")
            return
        print("\nBuild KITT Assistant HUD")
        self._run(["npm", "ci", "--no-audit", "--no-fund"], cwd=hud)
        self._run(["npm", "run", "build"], cwd=hud)

    def _playwright_binary(self, proxy: Path) -> Path:
        base = proxy / "node_modules" / ".bin"
        return base / ("playwright.cmd" if self.platform.name == "windows" else "playwright")

    def _has_browser(self) -> bool:
        names = (
            "chrome", "msedge", "google-chrome", "google-chrome-stable",
            "chromium", "chromium-browser",
        )
        return any(shutil.which(name) for name in names)

    def _build_reverse_proxy(self, resolution: Resolution) -> None:
        if "reverse-proxy" not in resolution.ids:
            return
        proxy = self._repo_dir(self.catalog.modules["reverse-proxy"])
        print("\nBuild KITT Reverse Proxy")
        self._run(["npm", "ci", "--no-audit", "--no-fund"], cwd=proxy)
        self._run(["npm", "run", "build"], cwd=proxy)
        if not self._has_browser():
            playwright = self._playwright_binary(proxy)
            if not playwright.exists():
                raise InstallerError("Playwright binary missing after npm ci")
            self._run([str(playwright), "install", "chromium"], cwd=proxy)
        self._run(["npm", "prune", "--omit=dev", "--no-audit", "--no-fund"], cwd=proxy)

    def _venv_python(self, venv: Path) -> Path:
        if self.platform.name == "windows":
            return venv / "Scripts" / "python.exe"
        return venv / "bin" / "python"

    def _venv_executable(self, venv: Path, name: str) -> Path:
        if self.platform.name == "windows":
            exe = venv / "Scripts" / f"{name}.exe"
            if exe.exists():
                return exe
            return venv / "Scripts" / name
        return venv / "bin" / name

    def _needs_python_env(self, resolution: Resolution) -> bool:
        return bool({"agent-cli", "ai-workers", "toolbox"} & set(resolution.ids))

    def _install_python_stack(self, resolution: Resolution) -> Path | None:
        if not self._needs_python_env(resolution):
            return None
        if self._python is None:
            raise InstallerError("Python 3.12+ is required for the selected modules")

        root = self.options.root
        staging = root / ".staging" / f"venv-{os.getpid()}-{int(time.time())}"
        if staging.exists():
            shutil.rmtree(staging)
        print("\nBuild isolated Python runtime")
        self._run([*self._python.argv, "-m", "venv", str(staging)])
        python = self._venv_python(staging)
        self._run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "-U", "pip", "wheel"])

        selected = set(resolution.ids)
        if "protocol" in selected:
            protocol = self._repo_dir(self.catalog.modules["protocol"]) / "sdk" / "python"
            self._run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "--no-deps", str(protocol)])

        if "agent-cli" in selected:
            agent = self._repo_dir(self.catalog.modules["agent-cli"])
            self._run([
                str(python), "-m", "pip", "install", "--disable-pip-version-check",
                "prompt-toolkit>=3.0.52,<4",
            ])
            self._run([
                str(python), "-m", "pip", "install", "--disable-pip-version-check",
                "--no-deps", "--upgrade", "--force-reinstall", str(agent),
            ])

        if "assistant" in selected and "agent-cli" in selected:
            assistant_runtime = (
                self._repo_dir(self.catalog.modules["assistant"])
                / "packages" / "kitt-assistant-runtime"
            )
            self._run([
                str(python), "-m", "pip", "install", "--disable-pip-version-check",
                "--no-deps", "--upgrade", "--force-reinstall", str(assistant_runtime),
            ])

        if "ai-workers" in selected:
            workers = self._repo_dir(self.catalog.modules["ai-workers"])
            self._run([
                str(python), "-m", "pip", "install", "--disable-pip-version-check",
                "--no-deps", "--upgrade", "--force-reinstall", str(workers),
            ])
            if "agent-cli" in selected:
                for relative in ("packages/kitt-evolution", "packages/kitt-evals"):
                    self._run([
                        str(python), "-m", "pip", "install", "--disable-pip-version-check",
                        "--no-deps", "--upgrade", "--force-reinstall", str(workers / relative),
                    ])
            if self.options.with_ai_workers:
                self._run([
                    str(python), "-m", "pip", "install", "--disable-pip-version-check",
                    "faster-whisper>=1.0",
                ])

        if "toolbox" in selected and not self.options.portable:
            toolbox = self._repo_dir(self.catalog.modules["toolbox"])
            dist = root / ".staging" / "toolbox-native"
            if dist.exists():
                shutil.rmtree(dist)
            dist.mkdir(parents=True)
            self._run([
                str(python), "-m", "pip", "install", "--disable-pip-version-check",
                "maturin>=1.8,<2",
            ])
            build_script = toolbox / "packaging" / "build_native_release.py"
            self._run([str(python), str(build_script), "--out", str(dist)])
            wheels = sorted(dist.glob("*.whl"))
            if not wheels:
                raise InstallerError("kitt-toolbox native wheel was not produced")
            self._run([
                str(python), "-m", "pip", "install", "--disable-pip-version-check",
                "--no-deps", "--force-reinstall", str(wheels[0]),
            ])

        return staging

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

    def _install_launchers(self, resolution: Resolution, venv: Path | None) -> list[Path]:
        selected = set(resolution.ids)
        launchers: list[Path] = []
        if "agent-cli" in selected:
            if venv is None:
                raise InstallerError("Agent CLI selected but Python runtime was not created")
            kitt = self._venv_executable(venv, "kitt")
            if not kitt.exists():
                raise InstallerError(f"Agent CLI executable not found at {kitt}")
            launchers.append(self._write_launcher("kitt", [str(kitt)]))

        if "reverse-proxy" in selected:
            proxy = self._repo_dir(self.catalog.modules["reverse-proxy"])
            node = self.platform.command_info("node")
            if node is None:
                raise InstallerError("Node.js disappeared during installation")
            launchers.append(self._write_launcher(
                "kitt-reverse-proxy",
                [*node.argv, str(proxy / "dist" / "cli.js")],
            ))
            launchers.append(self._write_launcher(
                "kitt-agent-gateway",
                [*node.argv, str(proxy / "dist" / "gateway" / "cli.js")],
            ))

        if "assistant" in selected and not self.options.portable:
            assistant = self._repo_dir(self.catalog.modules["assistant"])
            release = assistant / "target" / "release"
            suffix = ".exe" if self.platform.name == "windows" else ""
            for name in ("kittctl", "kittd"):
                binary = release / f"{name}{suffix}"
                if binary.exists():
                    launchers.append(self._write_launcher(name, [str(binary)]))
        return launchers

    def _start_services(self, resolution: Resolution) -> None:
        if (
            not self.options.start_services
            or self.options.portable
            or "assistant" not in resolution.ids
        ):
            return
        assistant = self._repo_dir(self.catalog.modules["assistant"])
        suffix = ".exe" if self.platform.name == "windows" else ""
        kittctl = assistant / "target" / "release" / f"kittctl{suffix}"
        if not kittctl.exists():
            return
        print("\nInstall/start KITT Assistant service")
        self._run([str(kittctl), "service", "install"], check=False)
        self._run([str(kittctl), "service", "start"], check=False)

    def _smoke_test(self, resolution: Resolution, venv: Path | None) -> None:
        selected = set(resolution.ids)
        print("\nSmoke tests")
        if "agent-cli" in selected:
            if venv is None:
                raise InstallerError("Agent CLI runtime missing")
            self._run([str(self._venv_executable(venv, "kitt")), "--help"], quiet=True)
            python = self._venv_python(venv)
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
