# KITT 0.15.28 — WebChat DOM-only KAP recovery

## Root cause

An authenticated ChatGPT Web request in Reverse Proxy 5.3.3 generated a
completed KAP/2 response, but the 2.47 MB CDP tap ended `stream_aborted`
and the old role/test-id selectors found no assistant text, ultimately
returning `ui_timeout`. Gemini Web showed the same final-frame
symptom after the existing contract repair loop.

## Fix

- Pins `kitt-reverse-proxy` **5.3.4**, SHA
  `2227549163c5fef64c989badd744e07a0f9b6757`.
- ChatGPT and Gemini UI requests on default `readMode=auto`
  use only the DOM observer. CDP tap is not initialized or armed.
  `--read-mode tap` preserves explicit debugging access.
- The DOM reader examines current assistant/model-response fragments
  plus bounded visible conversation text when selectors have changed,
  validates only complete KAP/2 frames and requires a stable observation.
  Previous visible answers and submitted-prompt KAP examples cannot be
  replayed. Competing valid frames and newer unfinished frames fail closed.
- Stable invalid text still reaches the existing Agent contract repair
  flow after extended settling, instead of being held until transport
  timeout. The host remains the only authority for tool execution.
- Browser model generation is not aborted, nor are requests retried
  without host approval.

## Immutable composition

All other six repository pins are unchanged from root 0.15.27.
Only the Reverse Proxy SHA and root release version are advanced.

## Evidence and limits

- Proxy PR #83 passed TypeScript checks, focused KAP unit tests, real
  Playwright Chromium integration for both ChatGPT-like and Gemini-like
  DOM fixtures with CDP unavailable, and Docker build.
- Root `ecosystem-main`, `installer-portability` and clean
  `ecosystem-integration` must pass before this root release is merged.
- No authenticated production browser E2E was executed by CI.
  Operator replay of the originally failing authenticated session is
  required to confirm effectiveness against live UI revisions.

No benchmarks were run.
