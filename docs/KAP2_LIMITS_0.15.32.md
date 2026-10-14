# KAP/2 transport, parser and planner limits — 0.15.32

## Root-cause evidence (14 October 2026)

The recorded ChatGPT Web answer contained 12 task/final items and `K2/END`,
but its captured representation had only one physical line (around 16 KB).
Agent received `ui_timeout` before a KAP parser exception: provider DOM
recognition, not Python AST or host authorization, was the immediate blocker.

## Verified bounds

| Boundary | Current limit | Owner |
| --- | --- | --- |
| Parsed KAP/2 frame | 65,536 UTF-8 bytes | Protocol SDKs |
| KAP/2 physical lines | 3,000 | Protocol SDKs |
| KAP/2 nesting depth | 20 | Protocol SDKs |
| KAP/2 arrays/rows | 1,024 | Protocol SDKs |
| KAP/2 compact `@json` | single-line object, same byte/depth/row limits | Protocol SDKs |
| Durable plan items | 2–12 (last item `FINAL`) | Agent planner |
| Per-task prompt / validation prompt | 6,000 / 4,000 characters | Agent planner |
| Per-task criteria, paths | 16 / 64 | Agent planner |
| Aggregated final criteria, paths, host checks | 64 / 64 / 12 | Agent planner |
| UI response timeout configured in failing logs | 180,000 ms | Reverse proxy |
| ChatGPT/Gemini response mode `auto` | DOM-first | Reverse proxy |

The 64 KiB KAP frame cap applies to **model output**, not the often much
larger OpenAI-compatible **input prompt**. Raising size/timeout limits does
not restore missing DOM line separators. The `@json:` alternative is only
for K2 final plans: explicit JSON quoting and brackets retain deterministic
field boundaries when a UI flattens whitespace. No automatic inferred
reindentation, reparenting or repair of control-plane tool calls occurs.

## Responsibility and deployment

The proxy collects a unique bounded response and excludes prompt echoes,
older baselines and competing frames; a flattened legacy frame is forwarded
only as untrusted text. The canonical Protocol validates KAP/2; invalid
legacy flattened replies raise `E_LAYOUT_LOSS`. Agent consumes contract
results, enforces task semantics, path scopes, approvals, ledger and quality
gates. No transport component may authorize a model-derived tool action.

The proxy still embeds a local KAP parser for strict fast-path decisions;
the new tagged final is carried to the canonical host parser instead of
being interpreted by the proxy. Eliminating the duplicated parser requires
an independently reviewed shared runtime distribution; that migration is
not claimed by this release. End-to-end verification against an authenticated
live browser remains separate from CI DOM fixtures.

## Observability / operational checks

Correlate `x-kitt-request-id` and the host turn; inspect
`assistant_nodes`, `structural_turn_nodes`, `visible_end_markers`,
`fresh_visible_chars` and `ui.response.dom_unparsed_for_repair`.
Interpret a complete but flattened body as captured-but-unparsed, not a
successful tool call. Reject mixed/competing frames; retry with one fresh
tagged KAP/2 final. Do not increase timeouts for `E_LAYOUT_LOSS`.

