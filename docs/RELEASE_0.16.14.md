# KITT 0.16.14 — Clean-Room RE contract and offline isolation boundary

Pins Agent CLI 0.88.9, Protocol 0.14.1, Assistant 0.1.54 / Runtime 0.4.9 and Workers 0.1.79. Adds a structurally strict public API behavior schema, fail-closed sanitizer, reviewer-claimed private seal and trusted-digest verification, plus an opt-in networkless OCI implementer runner accepting only SHA-pinned local images with a separately prepared Wine/ReactOS checkout. Contract JSON, not the analyst history or disassembly, is the only supplied input mount.

This is NOT a claim of 100% clean-room attestation: independent human/legal review, external image supply/provenance, Windows Oracle guest E2E and independent winetest conformance verification are not automatic or verified. Treat missing prerequisites as BLOCKED_ENV; a successful container exit alone is UNVERIFIED. Reverse Proxy 5.4.9 remains unchanged and is not the authority for filesystem or process separation.
