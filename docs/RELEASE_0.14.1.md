# KITT Ecosystem 0.14.1 — Validated Agent release composition

This patch pins Agent 0.85.0 to the revision that aligns its source-tree runtime version with its package and lock metadata. Assistant, Evals and Evolution locks and the ecosystem manifest use the same corrected revision. Protocol 0.10.0, Proxy 5.0.0, Assistant 0.1.33 / runtime 0.3.0 and Workers 0.1.57 retain the structured Agent contract v3 introduced in 0.14.0.

The immutable 0.14.0 tag is preserved. No behavior or token policy changes are introduced in this patch; WebChat owns token limits.

The corrected composition passed all component CI checks, clean main installation, cross-language structured-result checks, immutable release-channel installation, Assistant release lock smoke and portable Windows/macOS installation. Structured objects preserve quotes, tabs and newlines across the actual compiled Proxy and installed Agent/Protocol decoders. Agent 0.85.0 and Proxy 5.0.0 release artifacts were published successfully. No fresh authenticated Gemini session was executed.
