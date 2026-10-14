# KITT 0.15.27 — KAP/2 version negotiation, logical early completion and audit

## Pinned modules

- Root 0.15.27; protocol **0.13.2** (SHA \`0b9300e418557b00e371eeb2c70ef91fbf50855d\`).
- Agent CLI **0.87.9** (SHA \`0aa1b3af2a4bcb49e45e8deabed8df631763823b\`).
- Reverse Proxy **5.3.2** (SHA \`1b99b47bd57429579c40091d99f6f0778956254c\`).
- Assistant, memory, toolbox and AI Workers retain immutable 0.15.26 pins.
- Full manifest: \`ecosystem.release.json\`.

## Delivered

1. \`X-Kitt-KAP: KAP/2\` exact selection on declared Agent HTTP
   contract requests; no downgrade for unsupported or ambiguous versions.
   Server acknowledgment required by the new Agent. \`kap.capabilities\`
   reports \`metadata_version_negotiation=true\`, and keeps
   \`early_stream_termination=false\` and \`frame_batch=false\`.
   This does **not** introduce a new \`K2/n\` wire grammar.
2. Proxy's early **logical read completion** may return when the
   correlated, previously trusted CDP tap has a strictly valid complete
   current KAP/2 frame, UI generation stopped, fresh assistant-owned DOM
   agrees, and tap/UI were quiet for a bounded interval. No token-level
   abort, no direct model-side authorization, no speculative replay.
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

Promote only after root \`ecosystem-main\` and
\`ecosystem-integration\` pass at the exact root SHA, with the immutable
pins checked against component mains. Automatic release must publish
tag \`v0.15.27\` at that SHA.

## Still not established by CI

- Live authenticated ChatGPT Web reproduction of the original UI failure.
- Proof of zero dead code or comprehensive removal/refactoring of every
  GOD-class/brain-method candidate in all seven repositories. The audit
  is exhaustive by files, not by verified runtime consumers.
- Early cancellation of model/upstream generation before transport
  confirmation: intentionally not supported, because \`K2/END\` alone
  is insufficient to establish ownership and exactly-once execution.

No benchmarks were run.
