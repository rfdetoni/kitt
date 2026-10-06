# Ecosystem 0.13.19

This composition promotes Reverse Proxy 4.9.14 at `11f58c341cdf88083d6fae0dde001616c90b5b4e` while preserving the other six revisions from 0.13.18, including Agent CLI 0.83.17 and the Assistant/AI Workers REA lock alignment. The Agent/Protocol wire contract and consumer dependency locks do not change; Proxy package and npm lock versions agree.

## Failure and correction

The supplied 4.9.13 Gemini logs show eleven valid contracts: the requested planning response and ten successful read/list tool calls. The next request failed after 180 seconds without response bytes. There is no submission-confirmation evidence for that last prompt, so its acceptance by the live provider cannot be established.

Code inspection and a failing reproduction found that the UI sender silently returned when its five-second acceptance window expired. A failed editor read also masqueraded as an empty, cleared editor. The sender now requires a connected readable cleared editor, generation start or an assistant response change against a pre-send baseline. Unconfirmed submission produces the existing terminal `ui_automation_error`, with no automatic resend or reset. Generation in progress prevents changing a user draft.

The response monitor uses the same provider and semantic generation controls as submission, preventing a partial answer from settling while an otherwise unrecognized stop control remains visible. Settled final responses are recognized before checking inactivity; the Chromium regression exposed an incorrect timeout with the minimum one-second budget. Existing inactivity/absolute budgets and raw-contract trust checks remain intact. New diagnostics distinguish submission confirmation from response inactivity and record metadata, without logging draft/answer contents.

## Validation

The submission regression failed before correction. Local verification passed 193 Proxy tests, TypeScript checks/build, both dependency audits with zero reported vulnerabilities, 30 Agent consumer tests plus three subtests, 58 root installer/catalog tests, architecture/manifest checks and Protocol/Proxy schema parity. Existing consumer retry policy treats `ui_automation_error` as terminal; no Agent code change is necessary.

[Proxy PR #76](https://github.com/rfdetoni/kitt-reverse-proxy/pull/76) passed [CI](https://github.com/rfdetoni/kitt-reverse-proxy/actions/runs/37513303194) and [Docker](https://github.com/rfdetoni/kitt-reverse-proxy/actions/runs/37513303187). All three required Chromium tests passed. The browser suite additionally covers ignored submission, fast response acceptance with a retained composer, draft preservation and semantic generation until a complete answer. The ecosystem integration gate verifies clean installation, release-channel startup, Assistant dependency locks and portable installers.

## Limits

The observed live timeout is not attributed to a dropped submission without browser evidence. The concrete sender defects and inconsistent generation selectors are corrected and reproduced independently. The supplied session's CDP tap remained untrusted and then disabled by its breaker; live Gemini network correlation is not claimed fixed. Browser fixtures do not authenticate with a live account. No response or tool execution is invented when the provider outcome is unknown.
