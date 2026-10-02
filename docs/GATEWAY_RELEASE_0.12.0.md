# KITT ecosystem 0.12.0 — gateway engineering review

Release date: 2026-10-02. This review covers architecture, security, performance,
stability, prompt injection and WebChat-to-API conversion. Component revisions
below are release evidence; the installer continues to resolve `main` per run.

## Architecture decisions

Agent remains the authority for task intent, privacy, execution wallets, approvals
and tool execution. Protocol owns the cross-repository contract. Proxy owns
transport/session state, repair attempts, context acknowledgements, cancellation
and output framing. Memory owns durable receipts and reconciliation. Toolbox owns
native workspace snapshots. Assistant and Workers consume Agent policy.

Repair attempts run inside one session lease and share the original deadline and
attempt/input grant. The browser gateway is remote processing even when bound to
loopback. Context, tool results and failed candidates are serialized as untrusted
data under the English system persona. Successful response completion commits
context acknowledgement; reset/error invalidates it.

HTTP transport idempotency and durable Memory receipts solve different problems.
An uncertain submitted browser request stays pinned until lifecycle reconciliation;
it must not silently disappear and run again. A Memory post-send error is terminal
at the client and exposes request identity for `request.status` reconciliation.

## Findings and corrections

All entries have High confidence from source inspection and targeted regression
coverage. Severity describes the original behavior.

