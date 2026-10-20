# KITT Ecosystem 0.16.26 — release metadata / pins

## Immutable versions

- Agent CLI **0.88.21** at `0484f2e81351d8c8bdab0cd9722d5b026ba98b25`, [PR #127](https://github.com/rfdetoni/kitt-agent-cli/pull/127).
- Assistant **0.1.60** / Python Runtime **0.4.15** at `6b019b311a7b02e7c2f5a0f50078216f4d049ed3`, [PR #54](https://github.com/rfdetoni/kitt-assistant/pull/54).
- Reverse Proxy remains **5.4.14** at `9dc9e788d77827eb5df04775a1c1b58a231764b5`.
- Protocol, Memory, Toolbox and AI Workers retain previous immutable revisions.

The CLI source-tree fallback version, pyproject version and uv.lock version are all 0.88.21, fixing its Automatic Release validation failure. The Assistant runtime and CI use the same CLI commit. No changes to permissions, approval gate behavior, workspace fences or sandbox fallback.

The main integration workflows validate the full installer, pin consistency and Assistant lock smoke; they do not establish that the user's local strong sandbox is available or that the Windows/Wine pilot has completed. Upgrade the daemon/CLI together and confirm the effective autonomy profile after connecting.
