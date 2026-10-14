# KITT 0.15.40 — Goal planning progress visible in Agent TUI

## Pinned change

Agent CLI **0.87.16** at immutable commit
`dab23c8819e4af61830b25386beeb268ef5f86fb`.
All other component SHAs remain at their previously validated root
0.15.39 release pins.

## Incident

On 2026-10-14 the Agent CLI and reverse-proxy logs showed that the
Windows API Observatory mission was undergoing three model-generated
task plans and three required high-risk contract reviews. The reviewer
returned `REVISE` on all three proposals. Every model turn in those logs
reported `tool_calls=0`. T00 had therefore **not yet executed**.

The WebChat UI captured the complete responses; the issue was missing
host-owned progress signals during planning/review, not a lost HTTP
response or a model tool-execution attempt.

## Behavior

- The TUI HUD and transcript now distinguish `PLANNING n/3`,
  `REVIEWING n/3`, `REVISING n/3`, accepted/scheduled contracts,
  active execution items and bounded plan-rejection outcomes.
- New `ContractProgress` events travel through the existing daemon IPC
  and UI event reducer; there is no second plan scheduler or permission
  bypass.
- The progress stream reports item identifiers and counts only; it does
  not expose prompts, model reasoning, secrets, or fabricated completion
  percentages. A model response validating a plan is never displayed as
  proof of a completed task.
- Three consecutive `REVISE` verdicts still cause a clear planning
  failure. The underlying evidence bar is not lowered merely to make
  the dashboard advance.

The Agent CLI critical release suite, Windows/Podman/Docker smokes and
Docker build passed for the pinned commit. Real WebChat and TUI
acceptance on the operator's host remains separate from CI.
