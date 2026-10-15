# KITT ecosystem 0.15.51 — planning progress UX

## Immutable pins

- Agent CLI 0.87.27: 33c83bbb6b05d06ea4dc91020ac9d7e2f78dfed3
- Assistant Runtime 0.3.34: 7c88a0d06a69f5c4d6ae5f228ff142110dd56442
- AI Workers 0.1.73: d9a50bcdfb8aa80ff1fbc4a45d3f1777a499c151
- Protocol, Memory, Toolbox and Reverse Proxy unchanged.

## Changes

- Contract planner emits host-owned phases; TUI displays generating, reviewing, revising, accepted, scheduled and executing. During a model wait, HUD reports current attempt and stage-specific elapsed time, and the agent dashboard shows a waiting state instead of fabricated percentages.
- On transition or failure, the previous stage closes. The existing contract validation remains authoritative; no extra orchestration or policy changes.
- The October 15 proxy log also showed a genuine UI capture timeout after generation. It cannot be marked fixed by a TUI change: the proxy rejected old K2 frames correctly; authenticated live-browser reproduction is needed to distinguish DOM markup drift from a missing reply. Do not automatically replay provider output or reuse stale frames.

## Validation
Agent CLI 0.87.27 PR release-critical contracts, Windows package, Docker and Podman smoke tests passed. Assistant Runtime and AI Workers CI passed at the pinned commits. Ecosystem integration tests run on this release commit.
