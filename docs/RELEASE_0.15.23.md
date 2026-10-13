# KITT 0.15.23 — KAP/2 hardened contract and integration fixes

## Included revisions

The authoritative immutable revision list is in `ecosystem.release.json`. This release updates:
- kitt-protocol **0.13.1**: KAP/2 strict Python/TypeScript decoders, typed errors, quoted keys, nested object arrays, UTF-8 literal length, schema-guided primitives, shared fixtures and 5,000-case differential fuzzing
- kitt-reverse-proxy **5.3.0**: canonical KAP/2 parser including typed diagnostic errors, ChatGPT UI/CDP recovery, and normalized Express 5.2.1 npm lock
- kitt-agent-cli **0.87.4**: Protocol 0.13.1 parser pin
- kitt-ai-workers **0.1.60**: Protocol 0.13.1 dependency pin
- kitt-assistant **0.1.39**, Runtime **0.3.19**: updated Agent and Protocol locks; fixed Cargo.lock `tracing-core` from an unresolvable 0.1.37 entry to the available 0.1.36

The trusted host remains responsible for validation, approvals, and tool authority. IPC Envelope v1 remains unchanged.

## Validation

- Protocol: TypeScript fixtures, Python tests, Rust checks and deterministic 5,000-case Python ↔ TypeScript parser fuzz — **passed**
- Agent CLI and Workers: module CI — **passed**
- Proxy: CI following Express lock correction — **passed**
- Assistant: Rust, Python, HUD and Linux/Windows/macOS service-manager checks following tracing-core lock correction — **passed**
- Root: clean installation and end-to-end release composition must pass on this exact manifest before publishing this root release

## Browser recovery issue from operator logs

The captured 2026-10-13 incident used **Proxy 5.2.1**, not this newly pinned 5.3.0. The UI composer accepted and submitted a large prompt (about 64k characters) and the browser showed generation activity. However CDP request correlation never became trusted (`no_matching_request`) and DOM response extraction found zero assistant nodes, so the proxy returned a `ui_timeout` error. This is a **transport/capture failure**, not evidence of malformed KAP response. The current proxy has independent DOM and tap fallbacks, but the log alone does not demonstrate that the incident is resolved. Agent 0.87.4 also includes the separate observed `FailoverLLMClient.create_kitt_proxy_browser_gateway` missing-method error with primary-provider-scoped delegation, and migrates planning/review prompts from legacy KAP/1 to KAP/2. A reproduction on 5.3.0 is required.

## Deferred scope

Read-only batches, version-negotiated positional arguments, host-scoped references, revision-based patches and differential plans are tracked as proposals in the Protocol roadmap, not silently enabled. The comprehensive cross-repository dead-code/God-class/brain-method architecture audit remains separate work.
