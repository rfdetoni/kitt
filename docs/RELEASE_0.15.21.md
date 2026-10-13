# KITT 0.15.21 — Completed response extraction for ChatGPT Web

## Evidence from operator's 2026-10-13 logs

- Agent CLI sent one `agent-loop` request at 18:42:32 UTC.
- Reverse Proxy 5.1.7 sent and confirmed a 64,573-character prompt in the
  ChatGPT composer.
- CDP tap returned `no_matching_request` early.
- Browser was generating until approximately 178 seconds after submit.
- DOM response extractor logged `response_chars=0` throughout.
- The proxy waited an additional ~180 seconds after the generating control
  disappeared, then failed with `ui_timeout`. The model was no longer
  generating; the browser already displayed the KITT/END response.

## Fix

This release pins Reverse Proxy 5.1.8:
`2b43baeeb0c946643850cb20e090cc4a42262aa3`.

- Adds assistant-scoped preformatted/prose selectors.
- Attempts strict KAP/1 contract recovery from the *newest assistant-owned
  DOM message* after generating stops, never from arbitrary page/user text.
- Prevents reusing a previously completed assistant contract as a new reply.
- Emits no-content diagnostics: assistant node count, candidate count and
  terminal-marker presence.
- Reports a specific extraction failure after a bounded 20-second
  post-generation grace rather than silently waiting another three minutes.
- Correlates large browser POSTs by independent start/middle/end text
  anchors, potentially distributed across JSON fields, while preserving
  same-request, origin, profile, status and stream verification. A repetitive
  prompt without distinguishable anchors retains strict full-prompt matching.
- No blind prompt replay and no unverified KAP invocation.
- Existing Agent CLI 0.86.17, Assistant 0.3.14, and other component
  pins are unchanged.

## Host-only update

```bash
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- \
  --preset full --channel release --yes
```

No VM, Windows guest or Docker/Podman provisioning changes are included.
The command requires the corresponding release tag to exist; the
main branch and release channel are distinct.

## Validation limits

CI covers correlation regression, KAP strictness/stale-reply protection
and regular proxy contracts. The authenticated Chromium DOM is not part of
CI; `ui.response.capture_missing` and `ui.tap.match_diagnostics` must be
reviewed in a live operator run to validate the actual markup.
