# Ecosystem 0.13.15

The immutable manifest promotes Reverse Proxy 4.9.11 at `2de5c7d2d3ccbac31af9f274b46eeea941d4708f`. The other six components, including Agent CLI, retain their 0.13.14 revisions. No wire schema or consumer dependency changed; the Proxy package and npm lock both declare 4.9.11.

| Reproduced defect | Correction |
| --- | --- |
| Failed attachment leaked CDP sessions; concurrent initialization created duplicates | Serialize initialize/reconnect/detach and release partial attachment on failure |
| Live chunks arrived before the buffered prefix | Queue live bytes until the prefix is emitted; enforce the turn byte budget and discard pending data on cancellation/failure |
| Redirected or unsuccessful responses were accepted as raw sources | Validate final URL and 2xx status; reject redirects before extraction |
| SSE decoding trimmed source indentation, trailing spaces and multiline data | Share data-field parsing that removes only the optional protocol space, with fragmented UTF-8 and LF/CRLF/CR support |

## Acceptance evidence

The deterministic regressions reproduced the original failures before correction. Local verification passed 187 Proxy tests, TypeScript checks, production build, version metadata checks and both npm audits with zero reported vulnerabilities. Root installer/catalog validation passed 58 tests; architecture checks, Protocol/Proxy schema parity and Bash installer syntax also passed.

[Proxy PR #73](https://github.com/rfdetoni/kitt-reverse-proxy/pull/73) passed [CI](https://github.com/rfdetoni/kitt-reverse-proxy/actions/runs/37445382736) and [Docker](https://github.com/rfdetoni/kitt-reverse-proxy/actions/runs/37445382670) before merge. CI installs Chromium and runs `npm run test:browser`: a real local HTTP/SSE response earns trust against a healthy DOM, then subsequent complete contracts are captured intact while the rendered DOM is deliberately damaged. The fixture includes Unicode, fragmented multibyte characters and all three SSE newline forms. Local Chromium download was truncated; the browser result is CI evidence.

The root integration gate exercises clean ecosystem installation, immutable release installation, schema parity, consumer lock consistency and portable Agent startup. The manifest pins complete commits rather than moving component branches.

## Limits

This fixture does not cover authenticated live provider sessions. Raw recovery still requires full-prompt correlation, a previously trusted extraction profile, stream completion and strict contract validation. Cancellation, manual intervention, tap failures and competing extraction results remain guarded. Redirected raw streams use the existing DOM fallback. These changes improve response integrity; they cannot infer missing contract semantics or safely reconstruct arbitrarily truncated source.
