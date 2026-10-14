## KITT 0.15.35 — DOM freshness capture for KAP/2

This release pins reverse-proxy **5.3.10** with an opt-in,
bounded post-submit DOM mutation capture fallback for ChatGPT/Gemini
KAP/2 frames. Prompts containing embedded KAP examples are not
accepted as fresh replies. No Agent CLI/Protocol grammar change.
See [release notes](docs/RELEASE_0.15.35.md).

## KITT 0.15.34 — compact KAP/2 final accepted end to end

The root pins reverse-proxy **5.3.9**, resolving the disagreement between
the proxy's generated KAP/2 decoder and canonical Protocol **0.13.3**.
A captured `K2 F @json: {...}\nK2/END` is now recognized by the proxy
contract validator and raw transport selector, with no duplicate parser
heuristics. The host still checks that a durable plan includes the mandatory
`FINAL` item, so incomplete plans cannot execute. See
[release 0.15.34](docs/RELEASE_0.15.34.md).

## KITT 0.15.33 — WebChat KAP/2 DOM recovery

Root pins Reverse Proxy 5.3.8, which detects one-line `K2 F @json`
replies, bounds the DOM fallback, and handles only deterministic Markdown
presentation escapes without relaxing canonical host validation.
See [release notes](docs/RELEASE_0.15.33.md).

# KITT 0.15.32 — lossless KAP/2 planning replies

The root manifest now pins Protocol 0.13.3, Agent CLI 0.87.11,
Reverse Proxy 5.3.7, Assistant Runtime 0.3.23 and AI Workers 0.1.62.
The planner uses explicit single-line `K2 F @json: {...} K2/END`
structured finals to survive WebChat whitespace flattening while host
schema validation and permissions remain strict. See
[release details](docs/RELEASE_0.15.32.md) and
[KAP/2 hard limits](docs/KAP2_LIMITS_0.15.32.md).

# KITT 0.15.31 — Safe Python via KAP/2

The full release snapshot pins Agent CLI **0.87.10** with the
`sandbox.python` host operation, Assistant Runtime **0.3.22**, and
AI Workers **0.1.61** with synchronized Python `uv.lock` references.
The executor reuses the existing `python_compute` restricted AST interpreter,
rather than allowing unrestricted Python. KAP/2 grammar and Protocol 0.13.2
remain unchanged. See [release 0.15.31](docs/RELEASE_0.15.31.md).

# Ecosystem 0.15.30 — KAP/2 DOM capture after transcript virtualization

The release installer pins Reverse Proxy **5.3.6** and validates its npm package/lock versions before building. The fix locates a fresh browser-rendered KAP envelope after the submitted prompt even if old chat DOM is virtualized; collapsed malformed frames are forwarded solely to the Agent repair flow. No changes to the other component pins. See [release 0.15.30](docs/RELEASE_0.15.30.md).

undefined