# KITT 0.16.9 — Docker/Podman discovery and managed RE Docker lab integration

Release-channel pins:

- Agent CLI **0.88.5**, immutable main commit `27b21b09af724c0b62efefff07baea15d15087c0`.
- Assistant **0.1.50** / Python runtime **0.4.5**, immutable main commit `d60938253a946714387a421a762b687f1d8ea4a9`.
- Reverse Proxy **5.4.5**, Protocol **0.14.0**, Memory, Toolbox and AI Workers retain their previously validated immutable commits.

## RE Docker improvements

- Install-time `--vm-container-runtime auto` resolves Docker first if healthy, then Podman. Explicit engine preferences never silently switch.
- Agent CLI `kitt re status` identifies existing, installer-managed `kitt-re-full` Linux RE toolbox and `kitt-re-win11` Dockur Windows by verified labels, expected private mounts, image identity and isolation; failures are reported as blocked instead of trusted.
- `kitt re setup linux|windows` without `--source` recognizes already provisioned Docker labs rather than requiring another ISO; explicit ISO/QCOW2 remains a separate QEMU VM workflow.
- Operator-only `kitt re start|stop linux|windows` controls existing verified containers by pinned ID; `kitt re shell linux` opens the existing toolbox via a terminal. No Docker container or VM disk is recreated, deleted or automatically enrolled as an authenticated guest.
- Windows Dockur is inventory-visible, but `oracle_ready=false` until separate guest SSH forced-command authentication is verified. This release does not automatically grant model-led Docker administration or Windows probes.
- Assistant runtime/Cargo and Python locks and Agent CI checkout pins are coordinated with the final Agent SHA. The root installer release manifest pins both current main commits.

## Verification

Agent PR #113: focused ownership, lifecycle and container-runtime tests, full regression suite, Docker/Podman smoke, Windows smoke and static checks. Assistant PR #47: runtime Python, Rust, HUD and lifecycle checks across Linux/macOS/Windows. Root installer PR #69: cross-platform installer and end-to-end ecosystem checks before merge.
