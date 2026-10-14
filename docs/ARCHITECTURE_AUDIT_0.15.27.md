# Auditoria KITT 0.15.27 — inventário integral e achados confirmados

Data de referência: 2026-10-13/14. Metodologia Pragmatic Dev, separados achados comprovados de suspeitas.

## Escopo executado

O workflow `ecosystem-source-audit` verifica os sete repositórios na sua
`main`, arquiva os SHAs em `source-commits.txt` e gera dois artefatos:
`inventory.json` com todos os símbolos/arquivos encontrados e `report.md`
com classificação inicial. Python passa por AST; TypeScript, JavaScript e
Rust passam por triagem lexical. Isso é um inventário *integral de arquivos*,
não uma prova estática+dinâmica de reachability de todos os símbolos.

Resultado do primeiro run aprovado (CI run 38490509902): **816 arquivos**,
**0 erros** de leitura/parsing, **26 candidatos** por concentração de classe,
**146 candidatos** por função longa/complexa e **11 privados** com uma
ocorrência lexical. A composição posterior da release pode variar: usar os
artefatos e hashes gerados pelo workflow para qualquer comparação futura.

| Repositório | Arquivos-fonte lidos | Linhas aproximadas |
|---|---:|---:|
| kitt-agent-cli | 534 | 108301 |
| kitt-reverse-proxy | 155 | 24953 |
| kitt-protocol | 33 | 5564 |
| kitt-memory | 18 | 7973 |
| kitt-toolbox | 10 | 2607 |
| kitt-assistant | 41 | 15375 |
| kitt-ai-workers | 25 | 3687 |

**Não somar candidatos como defeitos.** A contagem cobre diretórios de testes,
rotas públicas, módulos e entrypoints. Os identificadores possuem graus
diferentes de importância/autoridade.

## Achados e correções confirmados

**P2 — helpers privados redundantes no Agent CLI.** Três símbolos do
inventário possuem uma ocorrência lexical, não são rotas nem exports:
`kitt/llm/providers/kitt_reverse_proxy.py::_proxy_error_message`,
`kitt/llm/kitt_proxy_capabilities.py::_range` e
`kitt/llm/client.py::_normalize_reasoning_effort`.
Foram removidos no PR Agent #96 e correção de lock no PR #97; testes de contrato e Docker
passaram no SHA do PR. Permissões, schemas e adaptadores mantêm as
assinaturas públicas. Isso confirma ausência de consumidor *estático
dentro da árvore analisada*, não prova ausência de import externo.

**P2 — método brain parcialmente decomposto.** No Agent,
`KittReverseProxyAdapter.stream` continha também a negociação de headers
HTTP. O bloco de preparação e validação da versão foi separado em
`_proxy_request_headers`, com rejeição de duplicatas e falta de
acknowledgment, protegida por testes. O processamento principal SSE
continua longo: a extração **não** encerra sua refatoração.

**P1 — compatibilidade de contratos e proveniência de respostas web.**
Protocol 0.13.2 centraliza a seleção exata `X-Kitt-KAP`;
Agent 0.87.9 confirma a seleção; Proxy 5.3.3 disputa CDP tap e DOM como observers independentes,
validando KAP/2 completo e turno atual antes de concluir logicamente a espera. Não confundir marcador
`K2/END` solto com resposta válida, não executar ações do modelo sem host,
não abortar o navegador, não permitir downgrade silencioso.

## Hotspots P2 priorizados, ainda não refatorados

1. Agent: `kitt/runtime/core_runtime.py`, classe `SafeRuntime`
   com ~2137 linhas. Dividir o preflight de política e autorização de
   `SafeRuntime.execute` (~385 linhas) preservando grants de uso único
   e capacidades; ampliar regressões antes de extrair.
2. Assistant: `packages/kitt-assistant-runtime/kitt/daemon/server.py`,
   classe `DaemonServer` ~1988 linhas e `_handle_client` ~566 linhas.
   Isolar dispatch de RPC, preservando autenticação/revogação e ordem de eventos.
3. Agent: `kitt/core/turn_processor.py`, `TurnProcessor` ~1503
   linhas; `kitt/core/turn_tool_loop.py::_execute_tool_loop_core`
   ~899 linhas. Extrair somente fases com fronteiras comprovadas
   (planejamento, preflight, execução, validação, receipts) sem deslocar
   autoridade do host.
4. Agent: `kitt/tools/registry_core.py::ToolRegistry.execute_tool`
   ~446 linhas. Analisar coordenador de mutações, aprovação e replay.
5. Memory: `apps/kitt-memoryd/src/manage.rs::handle` ~426 linhas
   e `crates/kitt-memory-sqlite/src/lib.rs::migrate` ~230 linhas.
   Refatorar por handlers transacionais, após testes de migração compatíveis.
6. Proxy: `src/runtime/ui-executor.ts::UiChatExecutor` ~504 linhas;
   tocar captura/seleção de DOM só com regressões CDP/Chromium reais.
7. Toolbox e AI Workers: inventário foi concluído, sem evidência suficiente
   de um defeito por tamanho ou de código morto que justifique remoção.

## Símbolos não removidos automaticamente

Outros oito símbolos com referência lexical única foram preservados:
`RepositoryIndex._file_hash`, `_index_modules`, `_module_rows`,
`_rebuild_reference_edges`, `CredentialStore._write_atomic`,
`_with_retry`, `ApprovalManager._requests` e
`PostEditValidator._external`. Alguns são wrappers intencionais de lock
ou compatibilidade; a remoção exige mapear imports, plugin discovery,
reflection, testes externos e runtime. A auditoria não encontrou
prova suficiente para apagar esses símbolos.

## Segurança e critérios de encerramento

- Um envelope KAP, cabeçalho ou conteúdo de arquivo nunca atribui
  autoridade; validação e aprovação permanecem no host.
- Early completion requer um vencedor válido (CDP com requisição
  correlacionada, payload único, completo e estável; ou DOM com resposta
  completa, estável e pertencente ao novo turno do assistente).
  O outro observer não bloqueia a conclusão. **Não** encerra a geração
  upstream nem autoriza tools por texto do modelo.
- Gate aceito: Protocol CI, Agent PR Checks + Docker, Proxy CI + Docker,
  root ecosystem-main + ecosystem-integration na mesma composição.
- A sessão ChatGPT Web autenticada do incidente original continua
  dependente de reprodução operacional; CI não prova sucesso em produção.
- "Auditoria exaustiva de código morto" entendida como demonstração de
  reachability de *todos* os símbolos ainda **não está concluída**.
  O scanner cobre todos os arquivos acessíveis, mas não importa/invoca
  cada runtime nem segue todos os consumers dinâmicos.
- **Não** marcar todos os 26/146 hotspots como corrigidos com base em uma
  classificação automatizada. Criar correções pequenas, com teste de
  comportamento e revisão dos consumidores, em commits específicos.

Parecer: inventário completo e correções dirigidas verificáveis;
refatoração integral e prova global de ausência de código morto **pendentes**.
