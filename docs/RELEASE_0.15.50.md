# KITT ecosystem 0.15.50 — contract planner convergence

## Component pins
- Agent CLI 0.87.26: cea70a4227b3ba66455ef968cddcbc3468f65e61
- Assistant Runtime 0.3.33: 403143c6592be5bc80a905553d195e286b679a14
- AI Workers 0.1.72: f4f1b9856f626a8b66d1a953b4d80db4c4ff37a0
- Protocol, Memory, Toolbox and Reverse Proxy unchanged.

## Why
Evidence from October 15 agent-cli / reverse-proxy logs: a large Windows API Observatory mission generated a bounded plan but the host validator silently copied every task's criteria and optional dependencies into FINAL. The high-risk independent reviewer then correctly flagged the inflated FINAL and optional gates, causing repeated lengthy review/revision turns before execution.

## Fix
- Preserve explicitly authored FINAL criteria, host checks, paths and dependencies during host validation; verify individual task criteria at their original steps.
- Preserve global limits of 64 distinct criteria, 64 unique paths and 12 host check IDs.
- Strengthen planner prompt so optional or unavailable infrastructure extensions do not block required MVP deliverables.
- Contract regression tests, new release-critical checks, no permission escalation or protocol/schema migration.

## Validation
Agent CLI PR #106 CI: release-critical, Windows packaging, Docker and Podman smoke tests succeeded before main. Clean ecosystem installer/integration workflow validates updated pins.
