from __future__ import annotations

import os
import re
import signal
import shutil
import platform as stdlib_platform
import urllib.request
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class CommandInfo:
    argv: tuple[str, ...]
    version: tuple[int, ...]
    version_text: str


def _version_tuple(text: str) -> tuple[int, ...]:
    match = re.search(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", text)
    if not match:
        return ()
    return tuple(int(v) for v in match.groups(default="0"))


def _run_capture(argv: Sequence[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            list(argv),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return 127, ""
    return proc.returncode, (proc.stdout or "").strip()


class PlatformAdapter:
    """Small OS seam. All install orchestration stays platform-independent."""

    _KNOWN_LAUNCHERS = (
        "kitt",
        "kittctl",
        "kittd",
        "kitt-reverse-proxy",
        "kitt-agent-gateway",
    )

    def __init__(self, name: str, *, posix: bool):
        self.name = name
        self.posix = posix
        self._python_without_venv: CommandInfo | None = None

    @classmethod
    def detect(cls) -> "PlatformAdapter":
        platform = sys.platform.lower()
        if os.name == "nt" or platform.startswith("win"):
            return cls("windows", posix=False)
        if platform == "darwin":
            return cls("macos", posix=True)
        if platform.startswith("linux"):
            return cls("linux", posix=True)
        if platform.startswith("haiku"):
            return cls("haiku", posix=True)
        return cls("posix" if os.name == "posix" else platform, posix=os.name == "posix")

    def supports(self, platforms: Iterable[str]) -> bool:
        values = set(platforms)
        return self.name in values or (self.posix and "posix" in values)

    def default_root(self) -> Path:
        configured = os.environ.get("KITT_HOME")
        if configured:
            return Path(configured).expanduser()
        if self.name == "windows":
            base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
            return Path(base) / "KITT"
        if self.name == "macos":
            return Path.home() / "Library" / "Application Support" / "KITT"
        base = os.environ.get("XDG_DATA_HOME")
        return (Path(base).expanduser() if base else Path.home() / ".local" / "share") / "kitt"

    def default_bin_dir(self) -> Path:
        configured = os.environ.get("KITT_BIN_DIR")
        if configured:
            return Path(configured).expanduser()
        if self.name == "windows":
            base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
            return Path(base) / "KITT" / "bin"
        base = os.environ.get("XDG_BIN_HOME")
        return Path(base).expanduser() if base else Path.home() / ".local" / "bin"

    def _python_candidates(self) -> list[tuple[str, ...]]:
        candidates: list[tuple[str, ...]] = []
        if self.name == "windows" and shutil.which("py"):
            for minor in (14, 13, 12, 11, 10):
                candidates.append(("py", f"-3.{minor}"))
        for name in ("python3.14", "python3.13", "python3.12", "python3", "python"):
            executable = shutil.which(name)
            if executable:
                candidates.append((executable,))
        current = Path(sys.executable)
        if current.exists():
            candidates.insert(0, (str(current),))
        return candidates

    def _python_supports_venv(self, candidate: tuple[str, ...]) -> bool:
        """Prove that Python can create a pip-enabled venv before expensive builds."""
        code, _ = _run_capture((*candidate, "-c", "import ensurepip, venv"))
        if code != 0:
            return False
        try:
            with tempfile.TemporaryDirectory(prefix="kitt-venv-probe-") as temp:
                target = Path(temp) / "venv"
                code, _ = _run_capture((*candidate, "-m", "venv", str(target)))
                if code != 0:
                    return False
                python = (
                    target / "Scripts" / "python.exe"
                    if self.name == "windows"
                    else target / "bin" / "python"
                )
                code, _ = _run_capture((str(python), "-m", "pip", "--version"))
                return code == 0
        except OSError:
            return False

    def find_python(
        self,
        minimum: tuple[int, int] = (3, 12),
        *,
        require_venv: bool = True,
    ) -> CommandInfo | None:
        self._python_without_venv = None
        seen: set[tuple[str, ...]] = set()
        for candidate in self._python_candidates():
            if candidate in seen:
                continue
            seen.add(candidate)
            code, output = _run_capture(
                (*candidate, "-c", "import sys;print('.'.join(map(str,sys.version_info[:3])))")
            )
            if code != 0:
                continue
            version = _version_tuple(output)
            if version[:2] < minimum:
                continue
            info = CommandInfo(candidate, version, output)
            if require_venv and not self._python_supports_venv(candidate):
                if self._python_without_venv is None or version > self._python_without_venv.version:
                    self._python_without_venv = info
                continue
            return info
        return None

    def command_info(self, name: str) -> CommandInfo | None:
        if name == "python":
            return self.find_python((3, 12))
        executable = shutil.which(name)
        if not executable:
            return None
        version_args = {
            "git": ("--version",),
            "node": ("--version",),
            "npm": ("--version",),
            "cargo": ("--version",),
            "rustc": ("--version",),
        }.get(name, ("--version",))
        code, output = _run_capture((executable, *version_args))
        if code != 0:
            return None
        return CommandInfo((executable,), _version_tuple(output), output)

    def _python_venv_hint(self) -> str:
        info = self._python_without_venv
        version = info.version[:2] if info else ()
        version_text = ".".join(map(str, version)) if version else "3.12+"
        if self.name == "linux":
            package = f"python{version_text}-venv" if version else "python3-venv"
            return (
                f"Python {version_text} was found but cannot create pip-enabled virtual environments.\n"
                f"Debian/Ubuntu: sudo apt install {package}\n"
                "Other distributions: install the package that provides Python venv/ensurepip."
            )
        if self.name == "macos":
            return (
                f"Python {version_text} was found without a working venv/ensurepip. "
                "Install/reinstall Python with Homebrew: brew install python@3.12"
            )
        if self.name == "windows":
            return (
                f"Python {version_text} was found without a working venv/ensurepip. "
                "Repair/reinstall Python and include pip/venv support."
            )
        if self.name == "haiku":
            return (
                f"Python {version_text} was found without a working venv/ensurepip. "
                "Install the Haiku package that provides Python venv/pip support."
            )
        return f"Python {version_text} was found but venv/ensurepip is unavailable."

    def _rustup_target(self) -> str:
        machine = stdlib_platform.machine().strip().lower()
        arch = {
            "amd64": "x86_64",
            "x86_64": "x86_64",
            "arm64": "aarch64",
            "aarch64": "aarch64",
        }.get(machine)
        if arch is None:
            raise RuntimeError(f"automatic Rust bootstrap does not support architecture {machine!r}")
        suffix = {
            "windows": "pc-windows-msvc",
            "linux": "unknown-linux-gnu",
            "macos": "apple-darwin",
        }.get(self.name)
        if suffix is None:
            raise RuntimeError(
                f"automatic Rust bootstrap is not available on platform {self.name!r}"
            )
        return f"{arch}-{suffix}"

    def _prepend_process_path(self, path: Path) -> None:
        current = [part for part in os.environ.get("PATH", "").split(os.pathsep) if part]
        current = [part for part in current if not self._same_path(part, path)]
        os.environ["PATH"] = os.pathsep.join([str(path), *current])

    def install_rust(self, minimum: tuple[int, ...]) -> CommandInfo:
        """Install a user-local stable Rust toolchain through official rustup-init."""
        target = self._rustup_target()
        suffix = ".exe" if self.name == "windows" else ""
        url = f"https://static.rust-lang.org/rustup/dist/{target}/rustup-init{suffix}"
        cargo_home = Path(os.environ.get("CARGO_HOME") or (Path.home() / ".cargo")).expanduser()
        cargo_bin = cargo_home / "bin"
        cargo_bin.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="kitt-rustup-") as temp:
            installer = Path(temp) / f"rustup-init{suffix}"
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "kitt-installer-rust-bootstrap"},
            )
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    data = response.read(64 * 1024 * 1024 + 1)
            except Exception as exc:
                raise RuntimeError(f"could not download rustup-init from {url}: {exc}") from exc
            if not data or len(data) > 64 * 1024 * 1024:
                raise RuntimeError("downloaded rustup-init is empty or exceeds the safety limit")
            installer.write_bytes(data)
            if self.posix:
                installer.chmod(0o700)

            env = os.environ.copy()
            env["CARGO_HOME"] = str(cargo_home)
            command = [
                str(installer),
                "-y",
                "--profile",
                "minimal",
                "--default-toolchain",
                "stable",
            ]
            try:
                proc = subprocess.run(
                    command,
                    env=env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=300,
                    check=False,
                )
            except (OSError, subprocess.SubprocessError) as exc:
                raise RuntimeError(f"rustup-init could not be executed: {exc}") from exc
            if proc.returncode != 0:
                output = (proc.stdout or "").strip()
                raise RuntimeError(
                    f"rustup-init failed with exit code {proc.returncode}"
                    + (f": {output}" if output else "")
                )

        self._prepend_process_path(cargo_bin)
        cargo = self.command_info("cargo")
        rustc = self.command_info("rustc")
        if cargo is None or rustc is None:
            raise RuntimeError("rustup completed but cargo/rustc are still unavailable")
        if minimum:
            if (cargo.version and cargo.version < minimum) or (rustc.version and rustc.version < minimum):
                wanted = ".".join(map(str, minimum))
                raise RuntimeError(
                    f"rustup installed an incompatible toolchain; Rust >={wanted} is required"
                )
        return rustc

    @staticmethod
    def _first_existing_command(*candidates: str | Path | None) -> str | None:
        for candidate in candidates:
            if not candidate:
                continue
            path = Path(candidate)
            if path.is_file():
                return str(path)
        return None

    def stop_kitt_services(self, root: Path, bin_dir: Path) -> None:
        """Stop resident K.I.T.T. processes before replacing runtime artifacts.

        Best-effort service-manager shutdown is followed by a narrowly-scoped
        process cleanup. Interactive Agent clients are intentionally excluded.
        """
        suffix = ".exe" if self.name == "windows" else ""
        launcher_suffix = ".cmd" if self.name == "windows" else ""

        kittctl = self._first_existing_command(
            root / "runtime" / "assistant" / "bin" / f"kittctl{suffix}",
            bin_dir / f"kittctl{launcher_suffix}",
            shutil.which("kittctl"),
        )
        if kittctl:
            _run_capture((kittctl, "service", "stop"))

        kitt = self._first_existing_command(
            bin_dir / f"kitt{launcher_suffix}",
            shutil.which("kitt"),
        )
        if kitt:
            _run_capture((kitt, "daemon", "stop"))

        if self.name == "windows":
            powershell = shutil.which("powershell") or shutil.which("pwsh")
            if not powershell:
                return
            script = (
                "$ErrorActionPreference='SilentlyContinue';"
                "$tasks=@('KITT Daemon','KITT Assistant','KITT Reverse Proxy','KITT Agent Gateway');"
                "foreach($name in $tasks){"
                "$task=Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue;"
                "if($task){Stop-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue}};"
                "Get-Service -ErrorAction SilentlyContinue | "
                "Where-Object {$_.Name -match '(?i)^kitt' -or $_.DisplayName -match '(?i)^K\\.I\\.T\\.T\\.|^KITT'} | "
                "ForEach-Object {Stop-Service -Name $_.Name -Force -ErrorAction SilentlyContinue};"
                "$pattern='(?i)(kittd(?:\\.exe)?|kitt\\.cli\\.main.+daemon\\s+run|"
                "kitt-reverse-proxy(?:\\.cmd|\\.exe)?|kitt-agent-gateway(?:\\.cmd|\\.exe)?|"
                "kitt-reverse-proxy[\\\\/].*dist[\\\\/](?:gateway[\\\\/])?cli\\.js)';"
                f"$self={os.getpid()};"
                "Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | "
                "Where-Object {$_.ProcessId -ne $self -and $_.CommandLine -and $_.CommandLine -match $pattern} | "
                "ForEach-Object {Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue}"
            )
            _run_capture((powershell, "-NoProfile", "-NonInteractive", "-Command", script))
            return

        systemctl = shutil.which("systemctl")
        if systemctl:
            _run_capture((
                systemctl,
                "--user",
                "stop",
                "kitt-daemon.service",
                "kitt-assistant.service",
                "kitt-reverse-proxy.service",
                "kitt-agent-gateway.service",
            ))

        launchctl = shutil.which("launchctl")
        if launchctl:
            for label in (
                "com.kitt.daemon",
                "com.kitt.assistant",
                "com.kitt.reverse-proxy",
                "com.kitt.agent-gateway",
            ):
                _run_capture((launchctl, "stop", label))

        pgrep = shutil.which("pgrep")
        if not pgrep or not hasattr(os, "getuid"):
            return
        pattern = (
            r"(kittd([[:space:]]|$)|kitt[.]cli[.]main.*daemon[[:space:]]+run|"
            r"kitt-reverse-proxy([[:space:]]|$)|kitt-agent-gateway([[:space:]]|$)|"
            r"kitt-reverse-proxy/.*/dist/(gateway/)?cli[.]js)"
        )
        code, output = _run_capture((pgrep, "-u", str(os.getuid()), "-f", pattern))
        if code not in {0, 1}:
            return

        protected = {os.getpid(), os.getppid()}
        pids = [
            int(value)
            for value in output.split()
            if value.isdigit() and int(value) not in protected
        ]
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                pass

        deadline = time.monotonic() + 3.0
        alive = set(pids)
        while alive and time.monotonic() < deadline:
            for pid in tuple(alive):
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    alive.discard(pid)
                except PermissionError:
                    alive.discard(pid)
            if alive:
                time.sleep(0.1)

        for pid in alive:
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass

    def assistant_voice_build_available(self) -> bool:
        """Return whether the host can compile the resident microphone stack."""
        if self.name != "linux":
            return True
        executable = shutil.which("pkg-config")
        if not executable:
            return False
        code, _ = _run_capture((executable, "--exists", "alsa"))
        return code == 0

    def prerequisite_hint(self, missing: Iterable[str]) -> str:
        missing_set = set(missing)
        hints: list[str] = []
        if "python" in missing_set and self._python_without_venv is not None:
            hints.append(self._python_venv_hint())
            missing_set.remove("python")

        if self.name == "windows":
            commands = []
            if "git" in missing_set:
                commands.append("winget install --id Git.Git -e")
            if "python" in missing_set:
                commands.append("winget install --id Python.Python.3.12 -e")
            if {"node", "npm"} & missing_set:
                commands.append("winget install --id OpenJS.NodeJS.LTS -e")
            if {"rust", "cargo", "rustc"} & missing_set:
                commands.append("winget install --id Rustlang.Rustup -e")
            if commands:
                hints.append("\n".join(commands))
            return "\n".join(hints)
        if self.name == "macos":
            packages = []
            if "git" in missing_set:
                packages.append("git")
            if "python" in missing_set:
                packages.append("python@3.12")
            if {"node", "npm"} & missing_set:
                packages.append("node")
            hint = f"brew install {' '.join(dict.fromkeys(packages))}" if packages else ""
            if hint:
                hints.append(hint)
            if {"rust", "cargo", "rustc"} & missing_set:
                hints.append("Install Rust with rustup: https://rustup.rs")
            return "\n".join(hints)
        if self.name == "haiku":
            packages = []
            if "git" in missing_set:
                packages.append("git")
            if "python" in missing_set:
                packages.append("python3")
            if {"node", "npm"} & missing_set:
                packages.append("nodejs")
            if {"rust", "cargo", "rustc"} & missing_set:
                packages.append("rust")
            if packages:
                hints.append(f"pkgman install {' '.join(dict.fromkeys(packages))}")
            return "\n".join(hints)
        if missing_set:
            hints.append(
                "Install the missing prerequisites with your distribution package manager: "
                + ", ".join(sorted(missing_set))
            )
        return "\n".join(hints)

    @staticmethod
    def _same_path(left: str | Path, right: str | Path) -> bool:
        left_path = os.path.normcase(
            os.path.realpath(os.path.abspath(os.path.expanduser(str(left))))
        )
        right_path = os.path.normcase(
            os.path.realpath(os.path.abspath(os.path.expanduser(str(right))))
        )
        return left_path == right_path

    def _launcher_path(self, bin_dir: Path, name: str) -> Path:
        suffix = ".cmd" if self.name == "windows" else ""
        return bin_dir / f"{name}{suffix}"

    def launcher_shadow_conflicts(self, bin_dir: Path) -> dict[str, str]:
        """Return installed K.I.T.T. launchers shadowed by another PATH entry."""
        conflicts: dict[str, str] = {}
        for name in self._KNOWN_LAUNCHERS:
            expected = self._launcher_path(bin_dir, name)
            if not expected.exists():
                continue
            active = shutil.which(name)
            if active and not self._same_path(active, expected):
                conflicts[name] = active
        return conflicts

    def ensure_user_path(self, bin_dir: Path) -> bool:
        """Persist PATH on Windows and verify installed launchers are not shadowed."""
        if self.name != "windows":
            in_path = any(
                self._same_path(part, bin_dir)
                for part in os.environ.get("PATH", "").split(os.pathsep)
                if part
            )
            return in_path and not self.launcher_shadow_conflicts(bin_dir)
        try:
            import winreg  # type: ignore

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "Environment",
                0,
                winreg.KEY_READ | winreg.KEY_WRITE,
            ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, "Path")
                except FileNotFoundError:
                    value = ""
                parts = [part for part in str(value).split(";") if part]
                reordered = [
                    part
                    for part in parts
                    if not self._same_path(part, bin_dir)
                ]
                reordered.insert(0, str(bin_dir))
                if reordered != parts:
                    winreg.SetValueEx(
                        key,
                        "Path",
                        0,
                        winreg.REG_EXPAND_SZ,
                        ";".join(reordered),
                    )
            current_parts = [
                part
                for part in os.environ.get("PATH", "").split(os.pathsep)
                if part and not self._same_path(part, bin_dir)
            ]
            os.environ["PATH"] = os.pathsep.join([str(bin_dir), *current_parts])
            return not self.launcher_shadow_conflicts(bin_dir)
        except Exception:
            return False

    @staticmethod
    def _atomic_write_text(
        path: Path,
        content: str,
        *,
        encoding: str,
        mode: int | None = None,
    ) -> None:
        """Replace a launcher atomically so reinstalls never leave a partial executable."""
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding=encoding, newline="") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            if mode is not None:
                temp_path.chmod(mode)
            os.replace(temp_path, path)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    def write_launcher(self, bin_dir: Path, name: str, argv: Sequence[str]) -> Path:
        bin_dir.mkdir(parents=True, exist_ok=True)
        if self.name == "windows":
            path = bin_dir / f"{name}.cmd"

            def quote(value: str) -> str:
                return '"' + value.replace('"', '""') + '"'

            command = " ".join(quote(str(v)) for v in argv)
            self._atomic_write_text(
                path,
                f"@echo off\r\n{command} %*\r\n",
                encoding="ascii",
            )
            return path

        path = bin_dir / name

        def shell_quote(value: str) -> str:
            return "'" + value.replace("'", "'\\''") + "'"

        command = " ".join(shell_quote(str(v)) for v in argv)
        self._atomic_write_text(
            path,
            f"#!/bin/sh\nexec {command} \"$@\"\n",
            encoding="utf-8",
            mode=0o755,
        )
        return path
