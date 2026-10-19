# KITT 0.16.18 — Wine, Wine64, WineHQ Staging guests

Pins Agent CLI **0.88.13**, Linux RE container-image family **0.86.11**, Assistant **0.1.58** / runtime **0.4.13**, and AI Workers/Evals/Evolution **0.1.83**. Reverse Proxy 5.4.10, Protocol 0.14.2, Memory and Toolbox versions remain unchanged.

- Linux RE full/wine images contain real Debian `wine` and `wine64`, plus separate authenticated WineHQ Staging amd64+i386 and a `wine-staging` launcher. The exact package versions are written into `/usr/share/kitt/re-wine-packages.lock`. The full image retains REA, Ghidra and Frida.
- `kitt re lab upgrade-linux --approve` performs an operator-confirmed, networkless image preflight, then replaces only the KITT-managed Linux container while keeping the bind-mounted workspace and the Dockur Windows guest; on error it attempts rollback by previous image content ID.
- Dedicated CI builds the full and wine profiles and invokes all 3 Wine commands, while Python tests cover workspace safety, rollback and access control.
- **Host upgrade steps:** update the Agent CLI, run `kitt vm container pull --runtime docker --image toolbox --profile full` (or `build`) and `kitt re lab upgrade-linux --approve`; verify within `kitt re shell linux`.
- [Full RE Wine-Staging guide](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/RE_WINE_STAGING.md).

This image installs runtimes, **not** the Wine-Staging editable source tree. Its package repo and application binaries are separate from your host. Windows Oracle/real differential tests remain separate; this release does not certify arbitrary executable safety in a Linux container or full Clean-Room conformance.
