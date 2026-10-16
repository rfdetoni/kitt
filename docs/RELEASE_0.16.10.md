# KITT 0.16.10 — Agent-owned Linux RE / Dockur Windows lab

The full installer delegates `--with-re-lab` to the installed Agent CLI's
single canonical `kitt re lab setup` implementation.

- Initial setup uses upstream Dockur official image pinned by registry digest;
  private Docker storage, generated Windows credentials, OEM OpenSSH and
  host-key-pinned fixed probes. Existing guest storage is preserved.
- The Linux RE full toolbox is networkless. The fixed Wine probe runs in a
  separate ephemeral, read-only, networkless Docker Linux container.
- The installer requires `--preset full --with-re-lab --yes --accept-windows-license`.
  `--re-oracle-bootstrap` is retained as a compatible alias, but the full
  RE lab setup already provisions the Oracle.
- The old installer reset flag is rejected. Destructive scope reset requires
  `kitt re lab recreate --scope windows --destroy-data --dry-run` and a
  fresh token and explicit Windows license approval.
- The installer reports PROVISIONING, not Oracle READY, until real Windows/KVM
  `probe.info` succeeds. Windows 11 licensed host E2E remains an external gate.
- Release manifests pin immutable Agent CLI and Assistant main commits;
  non-RE components remain unchanged.
