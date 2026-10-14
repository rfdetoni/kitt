# KITT 0.15.32 — KAP/2 single-line plan resilience

## Composed immutable revisions

- Protocol 0.13.3: `cc3b51dd0e868adaab4ed7a0069c4dbf9aa08c42`
- Agent CLI 0.87.11: `53edf7bd75f7326e0a5d4303c8f0d12b5c8baaf3`
- Reverse Proxy 5.3.7: `e4b08073380e37fdd0dbd441efe7ec5d8be662b2`
- Assistant native 0.1.42 / Python runtime 0.3.23: `e5ded96e8ab550358267d2ebe7ff83366e4305cd`
- AI Workers 0.1.62 / Evals and Evolution 0.1.59: `d72a50ee4d022b89fc1c70875b32e86d2f2316d3`
- Memory and Toolbox remain pinned at prior revisions.

## Changes

- Browser DOM captures uniquely fresh flattened KAP/2 frames for **host
  validation**, rather than discarding them until transport timeout.
- Protocol accepts an **explicit tagged, single-line** K2 final:
  `K2 F @json: {"items":[...]} K2/END`, strictly checking key uniqueness,
  unsafe keys, structure, depth, size and arrays. Indented KAP/2 remains
  supported unchanged.
- The Agent planner requests this form for complex plans, eliminating
  indentation dependency for that route; tool authorization stays unchanged.
- Rust, Python and npm component versions and consumer lockfiles are aligned
  with this root `ecosystem.release.json`.

See [validated boundaries and limitations](KAP2_LIMITS_0.15.32.md).
Browser-authenticated E2E remains an external verification gate; CI fixture
and pipeline success must not be represented as live-provider validation.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- --preset full --channel release --yes
```
