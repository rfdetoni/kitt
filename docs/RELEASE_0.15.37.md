# KITT 0.15.37 — durable Goals must execute via host tools

## Exact component revisions

- Agent CLI 0.87.12: `4b955a82633fccc4ba6ffef3c97703b1dfda0916`
- Assistant Runtime 0.3.24 (native Assistant unchanged):
  `f38ae400484a4981d40f052e25aeeb2755036abf`
- AI Workers 0.1.63; Evals/Evolution 0.1.60:
  `d3ed9e2d75ecc341511671b2137c762c6b080955`
- Reverse Proxy 5.3.11, Protocol 0.13.3, Memory, Toolbox:
  immutable pins unchanged from 0.15.36

## Diagnosed incident: 2026-10-14 19:00–19:05

Logs confirm T00 submission through reverse-proxy 5.3.11
(`ui.prompt.submission` confirmed) and successful delivery to
Agent CLI (five model responses, zero host tool calls).

The Goals completion prompt unconditionally told the model to
respond exactly with KAP/2 `K2 F`, contradicting host-tool execution.
The model reported an inaccessible ChatGPT Web sandbox instead of
requesting `K2 T kitt_runtime`. The Goals outer verifier permitted
the no-tool final, leading to repeated `INCOMPLETE` reports.

## Correction

- The Agent now explicitly requests KAP/2 `K2 T` tool actions
  before criteria reports; a WebChat sandbox is never KITT host evidence.
- The host rejects premature final-only durable Goals turns with a
  bounded corrective prompt; after exhaustion it blocks instead
  of inventing progress.
- Approved host-action resumes are exempt to prevent repeating
  already approved actions.
- No permissions or tools are silently granted. Existing policy,
  evidence ledger and host validation remain authoritative.

## Installation / validation

The root installer consumes exact refs in `ecosystem.release.json`.
No installer code change is necessary. Verify root policy, clean
Linux installation, portable Windows/macOS installer gates and
a live authenticated WebChat request before declaring end-to-end
completion. In the live test, T00 must produce a real host
`kitt_runtime` tool event/receipt before any K2 F report.
