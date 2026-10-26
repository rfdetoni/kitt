# KITT 0.16.54 — Agent MCP discovery and declarative recipes

## Scope

The root ecosystem manifest retains immutable pins for all seven components.
Agent CLI 0.88.87 adds:

- Schema introspection via the existing policy-gated MCP runtime.
- Bounded, read-only TOML recipes backed by the existing program interpreter.
- Regression coverage for capability gating, scoped tool visibility, forbidden
  mutations, path containment and bounded workspace enumeration.

The Reverse Proxy release pin is refreshed to its newer main commit. Unmodified
components keep their previous immutable SHAs.

## Integration validation

Root installer policy, syntax, Windows/macOS portable installation and
end-to-end ecosystem checks are run by the repository CI. The Agent CLI has
its own contract, unit/integration, Windows package, Docker and Podman checks.

A CI pass does not authorize production deployment without verifying the
intended environment, Docker runtime and authenticated provider workloads.

## Not part of this release

ACP server/client support, general-purpose mutable recipes, new Tree-sitter
parsers and a new diff history engine were not introduced. Tree-sitter indexing,
workspace snapshots/worktrees and step-aware context selection already exist
and remain under their current subsystem owners.
