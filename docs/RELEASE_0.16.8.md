# KITT 0.16.8 — Agent CLI approval hardening and ecosystem synchronization

The release manifest pins the validated Agent CLI **0.88.4** commit `f3c7889ab356441ef87f0726149fd1f337c2f1ee` and Assistant **0.1.49** / Python Runtime **0.4.4** commit `f5efbf6b00d959a75a0968c553978768d006eb6e`.

- Agent 0.88.4: persist approvals before publishing, reject stale/reused IDs, retire cancelled requests, preserve concrete resume tool and original patch preconditions.
- Parallel contract work includes the currently scheduled item and avoids path/directory conflicts.
- Assistant CI and uv lock consume the identical immutable Agent commit; workspace Cargo version and local lock entries agree.
- No contract revisions are needed for Protocol, Memory, Toolbox, AI Workers or Reverse Proxy. Their immutable pins remain unchanged.
- Versioned source and release-channel installs must both pass end-to-end validation, including installer safety, lock freshness, daemon and runtime smoke tests.

No shared wire schema or external backward-compatibility layer was added.
