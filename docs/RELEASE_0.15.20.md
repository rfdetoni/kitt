# KITT 0.15.20 — Correlated CDP stream progress and complete KAP recovery

## Incident

On 2026-10-13 at 18:01:11 UTC, KITT submitted exactly one
Windows API Observatory planning request to ChatGPT Web. The browser
reported an active response but the proxy's DOM monitor showed
`response_chars=0`. At 18:05:11 UTC the request failed with
`request_deadline_exceeded`. The actual request carried
`kitt_meta.deadline_ms=240000`, despite an HTTP transport timeout of
960 s. The model's visible completion ending `KITT/END` was not
returned to the Agent.

## Corrections

- Agent CLI **0.86.17** (SHA
  `ade5b6d4d6f2b82ee5fd58bd0e688fddfdb14132`):
  `turn_model.py` now limits the deadline to the lesser of 900,000 ms
  and remaining durable execution budget. This removes the incorrect
  fixed 240,000-ms cap at the metadata source.
- Reverse Proxy **5.1.7** (SHA
  `28e8d8d48c57074b213dae5c866b7c168e2ac83e`):
  its existing passive CDP response tap feeds correlated-byte
  progress into the UI monitoring watchdog. KAP/1 envelopes ending
  in `KITT/END` are understood by the strict, trusted raw-stream
  completion path; the response still passes downstream host
  validation. Untrusted/cold taps cannot bypass DOM verification.
  In all cases an absolute time limit remains, and the prompt is
  never blindly replayed.
- Assistant Runtime **0.3.14** (SHA
  `9786ad50c56cd8b2cbda3fb851667502742347a7`):
  Python lock and CI checkouts pin the Agent revision.

Other four component pins remain unchanged.

## Operator update without changing Docker/Podman

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- \
  --preset full --channel release --yes
```

No VM or RE-container flags are enabled, so the command updates the
host KITT components without intentionally altering Docker/Podman
guests, images, volumes or the lab.

## Validation

The Agent regression covers a 600-second model budget. Reverse Proxy
tests cover strict KAP parsing and correlated tap activity when no DOM
assistant text is available. CDP correlation requires a matching
provider POST and a successful, completed stream. The first live
authenticated ChatGPT Web turn may still require DOM extraction until
a trusted tap profile is learned; use `ui.tap.*` and
`ui.response.progress` logs to inspect whether CDP chunks are available.
