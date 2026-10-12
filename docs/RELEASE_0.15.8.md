# KITT ecosystem 0.15.8 — REA-enabled full Linux reverse-engineering image

## Coordinated components

- Agent CLI **0.86.10**: prebuilt Docker/Podman `full` Linux toolbox includes pinned published `rea-agents@6.4.0` with Node.js 24.11.0 in addition to Ghidra 12.1.4, Frida 17.23.3, Wine and GDB/LLDB.
- Assistant runtime **0.3.8**: synchronized Agent dependency and immutable lock SHA; no daemon/protocol changes.
- KITT root **0.15.8**: coordinated manifest, README, Docker/Podman and complete VM documentation.

## Integration scope

- Opt-in `kitt-rea` plugin adds `rea_workflow` suggestions for native, JS/Electron, .NET, comparisons, core dumps and packet captures, reusing REA MCP and KITT's existing approval/evidence layer.
- `rea` in the toolbox can be used via `kitt vm container toolbox --runtime podman --profile full --workspace PATH`; it does **not** automatically register a host MCP server or appear inside unrelated guest ISOs.
- Base and Wine toolboxes do not acquire the Node/REA runtime. Normal KITT programming use remains unaffected.

## Build, publish and validation

Image PR CI verifies the exact installed REA CLI, Node, Ghidra and Frida. The main branch pipeline publishes GHCR tags when it completes successfully. Pull errors remain optional; operators can build locally.

Real Windows/Linux boot, rootless Podman/KVM access and cross-guest instrumented execution require operator-run acceptance checks and should not be considered verified by static CI.

See [VM Docker/Podman guide](VM_CONTAINERS_DOCKER_PODMAN.md) and [REA technical integration](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/REA.md).
