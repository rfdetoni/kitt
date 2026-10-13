# KITT 0.15.24 — KAP/2 goal lifecycle synchronization

## Versions

See `ecosystem.release.json` for immutable commit pins.

- Agent CLI **0.87.5**, Assistant Native **0.1.40** and Runtime **0.3.20**: all model-facing goal phases (planning, contract review, independent validation, adversarial review, and completion) now request KAP/2 structured envelopes instead of conflicting KAP/1 prompts.
- Protocol **0.13.1**, Reverse Proxy **5.3.0**, Workers **0.1.60**: unchanged from 0.15.23.
- Agent tests now parse KAP/2 prompt examples with the Protocol SDK. The read-only authority checks, runtime permissions and IPC Envelope v1 are unchanged.

## Validation gates

Agent CLI 0.87.5 passed PR Checks on the pinned revision. Publish this ecosystem version only after the Assistant multi-platform CI, root `ecosystem-main` policy, and root `ecosystem-integration` clean-install checks all pass for this exact commit. A green check from an earlier pin does not validate the new composition.

## Known limitations

- The ChatGPT Web incident with a large model-facing prompt and missing assistant DOM nodes has not been reproduced as fixed with Proxy 5.3.0; the existing tap/DOM recovery must be checked on the operator's browser installation.
- Read-only batching, version-negotiated positional arguments, host-scoped references, revision-aware patches, differential plan updates, and an exhaustive cross-repository architecture audit remain outstanding. See Protocol's KAP/2 roadmap.
