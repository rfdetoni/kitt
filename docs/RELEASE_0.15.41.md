# KITT 0.15.41 — performance changes and immutable integration pins

## Updated components

- Agent CLI 0.87.18: `7d8e821352964addb9ab25acef8aa9f96f3461f6`
- Reverse Proxy 5.3.12: `33820cb069e2cbeff27a05cb8474dc4b1a2e4b8c`
- Assistant Runtime 0.3.26: `d14b4f66c4d5f49876b6ad86a9dd73c486054828`
- AI Workers 0.1.65: `0ad67a601aa15e5dfca9a7e71b899e36ee8da7f2`

Protocol 0.13.3, Memory and the Rust Toolbox keep their previous immutable pins.

## Behavior

- More selective SQLite repository-index writes and reads; FTS5 maintenance remains transactional and independently audited on startup.
- Less repeated KAP/2 DOM candidate parsing, and cursor-based CDP event consumption.
- All Python consumers use the same validated Agent commit. No public KAP/2 wire grammar, trust, permission, RE/VM lifecycle or STT changes.

## Validation

Re-run Agent, Proxy, Assistant and AI Workers CI as well as root installer and release-manifest checks. Rust runtime rewrites and changes to RE workload concurrency are intentionally not introduced without comparative benchmarks; this release addresses verified overhead without enlarging system boundaries.
