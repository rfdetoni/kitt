# KITT 0.16.20 — private HOME for networkless Wine Oracle pilot

## Promotion

- Agent CLI **0.88.16**, immutable commit
  `38b0bf49b58ed3452c03c0a9689f35f69fff4e25`
  ([PR #119](https://github.com/rfdetoni/kitt-agent-cli/pull/119)).
- Existing Protocol, Memory, Assistant, Toolbox, AI Workers and Reverse Proxy
  SHAs are unchanged from 0.16.19.
- Root `VERSION`, README, changelog and `ecosystem.release.json` agree on
  `0.16.20`.

## Verified diagnosis

The actual Windows 11 Oracle `event_auto_reset` probe succeeded:
`exit_code=0`, `timed_out=false`, `truncated=false` and the observation
`{"before":258,"signaled":0,"consumed":258}`.

Linux Wine was launched as a non-root host UID with `HOME=/tmp` on a root-owned
Docker tmpfs and returned exit code 1 with a directory ownership refusal.
In 0.88.16 the command creates mode 0700 `/tmp/kitt-home` using a fixed static
shell preamble before executing the exact hash-pinned 64-bit probe, with
`HOME=/tmp/kitt-home` and `WINEPREFIX=/tmp/kitt-home/.wine`.

The pilot still uses network isolation, read-only root, no privileges,
bounded resources, immutable Linux image ID, approved PE and no OEM secret
mounts. No Windows VM reset, new Wine dependency or image bump is necessary.
Invalid Windows receipts are rejected before candidate execution, and failed
Wine execution yields only a bounded exit code rather than raw guest stderr.

## Validation

Agent CI passed full Python regression/critical contracts, uv lock, build,
Windows package smoke and both Docker and Podman runtime smoke. Root
`ecosystem-main` and `ecosystem-integration` must validate the release
composition and exact SHA pins before merging.

**Operator acceptance remains required**: after installing 0.16.20, run
`kitt --version` and `kitt re lab verify --full`. A green CI pipeline does
not certify a successful live Wine+Windows differential scenario, and
`guest_attested` remains false.
