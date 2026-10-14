# KITT 0.15.29 — rendered DOM KAP completion recovery

## Incident evidence
User logs dated 2026-10-14 13:48 show Reverse Proxy v5.3.4 using DOM-only auto mode. The browser submitted a 63,593-character prompt and observed generation for approximately 285 seconds, but every read logged `response_chars: 0`. The final probe found `text_samples: 2`, `visible_end_markers: 1`, and zero recognized assistant nodes/turn nodes, then returned `ui_timeout` to the Agent.

A visible KAP end marker is not itself a validated reply; it may come from the submitted prompt.

## Change
Root pins **kitt-reverse-proxy v5.3.5** at SHA
`8218b521a710dde7c8d26f792eb28a5ac8cba40b`.

Proxy reads code block `textContent` and visible page body as well as legacy `main` selectors so response portals and indentation-preserving KAP elements remain detectable. It captures full visible pre-submit baseline before both initial prompts and repair prompts. Completed strict KAP frames finish normally; uniquely delimited, fresh and stable *malformed* frames may only enter the host-owned validation/repair path, never directly authorize tool calls. Counts-only telemetry records new visible chars and marker presence without exposing response text.

All six other repository pins remain unchanged from root 0.15.28. ChatGPT and Gemini still default to DOM-only; CDP tap remains available only when explicitly enabled.

## Verification
Proxy PR #84 passed TypeScript, release-contract unit tests, Chromium integration tests including responses outside `main` and roleless code blocks, and Docker build at its exact PR head.

Before root promotion, `ecosystem-main` and `ecosystem-integration` must pass at the exact root SHA, including clean Linux installation, release-channel smoke, Assistant lock checks and portable installer checks.

Authenticated browser production reproduction is **not** provided by CI. Confirm after updating that the actually running proxy is 5.3.5 and inspect non-sensitive `dom_fresh_visible_chars` progress if a different UI revision remains unsupported.
