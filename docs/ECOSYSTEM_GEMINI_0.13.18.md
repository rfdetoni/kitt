# Ecosystem 0.13.18

The immutable manifest promotes Reverse Proxy 4.9.13 at `2761e541b504d02eb85a2ee13ab34ee275be17cd`. The other six components retain the governed REA snapshot’s 0.13.17 revisions. Package and npm lock versions agree; Agent/Protocol wire contracts and consumer dependency locks are unchanged.

## Reported failure and correction

The supplied Gemini logs contain one complete initial `use_tool` object twice: a standalone JSON-labelled object, followed by its exact fenced copy. The parser rejected the presentation and spent two repair attempts. The final repair changed `reasoning_summary` and loop data, which correctly failed continuity. No host tool was delivered.

The shared parser now recognizes only the exact plain-object/fenced mirror, removes presentation wrappers and validates one unchanged payload. Differing or incomplete copies, extra prose, multiple bare objects, duplicate keys and ambiguous interpretations remain rejected. The 2 MiB limit applies before removing wrappers or copies. Source strings and repair continuity are preserved; separate tool envelopes are not deduplicated.

The UI executor also prevents display artifact blocks from decorating Agent or structured-output responses. A separate reproduced case appended unrelated TypeScript to a valid JSON contract. Generic chat artifact display and explicit filename-matched tool hydration remain available. The logs establish the duplicate response but do not establish whether it originated in provider rendering or artifact augmentation.

## Evidence

Three new regressions failed before correction. Local verification passed 192 Proxy tests, TypeScript checks, build, version metadata and both npm audits with zero reported vulnerabilities. The exact contract-only log fixture now returns one original `kitt_runtime` call with `operation=repo.list`, `path=.`, and the original summary, using one upstream attempt.

[Proxy PR #75](https://github.com/rfdetoni/kitt-reverse-proxy/pull/75) passed [CI](https://github.com/rfdetoni/kitt-reverse-proxy/actions/runs/37496983360) and [Docker](https://github.com/rfdetoni/kitt-reverse-proxy/actions/runs/37496983384). Both required Chromium tests passed: the hybrid reader preserves complete source and cancels failed delivery; real Gemini-style DOM snapshots preserve the captured contract beside an unrelated code artifact.

Root local validation passed 58 installer/catalog tests, manifest policy, architecture checks, Protocol/Proxy schema parity and Bash syntax. The integration gate exercises clean installation, immutable release installation, Assistant locks and portable Agent startup.

## Capture limits

The logs show the CDP tap in shadow mode without trust, falling back with `no_matching_request` or `stall`. This release repairs the concrete DOM fallback response; it does not claim to fix live Gemini request correlation/timing without network capture evidence. The browser fixture does not authenticate with a live provider. Raw recovery still requires a trusted profile, full-prompt correlation, stream completion and a valid unambiguous payload. Missing source semantics are never invented.
