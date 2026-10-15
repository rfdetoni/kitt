# KITT 0.16.0 — JSON model wire across the ecosystem

Coordinates Protocol 0.14.0, Agent CLI 0.88.0, Reverse Proxy 5.4.0, Assistant 0.1.45 / Runtime 0.4.0, and AI Workers / Evals / Evolution 0.1.77. Memory and Toolbox contracts need no changes.

JSON replaces active KAP use in prompts, model results, host tool actions, capture, repair and capability discovery. KAP remains archived only in kitt-protocol, behind explicit module imports. This is a coordinated breaking migration using Agent contract v5; install all components from this composition.

The installed boundary check exercises structured plans/reviews, Unicode, quotes/newlines, canonical host tool actions, duplicate keys and conflicting JSON responses through the real TypeScript proxy and Python Agent consumers. Browser/UI and network failures still stop safely without automatic prompt replay.

## Validation

- Agent CLI: 472 passed, 4 optional tests skipped; compileall and clean-room guard passed.
- Reverse Proxy: 263 unit/contract tests and 11 real Chromium integration tests passed; typecheck, production/fast builds and package-content checks passed.
- Protocol: Python unittest, TypeScript fixture/corpus validation, 5,000 seeded differential cases, Rust tests, formatting, Clippy and generated-contract parity passed. The archived KAP corpus remains in Protocol only.
- Assistant: 27 supported runtime tests and HUD TypeScript/Vite build passed. Seven daemon tests could not run because this execution environment denies AF_UNIX sockets. Native workspace metadata validated; native Assistant behavior was not changed.
- Workers: 20 passed; Evals: 3 passed; Evolution: 10 passed.
- Root installer: 86 tests passed; the installed TypeScript/Python JSON contract boundary passed, including tool mapping and conflicting payload rejection.

No authenticated live ChatGPT/Gemini session was available for a provider-side production run. Stream aborts remain transport failures and never authorize an automatic duplicate submission.
