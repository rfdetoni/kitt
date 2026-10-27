# KITT 0.16.67 — Isolated Autopilot tasks

- Agent CLI `0.89.4`, pinned to `eaa4f198a14c24356c4d0578e9d41f54466c533b`.
- Assistant Runtime `0.4.46`, pinned to `727517fb8a91f743e5400f060245a88b5752e9a7`, with dependency `kitt-agent-cli>=0.89.4,<0.90` and synchronized CI/uv locks.
- New `autopilot.transaction.start/status/abandon` allows a single autonomous root task to work in an isolated linked Git worktree while leaving the original checkout unchanged.
- The worker sees only the task folder: native task commands require Docker; the Compose broker validates and mounts the same task root rather than the parent checkout. Weak sandbox fallback is rejected.
- Verification uses the task's root and publication requires a post-test fingerprint plus operator-scoped GitHub authorization. Existing GitHub non-force remote update guard remains.
- Task abandonment retains its worktree for audit; automatic local promotion is intentionally unavailable.
- Release gate: installer end-to-end, platform smoke, Assistant dependency lock, runtime CI and immutable pin validation.
