# KITT 0.16.60 — Autonomous sandbox execution

- Agent CLI 0.88.93 pinned at `1f62784529b1abab64c66586d6b4d2f53bd59b37`.
- Existing root release component pins remain unchanged.
- The installer preflights the local Docker daemon and ensures the `ghcr.io/rfdetoni/kitt-agent-cli:latest` sandbox image is present; Docker is never exposed to model commands.
- Agent `sandbox.run` accepts unrestricted commands only within an authenticated, strongly isolated workspace and requires both `process.run` and `repo.write`; network egress additionally needs `network.access`.
- This increment does not implement sandbox-proxy RPC for Compose-mode Agent; containerized Agent without Bubblewrap remains blocked. No unisolated fallback is permitted.
