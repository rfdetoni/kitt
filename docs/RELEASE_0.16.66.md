# KITT 0.16.66 — Persistent worker validation

- Agent CLI 0.89.3: `1b17a65f04723b2135d876d9eb4b96432412c430`.
- Assistant Runtime 0.4.45: `44970484f7f6b0ebb91c1814fbab6a3930aae4dd`.
- Real Docker integration tests now exercise persistent workspace workers, HOME cache reuse, denial of unauthorized network and read-only workspace writes, absence of the broker's Docker socket from workers, KITT state masking, and recovery after worker removal.
- Workers are reused only if image ID, network mode and readonly security settings match; wrong/stale workers are recreated.
- Parent Compose Agent still delegates local commands over a private Unix socket to a trusted sidecar. Only the sidecar has Docker socket.
- Trust and deployment limits remain: automated code publication is disabled by default and requires predelegated GitHub permissions; arbitrary projects and host setups have not been exhaustively validated.
- Installation tests, policy checks, platform compatibility and release lock verification are required to pass before merging.
