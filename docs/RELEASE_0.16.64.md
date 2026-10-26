# KITT 0.16.64 — Unattended sandbox execution

- Agent CLI 0.89.1 pinned at `0ddae4475cdd05d1c0c14059759ac0fd8d3ade88`.
- A Docker Compose `--profile agent` includes a trusted `sandbox-broker` sidecar.
  The sidecar alone mounts the Docker socket; the Agent uses a private
  Unix-domain socket and sandbox workers mount only the project directory.
- Broker resolves its workspace from the Docker container's own bind mount.
  Workers reuse persistent filesystem caches across commands, but not host credentials.
- Task `autopilot.checkpoint`, `autopilot.diff`, `autopilot.rollback` and
  `autopilot.verify` reuse the existing snapshot and validation infrastructure.
  Rollback requires current hashes to guard against concurrent modifications.
- Root user sessions may receive operator-predelegated network capability with
  `KITT_AUTOPILOT_DELEGATE_NETWORK=true`; the broker also requires
  `KITT_BROKER_ALLOW_NETWORK=true`. Defaults remain denied.
- Release installation and immutable revision checks must pass before main merge.

## Limits

This release does not guarantee bug-free results in arbitrary codebases.
Checkpoints are bounded and are not complete copy-on-write filesystem snapshots.
Automatic remote GitHub publication is not provided by the sandbox broker:
publish only through separately authorized GitHub integrations or approval workflows.
Existing old PRs were reviewed by ahead/behind; none was merged automatically
because old release pins, unverified changes or failing CI could regress the ecosystem.
