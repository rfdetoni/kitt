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

The root `rfdetoni/kitt` repository owns installation, dependency resolution and the immutable compatibility snapshot in `ecosystem.lock.json`. It must not become a shared source-code dumping ground.

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

rfdetoni/kitt composes compatible revisions of every context.
```

Arrows are collaboration/dependency relationships, not permission to import sibling internals.

## Strategic rules

1. **One authority per concept.** Conversation execution belongs to Agent; durable semantic memory belongs to Memory; provider transport belongs to Reverse Proxy.
2. **Contracts over shared internals.** Cross-context data moves through `kitt-protocol` or an explicitly versioned public interface.
3. **Dependencies are directional.** A context can depend on a contract or companion without taking ownership of its implementation.
4. **Infrastructure stays infrastructure.** HTTP clients, SQLite adapters, TUI renderers, browser automation and native bridges are not domain entities merely because DDD is used elsewhere.
5. **Aggregates require consistency boundaries.** Use aggregate-like modeling only when a set of state changes must preserve one invariant/transactional lifecycle.
6. **Composition is immutable.** The root lock promotes only revisions that passed component and cross-repository validation.
7. **Fallback preserves behavior.** Optional native or resident components may accelerate/enrich behavior but may not silently change security semantics.

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

`scripts/validate_architecture.py` validates the catalog dependency graph and checks that every catalog repository is represented in this document. CI runs it together with the ecosystem lock validation.

This guard intentionally checks high-value ownership/dependency invariants rather than cosmetic package names.
