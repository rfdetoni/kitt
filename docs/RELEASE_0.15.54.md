# KITT ecosystem v0.15.54 — local multilingual semantic installer guidance

## Immutable component pins
- Agent CLI v0.87.29: `cb530c2ecddaafa1241e957c3d379ea853f43863`.
- Assistant Runtime v0.3.36: `2cd77205df6deb7f7b8aa6bec3d390bc0d7e4f6e`.
- AI Workers v0.1.75: `5d1dd8998d9ca9f8d8b9b4bbecbbf5cd9c4a2bf0`.
- Reverse Proxy 5.3.16: `77bbce9137860016a23c5bdbdde03c96d8582320` (unchanged from concurrent 0.15.53 main release).
- Protocol, Memory and Toolbox pins remain as in the previous release.

## Installer and operations

Root installer `--channel release` resolves all components to immutable manifest SHAs. `python -m installer --semantic-help` displays instructions without downloading, starting services or touching installed state. Agent direct installation scripts additionally allow opt-in E5 model preparation using `install.sh --prepare-semantic-model` or `install.ps1 -PrepareSemanticModel`, after requiring a local user-owned Ollama service and validating SHA-256.

Runtime semantic mode remains disabled by default. Set `KITT_SEMANTIC_MODE=auto` and `KITT_SEMANTIC_LOCAL_MODEL=qllama/multilingual-e5-small:q8_0` after explicit preparation, and use `/semantic doctor` in TUI. This does not change the generative model or global egress policy.

## Evidence and limits

Agent 0.87.29: 467 passed, 4 skipped on Python 3.14 complete suite; Windows/Docker/Podman integration and real Ollama E5 CPU. Direct 24 PT-BR/EN/ES imperative requests were resolved by deterministic rules, not by an independently validated vector-intent classifier. Therefore this release does **not** claim measured total token savings or default-on production accuracy. Installer integrated release/main-channel CI must pass before merge.
