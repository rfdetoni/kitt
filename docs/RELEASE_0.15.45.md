# KITT 0.15.45 — unified KAP/2 conformance and current component pins

- Reverse Proxy 5.3.14: `12ca00379295c919ce160d5a9c211a99304ac240`.
- Proxy CI runs all authoritative KAP/2 valid/invalid fixtures from the immutable Protocol checkout; asserts parsed content and precise error codes.
- Root release manifest now matches all component main revisions including Proxy 5.3.14.
- Existing Memory 0.10.2, Agent CLI 0.87.22, Assistant Runtime 0.3.30 and AI Workers 0.1.69 commits unchanged.
- Validate ecosystem-main and ecosystem-integration, including release-channel native Assistant lock smoke.
