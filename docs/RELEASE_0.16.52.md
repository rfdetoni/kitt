# KITT 0.16.52 — FreeLLMAPI execution

## Changes

- Agent CLI **0.88.52**, commit `bc4694586ee826f057d034701c2e2589960788f6`: returns plan/ask output without inferring edits; sends native tool schemas, validates tool calls before execution, preserves tool-result IDs, records token usage and surfaces redacted stream errors. Multiple calls despite serial mode receive bounded correction while retaining prior host receipts.
- Native API Goal turns use the existing authoritative GoalStepVerifier when no nested TaskPlan exists. Reusing an initialized project does not require an artificial new write; ordinary user mutation safeguards, contract checks and independent validation remain active.
- Plain and headless CLI frontends display planning/checking/revision progress before tools run, including when connected to the daemon.
- FreeLLMAPI profiles reuse saved authentication, disable unsupported native JSON mode, reserve 8192 output tokens in a 32768-token context, and bound outer retries without replaying timed-out requests. HTTP response-header waits use the configured timeout while connections remain bounded.
- Assistant Runtime **0.4.41**, commit `a17d44645deb1c7fe1bbd58d9a9f253c626efc8f`: synchronizes the minimum Agent dependency, uv lock and both CI Agent checkout pins. Other components retain their existing immutable pins.

## Validation and limits

Agent validation: 690 tests passed, 4 skipped, and 129 subtests passed. Four existing RE/VM tests still fail against the host's active Windows container and occupied SSH port; they were already reproduced on the earlier main. Assistant Python validation: 45 tests and 2 subtests passed. Python compilation and the production clean-room guard passed.

The real FreeLLMAPI run accepted the Wine task plan and executed host inspection tools. Subsequent runs also observed empty upstream responses and provider failover/timeouts. This release fixes host integration and progress reporting; it does not guarantee free-provider capacity or certify any Wine stub implementation. No Wine compilation or Windows Oracle comparison is claimed complete by these checks.
