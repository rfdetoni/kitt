# KITT 0.16.53 — FreeLLMAPI model discovery

- Agent CLI **0.88.53**, commit `2ce5c7bb4d4a6dfbfe7a4831dfcdc81c28db665f`: registers FreeLLMAPI in the shared catalog and model picker, authenticates `/v1/models`, retains provider identity, and uses workspace endpoints in `kitt models freellmapi --root PATH`. Custom origins still require explicit user-local trust before credentials leave the machine.
- Assistant Runtime **0.4.42**, commit `2d2c6e3a30d43769a84c733bba96e81f086811b5`: synchronizes the Python minimum dependency, uv lock and both CI checkout pins.

## Validation

The installed CLI listed 279 models from the real local FreeLLMAPI instance. Six dedicated discovery tests passed. Agent suite: 696 passed, 4 skipped, 129 subtests passed; four existing RE/VM tests still fail against the active host lab. Assistant suite: 45 passed and 2 subtests passed. Python compilation and the production clean-room guard passed.

Catalog availability does not prove upstream inference capacity. This change does not certify Wine compilation, stub implementation, or Windows Oracle comparisons.
