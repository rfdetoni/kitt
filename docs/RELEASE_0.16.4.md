# KITT 0.16.4 — assistant patch decoding and terminal response recovery

Pins Reverse Proxy 5.4.3 (`9c78ea71d7e877672c51e41b1bf0accfefe6f5a8`). Other component pins and dependency locks remain unchanged; the shared model contract is still JSON Agent v5.

The latest 5.4.2 logs show successful planning and `repo.list`, then loss of the next response. Proxy capture now reconstructs ordered implicit patch batches and nonempty message snapshots, recognizes complete escape presentation, and excludes reasoning, user echoes and metadata copies. A complete correlated JSON object with observed SSE `[DONE]` survives a later CDP connection failure. Partial, ambiguous, cancelled or metadata-only data remains rejected; host schema validation and tool permissions remain mandatory.

Validation: 270 Proxy unit tests, 15 Chromium integrations, 86 root installer/catalog tests and installed Agent/Protocol/Proxy interoperability. The recorded action is a data-only fixture and is never executed. Reproduction covers observed frame shapes and post-EOF transport failure; the complete original stream and an authenticated live provider session were unavailable.
