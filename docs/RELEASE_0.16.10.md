# KITT 0.16.10 — reproducible Windows API Oracle lab

- Opt-in `--re-oracle-bootstrap` on the full Docker RE installer delegates to Agent CLI's OEM bootstrap to configure first-boot Windows OpenSSH and a SHA-pinned probe over loopback only.
- Optional `--re-oracle-recreate` deletes *only* the authenticated KITT-owned Windows test disk, requires `--yes` and `--accept-windows-license`, and retains the existing Linux toolbox and workspace.
- Fixed, host-generated SSH identities, managed Windows host key pinning, user-level PowerShell probe.info/probe.run protocol, and bounded event synchronization sample; never interpret container=running as Oracle readiness.
- Operator-only doctor and fixed Windows/Wine pilot remain separate from model permissions or QEMU guest auto-enrollment.
- Tests cover CLI opt-in, delegation, no duplicate Dockur creation, and lock handoff. Agent CI covers forbidden actions, hash pinning, packaging and cross-platform smoke.

The end-to-end Microsoft Windows 11 first-boot OpenSSH capability and differential result remain **UNVERIFIED** until the operator runs the new release in the isolated lab.

## Immutable component pins

- Agent CLI **0.88.6**, main merge `57071e5161ed6c77bcda14aafd46077b84fab0e7`.
- Assistant **0.1.51** / Python Runtime **0.4.6** pending its own validated immutable merge; other ecosystem pins remain unchanged.
- Root ecosystem version **0.16.10**; release manifest will switch to the final Assistant commit before the root PR is merged.
