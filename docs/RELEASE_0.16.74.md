# KITT 0.16.74 — directory listing in bounded read-only flows

## Symptom and cause

The Agent CLI logs captured on 2026-10-28 show a `flow.execute` graph being rejected when its child operation was `repo.list`, although the same file listing already worked as an individual `kitt_runtime` call and inside `repo.batch_read`. The explicit read-only allowlist omitted `repo.list`.

## Fix

Agent CLI 0.89.10 extends the shared read-only operation allowlist to include `repo.list`. Existing capability checks (`repo.read`), path-scoped filesystem access, list bounds, and the ban on mutations / process execution remain intact. Regression tests cover parallel listings, the program runtime, missing capabilities and forbidden writes. No Proxy code changed.

## Immutable component pins

- Agent CLI 0.89.10: `3b9cde3505cda1b452b76c89d528b3d1dac75bd4`
- Reverse Proxy 5.4.30: `05d8527c54551caf1e7f525a14a78ee4e7a86acf`
- All other components: unchanged from 0.16.73.

## Verification

Agent PR #202 passed critical contracts, Docker, Podman, Windows and build CI before merge. The KITT ecosystem PR must pass installer and manifest validation prior to integration. Browser integration remains covered by Reverse Proxy 5.4.30 CI and was not modified in this patch.
