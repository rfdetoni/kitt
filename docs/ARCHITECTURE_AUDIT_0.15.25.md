# Auditoria arquitetural KITT 0.15.25 — escopo, evidências e riscos

Data: 2026-10-13. Revisão Pragmatic Dev baseada no inventário das árvores
`main` dos sete repositórios e leitura direcionada das fronteiras
`SafeRuntime`, `TaskPlanCoordinator`, `CdpStreamTap`, `HybridUiResponseReader`,
`UiChatExecutor`, `ui-dom` e contratos KAP/2.

## Cobertura verificável

A enumeração de blobs de código `*.py`, `*.js`, `*.ts`, `*.tsx`,
`*.rs` (excluindo diretórios de testes/fixtures) encontrou aproximadamente:

| Repositório | Arquivos de código inventariados | Maior hotspot de tamanho |
| --- | ---: | --- |
| kitt-agent-cli | 459 | `kitt/runtime/core_runtime.py` (~107 KiB antes da extração) |
| kitt-reverse-proxy | 117 | `src/runtime/agent-contract.ts` (~32 KiB) |
| kitt-protocol | 24 | `src/lib.rs` (~22 KiB) |
| kitt-memory | 13 | `crates/kitt-memory-sqlite/src/lib.rs` (~92 KiB) |
| kitt-toolbox | 10 | `crates/kitt-native-engine/src/symbols.rs` (~23 KiB) |
| kitt-assistant | 31 | `packages/kitt-assistant-runtime/kitt/daemon/server.py` (~89 KiB) |
| kitt-ai-workers | 19 | `kitt_workers/stt_server.py` (~28 KiB) |

Isto é um **inventário por tamanho**, não leitura de todas as funções ou
prova de defeito. O total não considera arquivos de teste e não valida
alcance de símbolos por reflexão, plugins ou subprocessos.

## Achados e decisões

**P1 — resposta web não recuperada (proxy, em tratamento).** Nos logs de
13/10 o prompt de 64.048 caracteres foi enviado; CDP relatou cinco POSTs
vistos/decodificados, uma correspondência parcial e nenhuma requisição
plenamente correlacionada; o DOM não forneceu nós identificados do assistente.
O texto concluído no navegador não foi entregue. Correção aplicada no
Proxy 5.3.1: considerar fragmentos consecutivos no mesmo array sem unir
turnos diferentes, e usar último turno estruturado e contrato válido como
fallback. CI simulada verde; aceitar a correção operacionalmente requer
reexecução na mesma família de página autenticada. Não mascarar com timeout
infinito, body text arbitrário ou aceitação de anchor parcial.

**P2 — concentração de responsabilidades (Agent).** O módulo
`kitt/runtime/core_runtime.py` tinha ~2.575 linhas com política,
autorização, catálogo e múltiplos adaptadores. A rotina `_op_plan`
acumulava despacho, admissão de subagentes e validação. Extraídas
~99 linhas para `kitt/runtime/plan_runtime.py`; o facade mantém a mesma
assinatura e invoca o mesmo `_op_registry_tool`. Novas funcionalidades
ficam em `read_batch.py` e `revision_refs.py`, evitando ampliar o GOD
class. O trecho `SafeRuntime.execute` continua amplo e deve ser
decomposto por fases só com cobertura dos gates de aprovação.

**P2 — métodos longos e estados acoplados (a investigar).** Agent
`kitt/core/turn_processor.py` (~69 KiB) e
`kitt/core/turn_tool_loop.py` (~53 KiB), Proxy
`src/runtime/ui-executor.ts` (~26 KiB, método `execute` iniciado
na linha 262 antes desta release), Assistant
`kitt/daemon/server.py` (~89 KiB) e Memory
`kitt-memory-sqlite/src/lib.rs` (~92 KiB) merecem análise
de fluxo/chamadores. O tamanho sozinho **não estabelece bug**
ou necessidade de remover código, principalmente em contratos públicos.

**Código morto.** A inspeção de árvore/assinaturas não confirmou com
segurança funções sem consumidores. Remoção global sem checar imports
dinâmicos, entry points, plugins e serialização seria regressiva.
**Status: não comprovado/não removido**. Não confundir esse levantamento
com auditoria exaustiva de símbolos.

## Critérios de aceitação e lacunas

- Refatoração específica e testes de leitura, referência, plano e CDP
  foram incorporados; exigir PR/CI verde no SHA exato da release.
- Sem reproduzir navegador autenticado não há evidência de eliminação da
  causa de captura original em produção.
- Falta uma análise de uso estática+dinâmica e testes de consumidor dos
  demais grandes módulos para concluir limpeza de código morto.
- O caminho de implementação pragmático é decompor **uma responsabilidade
  por vez**, preservar a autoridade do host e rejeitar abstrações sem uso.

Parecer: **sem bloqueador demonstrado nos métodos modificados cobertos por
testes**, condicionado à execução dos gates declarados; a auditoria
exaustiva dos sete repositórios e a captura em navegador real permanecem
inconclusivas. Não equivale a atestado de segurança total.
