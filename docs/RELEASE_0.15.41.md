# KITT 0.15.41 — Targeted high-risk Goal plan review

## Pin

Agent CLI **0.87.17** at
`7eb89ea344209885a3c62a963085a82ff827ef6b`.

Preserves all other component pins from KITT 0.15.40.

## What changed

The Agent CLI previously rebuilt the full original task list after each
high-risk reviewer `REVISE` verdict, rather than editing the last
host-validated plan. The Observatory incident on 2026-10-14 showed three
review cycles finding different defects and stopping before T00.

The planner now supplies the validated plan as the amendment baseline,
asks the model to change only what the reviewer found defective and
rechecks the entire result with the host schema and reviewer. After a
malformed revised plan, outstanding reviewer issues are retained.
The TUI phase feedback delivered in Agent 0.87.16 remains active.

The three-attempt safety cap and no-automerge/no-permission-escalation
rules are preserved. A plan can still be rejected after repeated
unresolved issues; execution never proceeds on an unreviewed plan.

## Evidence

Agent #102 CI: critical contract suite, Windows smoke,
Podman smoke, Docker smoke and Docker build all passed.
This release's own CI validates root installer pins and a clean
release-channel installation before promotion.

Host TUI and Windows oracle hardware acceptance require actual
operator-host access and have **not** been claimed from CI results.
