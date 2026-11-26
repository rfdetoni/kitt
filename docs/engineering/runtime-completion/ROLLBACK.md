# Rollback & Recovery Procedures

## 1. Installer Level Rollback (End-User / Operator)

Every install/update via `SourceFreeEcosystemInstaller` persists the previous `installed-state.json` and launchers under `<root>/.rollback/previous/`.

- **Recover interrupted install/update**:
  ```bash
  kitt-installer --repair --root ~/.local/share/kitt --bin-dir ~/.local/bin
  ```
  Cleans stale `<root>/.staging/*` artifacts and repairs safe lockfile metadata drift via `installer/managed_drift.py`.
- **Roll back to N-1 installation**:
  ```bash
  kitt-installer --rollback --root ~/.local/share/kitt --bin-dir ~/.local/bin
  ```
  Stops active K.I.T.T. services (`stop_kitt_services`), restores previous launchers and `installed-state.json`.
- **Clean uninstall**:
  ```bash
  kitt-installer --uninstall --root ~/.local/share/kitt --bin-dir ~/.local/bin
  ```
  Stops running processes, unregisters systemd/launchd/Windows Scheduled Tasks (`unregister_kitt_services`), cleans Windows user `PATH`, removes launchers, and deletes `<root>`.

## 2. Repository / Release Level Rollback

All `v0.16.76` pins are immutable 40-character Git SHAs in `ecosystem.release.json`. To revert the ecosystem release:
1. Create a forward revert commit on `kitt` pointing `VERSION` to `0.16.77` and `ecosystem.release.json` to the prior known-good baseline (`0.16.75` component SHAs). Never overwrite or delete existing published release tags (`v0.16.75`, `v0.16.76`).
2. Run `scripts/validate_ecosystem_main.py --release` before publishing the forward revert tag.

## 3. GPU Lease & Worker Crash Recovery

If a worker crashes mid-provision or mid-terminate:
1. Inspect leases via `leases` action or Rune UI `Workers`.
2. Reconcile orphaned leases via `leases_reconcile` (`release_orphans: true` after verifying no container owns the lease).
3. For stuck `INDETERMINATE` leases where physical GPU idle state is operator-verified, invoke `leases_force_release` with an explicit audit reason.
