# KITT 0.15.34 — fix WebChat KAP/2 compact-final validation

Root manifest now pins reverse-proxy **5.3.9** at
`6edfc74b829c9d2250e85147f204ce4b0f06d5ff`.
All other component revisions remain unchanged from **0.15.33**,
including Protocol **0.13.3** and Agent CLI **0.87.11**.

## Evidence and fix

In the 2026-10-14 ChatGPT Web logs, reverse-proxy 5.3.8 captured
a **13,476-character** `K2 F @json:` final, then the internal KAP/2
validator returned `Invalid K2 header`. An unnecessary model repair
turn subsequently timed out without fresh DOM output.

The proxy now mirrors the exact published KAP/2 parser from Protocol
0.13.3. The CI parity SHA is updated from Protocol 0.13.2 to 0.13.3,
preventing this drift from recurring silently. The raw/DOM transport
reader recognizes the compact single-line header. Bootstrap and repair
prompts explicitly allow JSON **inside** the tagged KAP final, but
continue to prohibit standalone JSON.

The captured plan itself contained items T00–T10 without the mandatory
FINAL item. This remains an **Agent CLI semantic validation failure**
and must produce a bounded model retry, not tool execution.

## Release/install checks

The root installer already consumes this immutable versioned manifest;
no change to installer parsing is necessary. The proxy CI/Docker,
root release policy and integrated installer gates must pass before
the stable release is claimed. Live authenticated WebChat end-to-end
confirmation requires a separate operator test.
