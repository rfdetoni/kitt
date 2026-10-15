# KITT 0.16.1 — validated JSON ecosystem composition

Retains the JSON Agent contract v5 migration from [0.16.0](RELEASE_0.16.0.md), with final Agent, Assistant and Workers commit pins. Agent's static CI checks now pass, the release companion uses the JSON-compatible Assistant runtime, Assistant CI checks out the matching Agent revision, and third-party Rust registry versions/checksums remain unchanged.

All model communication uses JSON. KAP implementations remain archived only in kitt-protocol. Versions: Protocol 0.14.0, Agent CLI 0.88.0, Reverse Proxy 5.4.0, Assistant 0.1.45 / Runtime 0.4.0 / HUD 0.1.19, and Workers/Evals/Evolution 0.1.77. Memory and Toolbox stay unchanged.

See the 0.16.0 validation record for local test coverage and environment limitations.
