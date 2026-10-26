# KITT 0.16.59 — Python targeted host verification

- Agent CLI 0.88.92 pinned at `3a45f25f0abb0cec3925107fb3379993ac2f7aac`.
- Reverse Proxy 5.4.27 pin unchanged at `6d3a1910c0df1163d926bb6f90fb6cc16c651fa3`.
- Fixes `python.targeted-tests` UNAVAILABLE when a task explicitly requests this deterministic check and full verification is enabled. Host controls remain authoritative.
- Does not fix unrelated readonly `kitt doctor` log destination or Ghidra project visibility in the isolated workspace.
