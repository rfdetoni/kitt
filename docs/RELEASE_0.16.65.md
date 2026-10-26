# KITT 0.16.65 — Autopilot verified delivery

- Agent CLI 0.89.2, immutable main commit `105ebd7eaf7477ab6cc6ec6cf789d2c707afc614`.
- Assistant Runtime 0.4.44, immutable main commit `30b21334d4437f2412a7e2eaea558b5614182923`; Python dependency `kitt-agent-cli>=0.89.2,<0.90`, Agent uv lock and CI checkouts aligned.
- Autopilot can publish bounded source changes through the trusted GitHub Git Data API, only to a fixed preauthorized owner/repo and branch, with a post-validation workspace fingerprint check and non-forced ref update.
- Opt-in environment: `KITT_AUTOPILOT_PUBLISH_ENABLED=true`, `KITT_AUTOPILOT_PUBLISH_REPO`, `KITT_AUTOPILOT_PUBLISH_BRANCH`, and out-of-workspace `KITT_AUTOPILOT_GITHUB_TOKEN_FILE`; the secret file must be mounted in the Agent container only. `network.access` must also be delegated.
- Defaults are safe: no remote publication and no network-enabled worker. Docker broker still exclusively holds the Docker daemon socket, and no model selected credentials/branch are permitted.

## Remaining limits

A passing CI suite demonstrates declared behavior but cannot guarantee arbitrary code correctness or fully unattended execution for every repository, complex dependency installation, network outage or protected GitHub branch. Remote publication requires operator-provided GitHub credentials. Existing historical, divergent or red-CI PRs remain unmerged pending independent reconciliation.
