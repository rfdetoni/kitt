# KITT 0.15.56 — opt-in offline PT-BR/EN/ES lexicon

This release aligns the current ecosystem with Agent CLI **0.87.30**, Assistant Runtime **0.3.37** and AI Workers **0.1.76**. Existing Protocol, Memory, Toolbox and Reverse Proxy **5.3.17** pins remain unchanged.

The Agent accepts operator-supplied UniMorph PT/EN/ES verb-inflection tables and Open Multilingual Wordnet data via an offline, bounded compiler with SHA-256 provenance. WordNet synonyms are recorded **only as unapproved candidates**. Optional build-time wordfreq, Snowball and spaCy enrich metadata, and are not installed as runtime requirements. The installer `--semantic-help` points to the Agent lexicon guide.

## Privacy and licensing

The root installer downloads no lexical corpora and starts no Ollama services. Operators explicitly obtain compatible corpus releases and acknowledge language-specific licenses. UniMorph PT/EN/ES is CC BY-SA 3.0; OpenWN-PT is CC BY-SA 3.0; English Princeton WordNet has its own OSI-approved WordNet license. `wordfreq` code is Apache 2.0 and its datasets may use CC BY-SA 4.0. See [Agent lexicon documentation](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/SEMANTIC_LEXICON.md).

The semantic mode remains **off by default**. The lexicon and encoder do not alter approval policy, and original user prompts are never rewritten.

## Validation scope

CI must validate the Agent regression suite and real CPU Ollama integration, each consumer's uv locks and runtime checks, and the root main-first, release-channel and native installer smoke. This change does not establish an end-to-end token savings benchmark or broad, calibrated accuracy for imported lexical resources.
