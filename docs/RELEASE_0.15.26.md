# KITT 0.15.26 — proteção de estado concorrente e prefixos UTF-8

Data: 2026-10-13.

## Componentes e pins

- Root: **0.15.26**.
- Agent CLI: **0.87.7**, commit `ef4f205630cede465da852d3d94b0c32019d01a7`, merge do [PR #95](https://github.com/rfdetoni/kitt-agent-cli/pull/95).
- Reverse Proxy **5.3.1**, Protocol **0.13.1** e outros componentes: SHAs conservados da versão 0.15.25.
- O manifest `ecosystem.release.json` fixa o commit imutável do Agent; `ecosystem.json` continua o catálogo declarativo, não uma lista de versões.

## Correções validadas

1. **Deduplicação concorrente:** o estado de `RetrievalGuard` (geração, entradas, contadores de repetição e invalidação) usa `RLock` durante operações concorrentes do `repo.batch_read`. O `ThreadPoolExecutor` continua a executar leituras independentes; o bloqueio abrange apenas o estado compartilhado.
2. **Leitura parcial Unicode:** `repo.ref.read` usa decodificação UTF-8 incremental, descartando apenas um sufixo incompleto causado pelo limite em bytes. Entradas completas mantêm a política anterior de substituir bytes UTF-8 inválidos.
3. **Cobertura:** testes para duas operações concorrentes dentro do `RetrievalGuard` e prefixos de 1–5 bytes em conteúdo multibyte.
4. **Artefatos:** Agent CLI `pyproject.toml`, `uv.lock`, versão fallback e `docs/RELEASE_0.87.7.md` sincronizados.

O PR Agent passou **PR Checks** e **Docker** no commit `61124fce` da branch antes do merge. O SHA da main após squash é `ef4f205`.

## Aceitação do ecossistema

Esta release só pode ser considerada publicada após os workflows `ecosystem-main` e `ecosystem-integration` aprovarem o **mesmo commit da raiz**, e a tag da release aparecer. Validar o lock da versão 0.87.7 no Agent; não reduzir gates para contornar falhas.

## Limitações remanescentes

- A correção CDP/DOM do Proxy 5.3.1 passou CI, mas **a sessão real autenticada do incidente original não foi reproduzida**. O teste operacional segue necessário e não pode ser substituído por simulação.
- `kap.capabilities` continua reportando `frame_batch=false`, `early_stream_termination=false` e `metadata_version_negotiation=false`. Recursos de host (lotes, referências, argumentos posicionais e `plan.patch`) já funcionam sobre `K2 T`; isso **não** habilita automaticamente novos headers do wire protocol.
- A auditoria de arquitetura foi dirigida aos módulos alterados e seus consumidores; não elimina a necessidade de auditoria exaustiva de código morto/classes GOD/métodos brain nos sete repositórios.
- Sem benchmarks conforme a solicitação original.

Ver [revisão arquitetural](ARCHITECTURE_AUDIT_0.15.26.md).
