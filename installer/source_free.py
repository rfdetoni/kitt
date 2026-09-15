from __future__ import annotations

import shutil
from pathlib import Path
from typing import Sequence

from .catalog import ModuleSpec, Resolution
from .core import EcosystemInstaller, InstallerError


class SourceFreeEcosystemInstaller(EcosystemInstaller):
    """Build components from temporary checkouts and retain runtime artifacts only."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._runtime_backups: dict[Path, Path | None] = {}
        self._managed_legacy_sources: set[str] = set()

    def _repo_dir(self, module: ModuleSpec) -> Path:
        name = module.repository.split("/", 1)[1]
        return self.options.root / ".staging" / "sources" / name

    def _sync_repository(self, module: ModuleSpec) -> None:
        self._managed_legacy_sources.add(module.repository.split("/", 1)[1])
        path = self._repo_dir(module)
        if path.exists():
            shutil.rmtree(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        super()._sync_repository(module)

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
        release = source / "target" / "release"
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
                if backup is not None and backup.exists():
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
