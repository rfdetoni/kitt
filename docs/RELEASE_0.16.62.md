# KITT 0.16.62 — Autonomous Docker toolchains

- Agent CLI `0.88.95`, immutable SHA `46a37db1af921f327528c9e833f38ff29d34c079`.
- Official fixed worker catalog: Maven/Temurin Java 25, Node 24 Bookworm, Rust 1.99 Bookworm; missing Docker images are fetched by the trusted host broker on demand.
- Sandboxed commands remain confined to an authorized workspace with resource caps, a private temporary home, no mounted Docker socket and no automatic host-shell fallback.
- Existing ecosystem component pins unchanged.
- Known limitations: combined Java/Node/Rust commands in a single shell may need to be separated; caches are ephemeral; Compose-container Agent has no dedicated trusted Docker broker; access to dependency registries requires predelegated network capability.
