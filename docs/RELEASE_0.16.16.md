# KITT 0.16.16 — canonical changelogs and immutable Clean-Room component pins

Promotes Protocol **0.14.2**, Agent CLI **0.88.11**, Assistant **0.1.56** / Runtime **0.4.11**, and AI Workers/Evals/Evolution **0.1.81**. Reverse Proxy 5.4.9, Memory 0.10.2, and Toolbox 0.4.3 retain their software versions; their documentation commits are pinned by SHA.

## Release organization

- All eight ecosystem repositories store release chronology in `CHANGELOG.md`; the old README release sections have been migrated rather than discarded.
- README files now document the software itself and link to changelogs and current release guides.
- Automatic release workflows treat the new changelog as documentation-only. Actual changes to npm/Cargo/Python package metadata or lockfiles require immutable version bumps.
- The ecosystem manifest pins precise component SHAs, preserving coordinated installs without using mutable branch references.

## Clean-Room qualification

The black-box contract validator, signed review handoff, offline model image runner, independently signed test stage and scoped source auditing remain available. CI validation is not evidence of full Windows/Wine equivalence or independent implementation provenance. Operator-owned infrastructure, offline model/image provenance, signed review keys and real Oracle differential testing are required before claiming full Clean-Room.
