# KITT 0.15.27 — KAP/2 version negotiation, logical early completion and audit

## Pinned modules

- Root 0.15.27; protocol **0.13.2** (SHA `0b9300e418557b00e371eeb2c70ef91fbf50855d`).
- Agent CLI **0.87.9** (SHA `f69d2119579bb4d56178de01d7f7763ebdc9bf74`).
  - O Agent 0.87.9 atualiza o `uv.lock` para o Protocol **0.13.2** (`0b9300e`) e inclui teste de deriva de versão instalada.
- Reverse Proxy **5.3.3** (SHA `05aa12d3578448142742dbf746fb7c078a488152`).
- Assistant **0.1.41 / Runtime 0.3.21** (SHA `5b8fdc858dece435f82fe4ff8fe98af4ceed29ae`), with Protocol 0.13.2 and Agent 0.87.9 synchronized in Rust/Python/HUD locks.
- Memory, toolbox and AI Workers retain immutable 0.15.26 pins.
- Full manifest: `ecosystem.release.json`.

## Delivered

1. `X-Kitt-KAP: KAP/2` exact selection on declared Agent HTTP
   contract requests; no downgrade for unsupported or ambiguous versions.
   Server acknowledgment required by the new Agent. `kap.capabilities`
   reports `metadata_version_negotiation=true`, and keeps
   `early_stream_termination=false` and `frame_batch=false`.
   This does **not** introduce a new `K2/n` wire grammar.
2. Reverse Proxy 5.3.3 has **two independent CDP/DOM observers**.
   The first observer to provide a stable, complete, strictly validated
   KAP/2 action correlated to the current turn wins. Tap can finish
   while the DOM is unavailable; DOM can finish if the CDP matcher fails.
   The losing observer is cancelled, **not** the upstream WebChat request.
   Single-anchor matches on segmented long prompts require unique
   provider-scoped correlation, and competing candidates fail closed.
   Roleless ChatGPT reply markup has an assistant-owned DOM fallback.
   No model-side authorization or speculative replay.
3. Multi-repo audit job inventories source files across all seven
   repositories and publishes a pinned evidence bundle as GitHub Action
   artifacts. The first audit read 816 files and classified 26 classes,
   146 methods and 11 private symbols as *review candidates*; three
   demonstrably unreferenced internal helpers were removed, with
   consumers and CI checked.
4. Python and TypeScript tests for strict version negotiation, streaming
   malformed/ambiguous payload rejection, byte-correlation safety and
   Agent request/response headers. Existing gates were not relaxed.

## Acceptance gates

Promote only after root `ecosystem-main` and
`ecosystem-integration` pass at the exact root SHA, with the immutable
pins checked against component mains. Automatic release must publish
tag `v0.15.27` at that SHA.

## Still not established by CI

- Live authenticated ChatGPT Web reproduction of the original UI failure.
- Proof of zero dead code or comprehensive removal/refactoring of every
  GOD-class/brain-method candidate in all seven repositories. The audit
  is exhaustive by files, not by verified runtime consumers.
- Early cancellation of model/upstream generation is intentionally
  not supported: `K2/END` alone is insufficient for ownership and
  exactly-once execution. The **observer** ends when its KAP/2 is validated.

No benchmarks were run.
