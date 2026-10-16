# KITT 0.16.7 — complete autonomous and approved process flow

Pins Agent CLI 0.88.3 and Assistant 0.1.48 / Runtime 0.4.3. User-selected allow-all now applies to inline Python/Node processes. Manual approvals persist the exact effective tool and payload, pass the waiting Goal's approval fence, and resume its contract once after evidence persistence. Plain fallback uses the same contract approval owner.

The release installer gets the coordinated revisions from `ecosystem.release.json`. Protocol and other component contracts are unchanged. Update both Agent and daemon and restart them. An already terminal failed contract must be started again; stale requests are not replayed automatically.

Tests reproduce the original modal and Goal lease errors on Agent 0.88.2. Corrected coverage starts from model JSON and includes actual registry preflight, durable pending actions, grants, leased Goal state transitions, one-time command execution, patch concurrency guards and plain fallback. IPC transport validation remains unavailable in the local restricted environment.
