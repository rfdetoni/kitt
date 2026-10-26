# KITT 0.16.56 — hardened review/ACP and browser observability

## Immutable main revisions
- Agent CLI **0.88.90**: `717d2cf780638369db4a61a4907135eef8bcc91f`.
- Reverse Proxy **5.4.26**: `a757b21a8225645355bdd9bda0b896e1c9539c28`.
- Protocol, Memory, Toolbox, Assistant and AI Workers preserve their exact
  previously validated immutable main pins.

## Delivered
- Review files and recipes now bind staged changes to a principal,
  re-check the actual file paths/digests against host policy, and use
  SQLite atomic compare-and-swap claims against concurrent writers.
- ACP v1 gains same-workspace session loading, explicit client permission
  requests and host-minted, nonce-bound one-time grants; tool call states
  stream as session updates. Client-provided MCP servers and embedded
  media remain unsupported.
- Local `kitt review` list/diff/apply/rewind UX; bounded recipe values,
  file checks and read-only post-apply hooks.
- Origin-scoped Playwright JS/console/network error counts, SHA-256
  fingerprints and bounded evidence through `browser.diagnose`.
- Reverse Proxy patches transitive `body-parser` and `fast-uri`
  dependency vulnerabilities; `package-lock.json` pins patched versions.
- Agent CI adds a measured review preview/apply/rewind p50/p95 and
  Python peak-memory microbenchmark. This is not an end-to-end provider
  or Kubernetes latency benchmark.

## Validation and remaining scope
The root CI exercises installer policy, syntax, Windows/macOS portability,
Linux end-to-end installation and immutable release SHA checks, including
Assistant lock. The component PR checks cover agent security/unit
regressions and real Chromium browser tests. Successful CI does not
certify external ACP client compatibility with all IDE variants,
production provider token economics, or deployment-specific load tests.

User-managed host write policy is never elevated by recipes or review
identifiers. ASK/DENY for individual staged paths remain fail-closed.
