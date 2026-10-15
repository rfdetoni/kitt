# KITT ecosystem v0.15.53 — multilingual semantic Agent

## Immutable component pins
- Agent CLI v0.87.29: `cb530c2ecddaafa1241e957c3d379ea853f43863`.
- Assistant Runtime v0.3.36: `2cd77205df6deb7f7b8aa6bec3d390bc0d7e4f6e`.
- AI Workers v0.1.75: `5d1dd8998d9ca9f8d8b9b4bbecbbf5cd9c4a2bf0`.
- Protocol, Memory, Toolbox, Reverse Proxy: unchanged release manifest SHAs, because their APIs were not modified.

## Installer and operations

The root installer in `--channel release` resolves each component to these immutable commits. `python -m installer --semantic-help` provides a no-download setup guide. Agent direct install scripts additionally offer an explicit preparation flag: `install.sh --prepare-semantic-model` / `install.ps1 -PrepareSemanticModel`. In all normal install and startup flows, embeddings are disabled by default, and neither Ollama nor model weights are downloaded.

Enable an already prepared model with `KITT_SEMANTIC_MODE=auto` and `KITT_SEMANTIC_LOCAL_MODEL=qllama/multilingual-e5-small:q8_0`. Use `/semantic doctor` to diagnose missing services. The semantic stage is optional; it does not change generative LLM provider selection or global privacy policy. E5 weights are hosted by a third party and verified by full SHA-256 by the Agent preparation script.

## Validation and limitations

Agent CLI v0.87.29 PR/main tests include Python 3.14 complete suite, 467 passed and 4 skipped, Windows, Podman, Docker and real CPU Ollama embeddings. Direct multilingual commands were covered by deterministic rules, not an independently calibrated vector-classification holdout. An opt-in version of the semantic engine is being released, not a claim of overall token reduction. Root release integration checks verify main/release installs and the frozen manifest.
