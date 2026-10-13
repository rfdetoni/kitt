# KITT 0.15.15 — Release pin synchronization

## Changes

- Update the integrated Reverse Proxy to version 5.1.3
  (`db67b08076da99c7916e22ef2dfa391c042810b2`) in
  `ecosystem.release.json`. All seven component pins now match their
  respective main branch heads as inspected on 2026-10-13.
- Add an explicit CI freshness check that compares pinned revisions with
  the actual GitHub `main` refs, refusing a newly validated release when
  a component has moved ahead of the manifest.
- Keep the existing release channel immutable and reproducible. Do not
  silently resolve floating branch refs from a `--channel release` install.

## Updating the complete host ecosystem without Docker

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- \
  --preset full --channel release --yes
```

The command updates host KITT components only. It does **not** pass
`--with-re-lab`, `--with-vm-containers` or `--vm-pull-images`, and
therefore does not provision, recreate, pull or reset Docker/Podman VMs
or laboratory images. It does stop/restart KITT-managed host services as
part of the normal installation flow.

## Release synchronization policy

When any component main receives a new releasable revision, update
every affected consumer lock and then `ecosystem.release.json`, bump
`VERSION`, validate integration and publish a new immutable ecosystem
release. The online pin check makes unsynchronized revisions observable
in CI; it does not silently rewrite consumers or release manifests.