| Severity | Confidence | Location | Problem and impact | Fix | Validation |
| --- | --- | --- | --- | --- | --- |
| High | High | Agent `llm/privacy`, routing, goals, Dreaming; Workers evolution | Local proxy address was mistaken for local inference, bypassing processing policy | Shared backend/endpoint predicate; explicit gateway selection honors offline/local-only | Routing, privacy and evolution regressions |
| High | High | Agent execution budget; Proxy request state | Hidden repairs/retries could exceed the execution wallet | Atomic attempt reservation, cumulative prompt allowance, whole-request deadline and usage settlement | Budget/retry accounting and lifecycle tests |
| High | High | Proxy idempotency | TTL/eviction could remove pending or submitted-uncertain work and permit duplicate submission | Pin pending/uncertain entries; reject new work at capacity; completion TTL starts after finish | Idempotency lifecycle regressions |
| Medium | High | Proxy idempotency | Successful cached responses had no total byte bound | 64 MiB completed-response budget; evict completed entries only | Cache saturation tests |
| Medium | High | Proxy serial queue | Cancelled queued requests remained pending until earlier work finished | Remove cancelled pending entries immediately; explicit close/drain | Queue cancellation and close tests |
| High | High | Proxy session manager and context contract | Context could be acknowledged before response success or reused after reset | Transaction lease, generation identity, post-response acknowledgement and reset invalidation | Session and context lifecycle tests |
| Medium | High | Proxy context delta lowering | Repeated context was reinjected without stable segment acknowledgement | Hash segments/tool schemas separately; send compact deltas with explicit removals | Context contract tests |
| High | High | Proxy resilient/UI executors | Repair candidates could become instructions and lose original task/evidence | Bounded JSON repair evidence containing task, context, tools and candidate beneath system policy | Repair evidence and request lifecycle tests |
| Medium | High | Proxy UI executor | UI retries were incompletely counted; timeout could report partial success | Every dispatch/candidate accounts to shared state; typed timeout/contract failure; remove duplicate history cache | Executor and lifecycle tests |
| High | High | Proxy stream adapters | Stream terminal output could diverge from chunks already emitted or duplicate Ollama text | Validate emitted prefix against canonical final response; typed failure on mismatch; exact final framing | OpenAI/Responses/Anthropic/Ollama stream tests |
| Medium | High | Proxy stream I/O | Slow consumers retained writes/resources indefinitely | Ten-second drain bound, bounded pending bytes, SSE heartbeats, prompt disconnect propagation | Stream/backpressure tests |
| Medium | High | Proxy session memory sampling | Summed RSS double-counted shared memory and sampling could grow without bounds | Linux PSS over bounded process tree plus shared host PID; cached bounded sampling and visible fallback | Session memory tests; Linux behavior review |
| Medium | High | Proxy pressure handling | Memory pressure could evict busy/tool sessions | Preserve protected sessions and reject additional work under pressure | Session lifecycle tests |
| Medium | High | Agent HTTP cancellation | Cancelled consumers left network workers blocked on response reads | Shut down active sockets; cancellable retry waits and queued puts; bounded setup | Real stalled HTTP cancellation regression |
| Medium | High | Agent context envelope | Required structured context exceeded body budget or silently lost structure | Serialized JSON accounting; explicit failure if mandatory structure cannot fit | Required-context budget regression |
| High | High | Agent Memory client | Protocol/auth/correlation/post-send failures triggered automatic replay | Stable request ID; retry only pre-connect; one read deadline; bounded startup single-flight | Terminal error and real IPC tests |
| High | High | Memory daemon | Frames, connection count and I/O waits could consume unbounded resources | 1 MiB frames, 64 permits, two-second read/eight-second write bounds, bounded responses | Rust daemon and workspace tests |
| High | High | Memory SQLite | Mutation identity lacked durable conflict/uncertainty reconciliation | Serialized writes, identity/fingerprint receipts and `request.status`; uncertain receipts retained | Durable receipt conflict/replay tests |
| Medium | High | Toolbox and Agent file reads | Truncated long UTF-8 lines lost tails/newlines and could mix pages across revisions | Exact byte cursor, delimiters and full snapshot hash; stale-page rejection | Native read tests and Agent UTF-8/CRLF roundtrip |
| High | High | Toolbox edits | Hash/parse/replacement could observe different snapshots | Derive all edit state from one snapshot; process mutex; atomic persistence and pre-persist full hash check | Rust edit/snapshot tests |
| Medium | High | Workers STT server | Failed temporary-file creation/write retained the single-worker lock | Put creation/write inside structured cleanup; release lock and unlink if created | Failure cleanup regression |
| High | High | Assistant daemon shutdown | Python 3.14 listener wait occurred before client closure and could hang forever | Close accepted clients before waiting; bounded grace/abort; bounded writer cleanup; await writer cancellation | Live idle-client shutdown and full daemon suite |
| Medium | High | Agent USER surface policy | Non-executable registered UI actions were blocked by wrapper approval | Permit only exact USER `surface.action` through canonical SafeRuntime validation | Registered/unregistered action and other-operation policy tests |
| Medium | High | Agent Memory startup | Missing/disabled/unlaunchable daemon caused three-second polling with no process to await | Poll only after successful launch; retain single-flight cooldown and identity | One-call/zero-sleep unavailable-startup regression |
| Medium | High | Assistant CI discovery | unittest discovery omitted daemon tests in namespace subdirectories | Run pytest over the full test tree; expose stalled-task stacks | Full runtime CI, including previously omitted cases |
| Medium | High | Root contract composition | Independent generated contract copies could drift without an install-time gate | Compare Protocol exporter with Proxy copy at actual installed SHAs | Schema equality check and main-install CI |

## Validation evidence

- Agent: 180 passed, one skipped, three subtests; compileall, clean-room packaging,
  strict unused-symbol/security lint and uv lock consistency passed.
- Proxy 4.9.1: 146 tests plus TypeScript check/build; component CI, Docker and release
  workflows passed. Protocol-generated schema matches exactly.
- Protocol 0.8.0: Rust/Python contracts, TypeScript fixtures/typecheck and CI passed.
- Memory 0.8.1: 37 Rust tests, formatting/Clippy and CI passed. Atomic permit code
  uses compare-exchange compatible with the ecosystem MSRV and current stable.
- Toolbox 0.3.0: 15 Rust tests, formatting/Clippy, Python 3.14 native-wheel import
  and CI passed. Cargo.lock is tracked; wheel builds use the selected interpreter.
- Workers 0.1.42: 30 Python tests and lint passed; main-resolved consumer locks
  are refreshed after the final Agent promotion.
