# KITT 0.16.61 — Autonomous Git and network authorization

- Agent CLI 0.88.94: `f07ca85a3c3ede0eda4587a862d176564a676810`.
- Existing root release pins remain otherwise unchanged from 0.16.60.
- Autonomous processes can execute Git from shell scripts when `.git` is an actual directory inside the authorized workspace. Host-managed `.kitt` and external worktree metadata remain protected.
- Reject numeric (`0`/`1`), string and object `network` flags; only JSON booleans are accepted, and `true` additionally requires `network.access` capability.
- All Agent CLI CI contracts, Windows, Docker and Podman smoke tests passed before merging `rfdetoni/kitt-agent-cli#187`.
- Execution is not yet fully unattended for every codebase: Java/Node toolchains may be absent from the generic Docker fallback image, and Compose-mode Agent lacks a dedicated host-controlled container broker.
