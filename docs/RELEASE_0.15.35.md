# KITT 0.15.35 — Post-submit DOM response provenance

Root manifest pins Reverse Proxy **5.3.10** at `c950ad6d2d484743df0515481ac7fa019c942e22`,
retaining immutable pins of Protocol 0.13.3, Agent CLI 0.87.11,
Assistant, AI Workers, Memory and Toolbox.

## Incident evidence

In the 14 October 2026 18:25 WebChat logs, a 64,071-character
prompt was accepted; the proxy later reported 0 assistant nodes,
0 turn nodes, 3 visible KAP terminators, 1 compact candidate but
0 fresh compact candidates, and a 131,072-character DOM sample cap.
No assistant content reached the Agent CLI; timeout occurred before
Protocol parsing.

## Repair

The proxy now starts a native, bounded DOM MutationObserver before
submitting each chat turn. It captures recently changed small subtrees
that contain complete KAP envelopes, disconnects after response or
failure, and excludes composer/user nodes. The existing prompt echo,
pre-submit baseline, frame uniqueness and canonical KAP validation
checks still own acceptance; changed text alone never authorizes a
tool call. Diagnostic counters include `dom_mutation_samples`.

A Chromium test exercises post-submit response capture with no
assistant roles, an old prompt containing KAP examples, and an answer
hidden from the capped page-text tail by long DOM content.

The installer needs no new behavior: `ecosystem.release.json` already
pins each exact commit. CI, Linux/Windows/macOS installer integration and
a live authenticated WebChat retest remain separate validations. If
the provider never renders the actual answer in accessible DOM, the
proxy still fails closed.
