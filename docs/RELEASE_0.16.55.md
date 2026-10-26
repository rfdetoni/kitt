# KITT 0.16.55 — Plandex/Goose-inspired integration

## Components
- **Agent CLI 0.88.89** immutable main SHA: `c513114cfbb1f24e4738b10c7ce915f13c0762fb`.
- All other ecosystem modules remain pinned to their previous, unchanged
  immutable main revisions.

## Features
- `kitt acp --root /absolute/workspace` provides ACP v1 stdio integration
  for IDEs/clients that negotiate protocol v1, with text session prompts,
  streaming and cancellation. Approval-requiring tools fail closed without
  changing the user's KITT host policy.
- `review.preview/diff/apply/rewind` provide bounded unified diffs, persisted
  staged changes, atomic compare-and-swap writes and conflict-checked reversal.
- `recipe.preview/apply/rewind` reuse that review pipeline for declarative
  TOML write recipes, protected by the existing `repo.write` capability,
  approval policy and risk limits.
- `browser.diagnose` reports structural metrics from authorized browser
  inspection without echoing raw page, network or console data.

## Validation
PR checks include Python unit/integration contracts and package builds,
Windows, Docker and Podman smoke runs, with root installer and immutable
revision checks. Successful CI does not imply every IDE/ACP client variant
is certified or that live production browser workloads were benchmarked.

## Design boundaries
No replacement of the KITT planner, models, native Tree-sitter engine,
agents, protocol SDK, or browser provider is required. See Agent CLI
`docs/ACP_AND_REVIEW.md` and `docs/RECIPES.md` for usage and limits.
