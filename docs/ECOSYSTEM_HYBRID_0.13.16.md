# Ecosystem 0.13.16

The immutable manifest promotes Reverse Proxy 4.9.12 at `260802253c8d7755dd2fe68c9f20d2c1d3029b6b`. The other six components retain their 0.13.15 revisions. Package and npm lock versions are aligned; no Agent/Protocol wire or consumer dependency change is needed.

| Reproduced failure | Correction |
| --- | --- |
| A rejected streaming callback became a decode error and generated an unhandled tap rejection while the DOM monitor remained pending | Separate decoding from delivery, observe rejection immediately, propagate the original error and cancel the monitor |
| Fallback treated an empty or lagging DOM as definitive stream divergence | Wait for intermediate DOM prefixes to catch up without replay; retain final mismatch/truncation checks |

The two added regressions failed on 4.9.11 and passed after correction. Local Proxy verification passed 189 tests, TypeScript checks, production build, version metadata checks and both npm audits with zero reported vulnerabilities. Root validation passed 58 installer/catalog tests, architecture checks, manifest policy, Protocol/Proxy schema parity and Bash syntax.

[Proxy PR #74](https://github.com/rfdetoni/kitt-reverse-proxy/pull/74) passed [CI](https://github.com/rfdetoni/kitt-reverse-proxy/actions/runs/37464658094) and [Docker](https://github.com/rfdetoni/kitt-reverse-proxy/actions/runs/37464658115). The mandatory Chromium fixture now runs the actual hybrid reader against local HTTP/SSE and rendered DOM: a healthy first turn earns trust, complete raw contracts survive damaged HTML, and a failed consumer aborts monitoring while the extraction profile stays healthy. Fragmented UTF-8 and LF/CRLF/CR coverage is retained.

The root integration gate checks clean installation, immutable release installation, schema parity, Assistant locks and portable Agent startup. No gate is removed or weakened.

Authenticated live provider sessions remain outside the fixture. The fixture controls DOM-monitor timing; it does not cover live provider UI changes. Raw recovery still requires a trusted profile, full-prompt correlation, completion and a valid unambiguous payload. Cancellation and manual intervention remain guarded; missing source semantics are not inferred.
