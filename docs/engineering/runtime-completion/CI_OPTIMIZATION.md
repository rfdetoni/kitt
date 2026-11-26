# CI/CD Workflow Optimizations

## Summary of Changes Across All 8 Repositories

1. **`kitt-protocol` (PR #17)**:
   - Updated `actions/checkout` & `setup-python` to Node-24 compatible pinned SHAs.
   - Added job `timeout-minutes` bounds.
2. **`kitt-memory` (PR #27)**:
   - Gated expensive MSRV matrix compilation to non-PR runs (`github.event_name != 'pull_request'`).
   - Updated pinned action SHAs and added `timeout-minutes`.
3. **`kitt-toolbox` (PR #11)**:
   - Added explicit 15-minute job timeouts cleanly.
4. **`kitt-reverse-proxy` (PR #128)**:
   - Consolidated CI build/test steps and updated Docker buildx/setup-node pinned SHAs.
5. **`kitt-agent-cli` (PR #224)**:
   - Fixed global `--no-deps` installation bug in `pr-checks.yml` (isolated `--no-deps -e packages/...` from main install).
   - Added `timeout-minutes` bounds across `pr-checks`, `release`, `install-hygiene`, `docker` workflows.
6. **`kitt-ai-workers` (PR #33)**:
   - Consolidated Python dependency + tool installation into a single install step with isolated `--no-deps` for companion packages and `cache: pip`.
7. **`kitt-assistant` (PR #83)**:
   - Updated pinned action SHAs (`actions/checkout`, `setup-python`, `setup-node`) and aligned `kitt-protocol` (`0.14.4`) + `kitt-agent-cli` (`0.89.14`) lock/checkout pins.
   - Separated `Rune UI` wasm32 target check without stale ignored lockfile flags while keeping workspace `--locked`.
8. **`kitt` (`feat/kitt-runtime-completion`)**:
   - Enabled `platform-lifecycle` (`ubuntu-latest`, `windows-latest`, `macos-latest`) on PRs touching `installer/**` (not only manual `workflow_dispatch`).
   - Removed unused dead script `.github/scripts/next_semver.py`.
   - Updated `release.yml` to build/verify multi-OS installer bundles + `SHA256SUMS.txt` + `actions/attest` provenance.
