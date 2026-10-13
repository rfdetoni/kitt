# KITT 0.15.17 — Single-flight Agent and verified WebChat editor

## Pinned components
- Agent CLI 0.86.14 — `4a7843476375be17f73a88f92ee8c2042c1685d2`.
- Reverse Proxy 5.1.5 — `0dbcb6c88e25ee198da78b5de95b10d6e444530c`.
- Assistant Python runtime 0.3.11 — `b0c50eae45a79b836885097e79959e24e79c8cb1`.
- Protocol, Memory, Toolbox, and AI Workers revisions unchanged.

## What changed
1. Agent UI bridge serializes daemon bootstrap/attach and turn submission.
   Concurrent callbacks in one UI must not create multiple IPC attachments
   or send the same user prompt twice during asynchronous startup.
2. Reverse Proxy tries one bounded DOM recovery for a long rich-text
   `contenteditable` draft whose characters changed during browser fill.
   It verifies the recovered text twice; no unverified content is sent.
3. Assistant `uv.lock` now pins the same Agent revision. Its runtime
   minimum version and editable version were bumped together.
4. This ecosystem release pins all current component main SHAs.

## Upgrade the host ecosystem without Docker or Podman changes

```bash
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- \
  --preset full --channel release --yes
```

The installer updates only the KITT host programs when `--with-re-lab`,
`--with-vm-containers`, and `--vm-pull-images` are omitted. It does
stop/restart KITT-managed processes.

## Validation and remaining limitations
Regression tests cover simultaneous UI bootstrap/submit and a long rich
editor altered by the initial fill, with a single verified recovery. CI
build/test gates are authoritative; a live authenticated ChatGPT Web test
is still necessary to prove the provider DOM accepts the replacement.
The observed log had only one `send_input` to begin with; repeated
daemon attaches were the separate concurrency symptom.
