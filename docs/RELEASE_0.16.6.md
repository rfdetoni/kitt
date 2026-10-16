# KITT 0.16.6 — approvals resume without reopening the permission modal

Pins Agent CLI 0.88.2 and Assistant 0.1.47 / Runtime 0.4.2. Saving a remembered allow rule no longer invalidates the explicitly approved waiting action. Revocations and other authority changes still block execution. Terminal execution failures are acknowledged separately from approval decisions, so the TUI closes the request and displays its error instead of asking again.

The release installer resolves both corrected components through `ecosystem.release.json`; edge continues to resolve main. No installer code or Protocol schema change is required. Update the installation and restart the Agent/daemon to load both corrected components. Restart an already failed contract after updating; terminal stale requests are not replayed automatically.

Validation: Agent regressions reproduce the failure on the old main and pass after the fix; the full Agent suite passes. Assistant tests exercise the real handler, SQLite, single-use grants, process execution and Goal resumption. Unix-socket IPC tests cannot run in the restricted validation container (EPERM also reproduced on the old main).
