# KITT release 0.15.48 — operational KAP/2 DOM capture

## Pinned components
- Reverse Proxy 5.3.15: `e4fb75487780abedd32838c0fcd486b26df93ddd`
- Agent CLI 0.87.24: `3d0ec9058f7c925038536f71e62427f022c292ab`
- Protocol 0.13.3 unchanged: `cc3b51dd0e868adaab4ed7a0069c4dbf9aa08c42`
- All other components remain on the exact prior release pins.

## Fix
The reverse-proxy DOM mutation collector now recognizes bounded `K2 T`
tool envelopes as well as `K2 F/W/Q`, retaining strict host parsing,
pre-submit baseline and prompt-echo rejection. Agent CLI reports UI capture
timeouts as undelivered actions without automatically replaying the request.
Its `kitt-protocol` Python dependency is pinned to the immutable Protocol
commit instead of mutable `main`.

## Verification
Reverse Proxy: `npm ci && npm run verify` (Node >=24).
Agent CLI: `python -m pytest tests/test_kitt_reverse_proxy_compat.py`
(Python >=3.14 with dependencies installed).
Installer: `python -m unittest tests.test_ecosystem_release_pins`.
Authenticated ChatGPT Web UI E2E remains outstanding in this environment.
