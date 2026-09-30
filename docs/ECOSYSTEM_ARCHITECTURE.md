# K.I.T.T. Ecosystem Architecture

This repository is the composition boundary for the K.I.T.T. ecosystem. The architecture uses domain-driven boundaries where they express real ownership and consistency rules; it does not impose ceremonial DDD layers on adapters or infrastructure.

## Bounded contexts

| Module id | Repository | Bounded context | Owns |
| --- | --- | --- | --- |
| `protocol` | `rfdetoni/kitt-protocol` | Shared Contracts | versioned cross-component contracts and SDKs |
| `memory` | `rfdetoni/kitt-memory` | Semantic Memory | durable memory, provenance, retrieval, lifecycle and dream persistence |
| `toolbox` | `rfdetoni/kitt-toolbox` | Native Data Plane | native repository/code intelligence and acceleration |
| `assistant` | `rfdetoni/kitt-assistant` | Resident Assistant | daemon, remote runtime and Control Center lifecycle |
| `agent-cli` | `rfdetoni/kitt-agent-cli` | Agent Execution | task semantics, goals, execution orchestration, approvals and workspace policy |
| `ai-workers` | `rfdetoni/kitt-ai-workers` | Evaluation/AI Workers | evals, evolution and optional heavy workers |
| `reverse-proxy` | `rfdetoni/kitt-reverse-proxy` | Provider Gateway | authorized API/web-provider transport, sessions and provider plugins |

The root `rfdetoni/kitt` repository owns installation, dependency resolution and cross-repository compatibility validation. It composes the current `main` branches by default and must not become a shared source-code dumping ground.

## Context map

```text
                         +------------------+
                         | kitt-protocol    |
                         | shared contracts |
                         +---------+--------+
                                   ^
             +---------------------+----------------------+
             |                     |                      |
             |                     |                      |
+------------+---------+ +---------+---------+ +----------+----------+
| kitt-memory          | | kitt-assistant   | | kitt-reverse-proxy |
| semantic memory      | | resident runtime | | provider gateway    |
+------------+---------+ +---------+---------+ +----------+----------+
             ^                     ^                      ^
             |                     |                      |
             +----------+----------+----------+-----------+
                        |                     |
               +--------+---------+   +-------+---------+
               | kitt-agent-cli  |   | kitt-ai-workers |
               | execution       |   | eval/evolution   |
               +--------+---------+   +-----------------+
                        |
                        v
               +--------+---------+
               | kitt-toolbox    |
               | native data     |
               +-----------------+

rfdetoni/kitt composes the current `main` revision of every selected context.
```

Arrows are collaboration/dependency relationships, not permission to import sibling internals.

## Agent Engineering ownership in 0.10

The Agent Engineering contracts introduced by Protocol 0.5 are intentionally
cross-language value contracts, not new shared runtime authorities:

| Contract / concern | Runtime owner | Notes |
| --- | --- | --- |
| `AgentEvent`, replayable run state | Agent CLI | persisted by the Agent EventLedger; Assistant transports events only |
| `ExecutionBudget`, `BudgetLease`, `AgentLineage` | Agent CLI | one parent wallet; child workers consume leased slices |
| `ExecutionAuthoritySnapshot`, `SavedPermission` | Agent CLI | policy/approval authority; Assistant forwards daemon identity only |
| `ContextEpoch`, `CompactionCheckpoint`, recovery refs | Agent CLI | exact bytes remain in Agent ArtifactStore; Protocol defines shape |
| `WorkspaceSnapshot` | Agent CLI | captured/restored under Agent workspace mutation fencing |
| `RecallTrace`, `MemoryConsumptionReceipt`, `MemoryJob` | Memory | kitt-memoryd remains the only durable semantic-memory authority |
| Task Episode efficiency and learning candidates | Agent CLI + AI Workers | Agent records evidence; Workers/Evals evaluate candidates; no silent live auto-apply |
| `PluginCapabilities` | Plugin host (Agent) | declarations narrow exports; host permissions remain authority |

A companion may cache or transport one of these values, but it must not create a
second durable source of truth for the same lifecycle.

## Strategic rules

1. **One authority per concept.** Conversation execution belongs to Agent; durable semantic memory belongs to Memory; provider transport belongs to Reverse Proxy.
2. **Contracts over shared internals.** Cross-context data moves through `kitt-protocol` or an explicitly versioned public interface.
3. **Dependencies are directional.** A context can depend on a contract or companion without taking ownership of its implementation.
4. **Infrastructure stays infrastructure.** HTTP clients, SQLite adapters, TUI renderers, browser automation and native bridges are not domain entities merely because DDD is used elsewhere.
5. **Aggregates require consistency boundaries.** Use aggregate-like modeling only when a set of state changes must preserve one invariant/transactional lifecycle.
6. **Composition follows main.** The root installer resolves every selected K.I.T.T. repository from `main` by default; explicit tags/SHAs are opt-in diagnostic overrides.
7. **Fallback preserves behavior.** Optional native or resident components may accelerate/enrich behavior but may not silently change security semantics.
8. **CI snapshots are ephemeral.** Cross-repository CI resolves moving refs to concrete SHAs once at the start of a run so that run is internally consistent. Those SHAs are evidence for that run, not a persistent ecosystem lock.

## Compatibility invariants

A promotion must preserve or intentionally version:

- protocol and wire schemas;
- model-facing Agent runtime contracts;
- memory ownership/lifecycle semantics;
- installer dependency closure;
- Python namespace composition;
- platform support declared by the catalog;
- provider-gateway contracts used by the Agent;
- native fallback semantics.

If a change crosses more than one bounded context, prefer a staged compatibility window: add compatible contract support first, promote both sides, then remove the old contract in a later release.

## Tactical DDD guidance

Use value objects for identity/configuration with stable invariants. Use domain services for domain rules that do not belong to one entity. Introduce repository abstractions only when domain/application code genuinely needs persistence independence.

Do **not** introduce a generic `domain/application/infrastructure` folder hierarchy into every repository by policy. Each repository should express the same dependency direction using its native language and existing structure.

## Governance

`scripts/validate_architecture.py` validates the catalog dependency graph and checks that every catalog repository is represented in this document. CI runs it together with the main-first ecosystem validation.

This guard intentionally checks high-value ownership/dependency invariants rather than cosmetic package names.
