# KITT 0.15.55 — independent WebChat response capture

Pins Reverse Proxy 5.3.17. The new 16:38 logs confirmed that 5.3.16 could still
capture a plan and lose the following task reply: auto mode disabled CDP and
depended entirely on the provider DOM.

Auto mode now runs the passive, current-request network reader alongside DOM.
The proxy assembles stateful text patches, excludes explicit user messages,
echoed history and metadata, and returns only a unique valid KAP/2 frame. No
accepted provider request is replayed. Explicit DOM-only mode remains available.

This release is based on current main 0.15.54 and preserves its opt-in semantic
installer guidance. Agent CLI stays 0.87.29; Protocol and the other component
contracts are unchanged. `VERSION` and the release composition advance together;
the proxy package and npm lock advance together to 5.3.17.

Validation includes 284 proxy tests, 11 Chromium integrations, the 31-case
authoritative KAP/2 corpus, schema/parser parity, builds, package validation,
dependency audits and 81 installer tests. The network-only Chromium regression
fails with the previous auto-mode reader and asserts exactly one POST with the
fix. The authenticated user's ChatGPT session and a full native ecosystem
installation were not available for validation.
