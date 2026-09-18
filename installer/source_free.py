from __future__ import annotations

import os
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Sequence, TypeVar

from .catalog import ModuleSpec, Resolution
from .core import EcosystemInstaller, InstallerError


T = TypeVar("T")


class SourceFreeEcosystemInstaller(EcosystemInstaller):
    """Build components from temporary checkouts and retain runtime artifacts only."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._runtime_backups: dict[Path, Path | None] = {}
        self._managed_legacy_sources: set[str] = set()
        self._state_lock = threading.Lock()
        self._jobs = self._resolve_jobs()
        self._native_build_slots = 1

    @staticmethod
    def _resolve_jobs() -> int:
        raw = os.environ.get("KITT_INSTALL_JOBS", "").strip()
        if raw:
            try:
                value = int(raw)
            except ValueError as exc:
                raise InstallerError("KITT_INSTALL_JOBS must be a positive integer") from exc
            if value <= 0:
                raise InstallerError("KITT_INSTALL_JOBS must be a positive integer")
            return min(value, 32)
        return max(1, min(os.cpu_count() or 1, 16))

    def _io_workers(self, count: int) -> int:
        return min(count, max(2, min(8, self._jobs * 2)))

    def _phase_workers(self, count: int) -> int:
        return min(count, max(2, min(4, self._jobs)))

    def _cargo_jobs(self) -> int:
        return max(1, self._jobs // max(1, self._native_build_slots))

    def _build_cache_dir(self) -> Path:
        path = self.options.root / ".cache" / "build"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _cargo_target_dir(self, name: str) -> Path:
        path = self._build_cache_dir() / "cargo" / name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _cargo_env(self, name: str) -> dict[str, str]:
        env = os.environ.copy()
        env["CARGO_TARGET_DIR"] = str(self._cargo_target_dir(name))
        env["CARGO_BUILD_JOBS"] = str(self._cargo_jobs())
        env.setdefault("CARGO_INCREMENTAL", "1")
        env.setdefault("CARGO_NET_RETRY", "3")
        return env

    def _npm_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.setdefault("npm_config_prefer_offline", "true")
        env.setdefault("npm_config_audit", "false")
        env.setdefault("npm_config_fund", "false")
        env.setdefault("npm_config_progress", "false")
        env.setdefault("npm_config_maxsockets", str(max(16, min(64, self._jobs * 4))))
        return env

    def _timed(self, label: str, action: Callable[[], T]) -> T:
        started = time.monotonic()
        result = action()
        print(f"    completed {label} in {time.monotonic() - started:.2f}s")
        return result

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
        (root / ".staging").mkdir(parents=True, exist_ok=True)

        selected = set(resolution.ids)
        self._native_build_slots = 2 if {"assistant", "toolbox"} <= selected and not self.options.portable else 1

        try:
            self._sync_repositories_parallel(resolution)
            staged_venv = self._build_install_artifacts_parallel(resolution)
            self._smoke_test(resolution, staged_venv)
            venv = self._commit_python_stack(staged_venv)
            launchers = self._install_launchers(resolution, venv)
            self._write_state(resolution, launchers)
            self._start_services(resolution)
            self._cleanup_generated_artifacts(resolution)
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

    def _repo_dir(self, module: ModuleSpec) -> Path:
        name = module.repository.split("/", 1)[1]
        return self.options.root / ".staging" / "sources" / name

    def _sync_repository(self, module: ModuleSpec) -> None:
        name = module.repository.split("/", 1)[1]
        path = self._repo_dir(module)
        ref = self.catalog.locked_ref(module, self.options.ref)
        url = f"https://github.com/{module.repository}.git"
        with self._state_lock:
            self._managed_legacy_sources.add(name)
        if path.exists():
            shutil.rmtree(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\nSync {module.name} -> {ref}")
        self._run(["git", "init", "--quiet", str(path)])
        self._run(["git", "-C", str(path), "remote", "add", "origin", url])
        self._run([
            "git", "-C", str(path), "fetch", "--force", "--depth", "1", "origin", ref,
        ])
        self._run(["git", "-C", str(path), "checkout", "--detach", "--force", "FETCH_HEAD"])
        self._run(["git", "-C", str(path), "clean", "-ffd"])
        actual = self._capture(["git", "rev-parse", "HEAD"], cwd=path)
        with self._state_lock:
            self._resolved_revisions[module.repository] = actual
        print(f"    resolved {actual[:12]}")

    def _sync_repositories_parallel(self, resolution: Resolution) -> None:
        modules = tuple(resolution.modules)
        workers = self._io_workers(len(modules))
        if workers <= 1:
            for module in modules:
                self._sync_repository(module)
            return
        print(f"\nSync repositories in parallel ({workers} workers)")
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="kitt-sync") as pool:
            futures = {pool.submit(self._sync_repository, module): module for module in modules}
            for future in as_completed(futures):
                future.result()

    def _build_install_artifacts_parallel(self, resolution: Resolution) -> Path | None:
        selected = set(resolution.ids)
        tasks: list[tuple[str, Callable[[], object]]] = []
        if "assistant" in selected and not self.options.portable:
            tasks.append(("KITT Assistant native", lambda: self._build_native_components(resolution)))
        if "assistant" in selected:
            tasks.append(("KITT Assistant HUD", lambda: self._build_assistant_ui(resolution)))
        if "reverse-proxy" in selected:
            tasks.append(("KITT Reverse Proxy", lambda: self._build_reverse_proxy(resolution)))
        if self._needs_python_env(resolution):
            tasks.append(("Python runtime", lambda: self._install_python_stack(resolution)))

        if not tasks:
            return None

        print(f"\nBuild/install artifacts in parallel ({self._phase_workers(len(tasks))} workers)")
        staged_venv: Path | None = None
        workers = self._phase_workers(len(tasks))
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="kitt-build") as pool:
            futures = {
                pool.submit(self._timed, label, action): label
                for label, action in tasks
            }
            for future in as_completed(futures):
                label = futures[future]
                result = future.result()
                if label == "Python runtime":
                    staged_venv = result if isinstance(result, Path) else None
        return staged_venv

    def _cargo_build_cached(self, module: ModuleSpec) -> None:
        path = self._repo_dir(module)
        if not (path / "Cargo.toml").is_file():
            raise InstallerError(f"{module.repository} has no Cargo.toml for strategy {module.strategy}")
        lock = path / "Cargo.lock"
        generated_lock = not lock.exists()
        command = ["cargo", "build", "--release", "--jobs", str(self._cargo_jobs())]
        if not generated_lock:
            command.append("--locked")
        try:
            self._run(command, cwd=path, env=self._cargo_env(module.id))
        finally:
            if generated_lock:
                lock.unlink(missing_ok=True)

    def _build_native_components(self, resolution: Resolution) -> None:
        if self.options.portable or "assistant" not in resolution.ids:
            return
        module = self.catalog.modules["assistant"]
        print("\nBuild native KITT Assistant")
        self._cargo_build_cached(module)

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
        env = self._npm_env()
        self._run(["npm", "ci", "--no-audit", "--no-fund", "--prefer-offline"], cwd=hud, env=env)
        self._run(["npm", "run", "build"], cwd=hud, env=env)

    def _build_reverse_proxy(self, resolution: Resolution) -> None:
        if "reverse-proxy" not in resolution.ids:
            return
        proxy = self._repo_dir(self.catalog.modules["reverse-proxy"])
        print("\nBuild KITT Reverse Proxy")
        env = self._npm_env()
        self._run(["npm", "ci", "--no-audit", "--no-fund", "--prefer-offline"], cwd=proxy, env=env)
        self._run(["npm", "run", "build"], cwd=proxy, env=env)
        if not self._has_browser():
            playwright = self._playwright_binary(proxy)
            if not playwright.exists():
                raise InstallerError("Playwright binary missing after npm ci")
            self._run([str(playwright), "install", "chromium"], cwd=proxy, env=env)
        self._run([
            "npm", "prune", "--omit=dev", "--no-audit", "--no-fund", "--prefer-offline",
        ], cwd=proxy, env=env)

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
        selected = set(resolution.ids)

        bootstrap = ["setuptools>=68", "wheel"]
        if "toolbox" in selected and not self.options.portable:
            bootstrap.append("maturin>=1.8,<2")
        if "ai-workers" in selected and self.options.with_ai_workers:
            bootstrap.append("faster-whisper>=1.0")
        self._run([
            str(python), "-m", "pip", "install", "--disable-pip-version-check",
            "--prefer-binary", *bootstrap,
        ])

        local_packages: list[Path] = []
        agent_package: Path | None = None
        if "protocol" in selected:
            local_packages.append(
                self._repo_dir(self.catalog.modules["protocol"]) / "sdk" / "python"
            )
        if "agent-cli" in selected:
            agent_package = self._repo_dir(self.catalog.modules["agent-cli"])
            local_packages.append(agent_package)
        if "assistant" in selected and "agent-cli" in selected:
            local_packages.append(
                self._repo_dir(self.catalog.modules["assistant"])
                / "packages" / "kitt-assistant-runtime"
            )
        if "ai-workers" in selected:
            workers = self._repo_dir(self.catalog.modules["ai-workers"])
            local_packages.append(workers)
            if "agent-cli" in selected:
                local_packages.extend([
                    workers / "packages" / "kitt-evolution",
                    workers / "packages" / "kitt-evals",
                ])

        if local_packages:
            # Resolve declared runtime dependencies from each package's own
            # pyproject metadata. This prevents installer dependency drift when a
            # component adds a new mandatory dependency.
            for package in local_packages:
                self._run([
                    str(python), "-m", "pip", "install", "--disable-pip-version-check",
                    "--prefer-binary", "--no-build-isolation", str(package),
                ])

            # Re-apply selected KITT packages without dependency resolution
            # so the requested main/locked checkouts are authoritative even when
            # one package declares another KITT repository through a direct URL.
            #
            # Install the Agent on its own and last. Multiple KITT distributions
            # intentionally share the kitt namespace, so a single multi-wheel
            # reinstall must not leave Agent-owned modules from an older install
            # order in site-packages.
            non_agent_packages = [
                package for package in local_packages if package != agent_package
            ]
            if non_agent_packages:
                self._run([
                    str(python), "-m", "pip", "install", "--disable-pip-version-check",
                    "--no-deps", "--no-build-isolation", "--upgrade", "--force-reinstall",
                    *map(str, non_agent_packages),
                ])
            if agent_package is not None:
                self._run([
                    str(python), "-m", "pip", "install", "--disable-pip-version-check",
                    "--no-deps", "--no-build-isolation", "--upgrade", "--force-reinstall",
                    str(agent_package),
                ])

        if "toolbox" in selected and not self.options.portable:
            toolbox = self._repo_dir(self.catalog.modules["toolbox"])
            dist = root / ".staging" / "toolbox-native"
            if dist.exists():
                shutil.rmtree(dist)
            dist.mkdir(parents=True)
            build_script = toolbox / "packaging" / "build_native_release.py"
            self._run(
                [str(python), str(build_script), "--out", str(dist)],
                env=self._cargo_env("toolbox"),
            )
            wheels = sorted(dist.glob("*.whl"))
            if not wheels:
                raise InstallerError("kitt-toolbox native wheel was not produced")
            self._run([
                str(python), "-m", "pip", "install", "--disable-pip-version-check",
                "--no-deps", str(wheels[0]),
            ])

        return staging

    def _runtime_component_dir(self, name: str) -> Path:
        return self.options.root / "runtime" / name

    def _staged_runtime_component_dir(self, name: str) -> Path:
        return self.options.root / ".staging" / "runtime-next" / name

    def _swap_runtime_component(self, name: str, staged: Path) -> Path:
        final = self._runtime_component_dir(name)
        backup = self.options.root / ".staging" / "runtime-previous" / name
        if backup.exists():
            shutil.rmtree(backup)
        backup.parent.mkdir(parents=True, exist_ok=True)
        final.parent.mkdir(parents=True, exist_ok=True)

        previous: Path | None = None
        if final.exists():
            final.rename(backup)
            previous = backup

        try:
            staged.rename(final)
        except Exception:
            if previous is not None and previous.exists() and not final.exists():
                previous.rename(final)
            raise

        self._runtime_backups[final] = previous
        return final

    def _prepare_reverse_proxy_runtime(self) -> Path:
        source = self._repo_dir(self.catalog.modules["reverse-proxy"])
        staged = self._staged_runtime_component_dir("reverse-proxy")
        if staged.exists():
            shutil.rmtree(staged)
        staged.mkdir(parents=True, exist_ok=True)

        for relative in ("dist", "node_modules"):
            source_dir = source / relative
            if not source_dir.is_dir():
                raise InstallerError(
                    f"reverse-proxy runtime artifact missing after build: {source_dir}"
                )
            shutil.copytree(source_dir, staged / relative, symlinks=True)

        for relative in ("package.json", "package-lock.json"):
            source_file = source / relative
            if source_file.is_file():
                shutil.copy2(source_file, staged / relative)

        return self._swap_runtime_component("reverse-proxy", staged)

    def _prepare_assistant_runtime(self) -> Path:
        source = self._repo_dir(self.catalog.modules["assistant"])
        release = self._cargo_target_dir("assistant") / "release"
        staged = self._staged_runtime_component_dir("assistant")
        if staged.exists():
            shutil.rmtree(staged)
        binary_dir = staged / "bin"
        binary_dir.mkdir(parents=True, exist_ok=True)

        suffix = ".exe" if self.platform.name == "windows" else ""
        for name in ("kittctl", "kittd"):
            source_binary = release / f"{name}{suffix}"
            if not source_binary.is_file():
                raise InstallerError(
                    f"assistant runtime artifact missing after build: {source_binary}"
                )
            shutil.copy2(source_binary, binary_dir / source_binary.name)

        hud = source / "apps" / "kitt-hud" / "dist"
        if hud.is_dir():
            shutil.copytree(hud, staged / "hud")

        return self._swap_runtime_component("assistant", staged)

    def _write_runtime_launcher(self, name: str, argv: Sequence[str]) -> Path:
        return self._write_launcher(name, argv)

    def _install_launchers(self, resolution: Resolution, venv: Path | None) -> list[Path]:
        selected = set(resolution.ids)
        launchers: list[Path] = []

        if "agent-cli" in selected:
            if venv is None:
                raise InstallerError("Agent CLI selected but Python runtime was not created")
            python = self._venv_python(venv)
            if not python.exists():
                raise InstallerError(f"Agent CLI Python runtime not found at {python}")
            launchers.append(
                self._write_runtime_launcher("kitt", [str(python), "-m", "kitt.cli.main"])
            )

        if "reverse-proxy" in selected:
            proxy = self._prepare_reverse_proxy_runtime()
            node = self.platform.command_info("node")
            if node is None:
                raise InstallerError("Node.js disappeared during installation")
            self._run([*node.argv, str(proxy / "dist" / "cli.js"), "--help"], quiet=True)
            launchers.append(
                self._write_runtime_launcher(
                    "kitt-reverse-proxy",
                    [*node.argv, str(proxy / "dist" / "cli.js")],
                )
            )
            launchers.append(
                self._write_runtime_launcher(
                    "kitt-agent-gateway",
                    [*node.argv, str(proxy / "dist" / "gateway" / "cli.js")],
                )
            )

        if "assistant" in selected and not self.options.portable:
            assistant = self._prepare_assistant_runtime()
            suffix = ".exe" if self.platform.name == "windows" else ""
            for name in ("kittctl", "kittd"):
                binary = assistant / "bin" / f"{name}{suffix}"
                launchers.append(self._write_runtime_launcher(name, [str(binary)]))

        return launchers

    def _start_services(self, resolution: Resolution) -> None:
        if (
            not self.options.start_services
            or self.options.portable
            or "assistant" not in resolution.ids
        ):
            return
        suffix = ".exe" if self.platform.name == "windows" else ""
        kittctl = self._runtime_component_dir("assistant") / "bin" / f"kittctl{suffix}"
        if not kittctl.exists():
            return
        print("\nInstall/start KITT Assistant service")
        self._run([str(kittctl), "service", "install"], check=False)
        self._run([str(kittctl), "service", "start"], check=False)

    def _rollback_runtime(self) -> None:
        super()._rollback_runtime()
        for final, backup in reversed(list(self._runtime_backups.items())):
            try:
                if final.exists():
                    shutil.rmtree(final)
                if backup is not None and backup.exists() and not final.exists():
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    backup.rename(final)
            except OSError:
                pass
        self._runtime_backups.clear()

    def _remove_legacy_source_checkouts(self) -> None:
        for name in sorted(self._managed_legacy_sources):
            legacy = self.options.root / name
            if legacy == self.options.root or not (legacy / ".git").is_dir():
                continue
            try:
                shutil.rmtree(legacy)
                print(f"Removed legacy source checkout: {legacy}")
            except OSError as exc:
                print(f"Warning: could not remove legacy source checkout {legacy}: {exc}")

    def _finalize_runtime(self) -> None:
        self._remove_legacy_source_checkouts()
        for backup in self._runtime_backups.values():
            if backup is not None and backup.exists():
                shutil.rmtree(backup, ignore_errors=True)
        self._runtime_backups.clear()
        super()._finalize_runtime()

    def _cleanup_staging(self) -> None:
        staging = self.options.root / ".staging"
        for name in ("sources", "runtime-next", "runtime-previous"):
            path = staging / name
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
        super()._cleanup_staging()