- Assistant Runtime 0.2.30: 28 Python tests passed locally over its production TCP
  transport. Unix transport also passed all 28 tests in component CI; HUD passed.
  Rust core is checked by the same workflow.
- Root: 51 tests and seven subtests, catalog/architecture validation, installer
  syntax and the new exact schema gate passed locally.

Component CI links are recorded below. The root clean main-install workflow runs
on promotion and checks schema equality at its actual installed revisions.

## Performance interpretation and operational limits

The previous core queue microbenchmark measured approximately 1.315 microseconds
per operation over 20,000 iterations on Node 24. It is a workload observation,
not a measured improvement against a baseline. Stability improvements remove
unbounded waits, duplicate context and unnecessary polling; browser inference
latency still dominates and must be measured against each provider.

Transport cancellation does not undo already submitted remote work. Browser
idempotency is process-local; it is not exactly-once across restarts. Uncertain
entries are deliberately retained and may require reconciliation/session reset.
Completed cache entries expire after five minutes and share a 64 MiB bound;
the registry rejects work when its 512 entries are all protected.

Memory completed receipts have seven-day retention; uncertain receipts remain
pinned. `not_found` after pruning is not proof that a mutation never executed.
Frame/resource bounds and SQLite serialized writes do not provide a transaction
covering third-party systems.

Native edits cannot eliminate the final race against an unrelated external
writer between the last hash check and rename. Consumers must use the expected
snapshot hash. Native and Python reads retain the workspace containment authority.

Linux PSS sampling is bounded and cached; partial/fallback measurements remain
visible. Windows and unavailable procfs use fallback rather than Linux PSS.
Third-party legacy provider plugins cannot always preflight the actual rendered
prompt; their completed requests are charged conservatively. UI/network usage
may be estimated when the provider does not expose authoritative token counts.

The review does not claim authenticated live-provider browser E2E coverage. The
provider scenarios deferred in 0.11.0 still require authorized sessions and
provider-specific validation. Unit/transport contract coverage is recorded
separately from that operational evidence.

## Promoted components

| Component | Version | Main revision | Validation workflow |
| --- | --- | --- | --- |
| Agent CLI | 0.83.3 | `701bbf3b1f5237056745e1bc90bcaf78326d3cc1` | [PR Checks](https://github.com/rfdetoni/kitt-agent-cli/actions/runs/37008979784) |
| Reverse Proxy | 4.9.1 | `6fe810e784393961d19e498feae450c98a4506bf` | [CI](https://github.com/rfdetoni/kitt-reverse-proxy/actions/runs/37003856881) |
| Protocol | 0.8.0 | `bf6cb7cb4eb7b8e6d0b873180519dd5c999dc8ac` | [CI](https://github.com/rfdetoni/kitt-protocol/actions/runs/36998291790) |
| Memory | 0.8.1 | `33d50f6b64425fcc915efc1caa8ce4e971692a8e` | [CI](https://github.com/rfdetoni/kitt-memory/actions/runs/37002274987) |
| Toolbox | 0.3.0 | `3d81ad11035499ad9bb9db84cb30b383b75320ef` | [CI](https://github.com/rfdetoni/kitt-toolbox/actions/runs/37000391771) |
| Assistant | Runtime 0.2.30; native/HUD 0.1.16 | `3e6189e26f120c875d684d75668bf2b85750cf1b` | [CI](https://github.com/rfdetoni/kitt-assistant/actions/runs/37009412959) |
| AI Workers / Evolution / Evals | 0.1.42 | `9336a4e21b3c7be6272aa4b52f8fc6a09ef6d251` | Latest-main CI; previous behavior gate [passed](https://github.com/rfdetoni/kitt-ai-workers/actions/runs/37004045702) |

Root version is 0.12.0. Its main-install gate verifies a fresh installation, the
installed Python graph, entrypoints, recorded main SHAs, architecture and
Protocol/Proxy contract equality. The installer deliberately has no permanent
cross-repository SHA lock.
