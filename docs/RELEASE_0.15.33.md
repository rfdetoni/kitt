# KITT 0.15.33 — compact KAP/2 WebChat response recovery

## Updated immutable pin

- Reverse Proxy 5.3.8: `505ff156b54f2102dc85de0daf22bfd18c0b80ec`
- Protocol 0.13.3, Agent CLI 0.87.11, Assistant 0.1.42, AI Workers 0.1.62,
  Memory and Toolbox: unchanged immutable pins from 0.15.32.

## Incident

A WebChat model reply with a complete one-line `K2 F @json: {...} K2/END`
frame (16,848 characters) was not delivered by proxy 5.3.7 to Agent CLI.
The host saw `ui_timeout` and 0 chunks. Browser observations recorded
0 assistant nodes, 2 visible `K2/END` markers and no fresh extracted content.
The submitted prompt contained KAP examples itself; delimiter presence alone
cannot establish that a fresh assistant answer was captured.

The pasted response also had 17 non-JSON Markdown presentation escapes
(backslashes before underscores and asterisks).

## Changes in 5.3.8

- Parse frame boundaries with quote-aware braces to handle compact `@json`
  responses rendered without assistant-specific selectors.
- Recover bounded DOM `textContent` where `innerText` omits portaled spans,
  while rejecting prompt echoes, prior baselines and competing frames.
- Remove only the two known invalid presentation escapes (`\\_` and `\\*`)
  within JSON strings when the entire result then passes strict syntax checks.
  All other invalid frames remain untrusted and are sent to host validation.
- Add non-content DOM capture metrics (fresh compact candidate counts and
  sample lengths) to distinguish missing model text from parser failures.
- Regression tests cover prompt KAP examples, valid/malformed compact
  finals, Markdown escaping and failed extraction.

The canonical Protocol SDK still validates the envelope, semantic schema,
permissions and capabilities. No browser DOM parser authorizes tool calls.

## Validation boundaries

The source CI, Docker build and Chromium boundary tests are the available
gates. An authenticated end-to-end ChatGPT Web retest in the operator's
profile remains necessary; tests cannot guarantee future DOM revisions.
The root installer already consumes `ecosystem.release.json`, so a new
installer implementation is not required. The release's installer gate
must still pass before the stable root release is confirmed.
