# KITT 0.16.63 — Reliable autonomous toolchain isolation

- Agent CLI 0.88.97 pinned at `2a21ca81d87df5c3ec5d87f49ef8b5102ea5e062`.
- Autonomous Maven/Gradle/Node/Rust build commands prefer fixed, provisionable Docker workers, even when Bubblewrap is functional.
- Generic Git, shell and inspection commands continue to use Bubblewrap when it works. Sandbox confinement remains mandatory; no host-shell fallback or privilege escalation.
- Real Docker smoke tested workspace writes, read-only profile, network isolation and masking of KITT control-plane state (Agent 0.88.96).
- Remaining limitations: untrusted toolchains and packages can fail due to dependency network access; network must be delegated ahead of time; worker cache is ephemeral; no Compose-mode trusted remote broker or transactional workspace publishing yet.
