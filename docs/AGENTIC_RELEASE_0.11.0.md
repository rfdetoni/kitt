# KITT 0.11.0 — melhorias do loop e da orquestração

## Resultado implementado

O Agent passa a aceitar planos opcionais de tarefas com dependências, UUIDs atribuídos pelo host, escopo limitado, estados persistidos e verificações registradas. A delegação reutiliza o gerenciador de filhos existente. O Proxy consome fatos estruturados do host para decidir se uma resposta final pode encerrar o loop. Os três componentes preservam a autoridade de política/aprovação no Agent e o transporte estrutural-only.

O trabalho prioriza correções de segurança e controle de execução antes de acrescentar automação de planejamento. Não acrescenta uma chamada obrigatória de planner nem um segundo motor de workflows. Tarefas independentes podem usar os limites existentes de filhos simultâneos, mediante chamadas explícitas de dispatch.

## Composição publicada

| Repositório | Versão | SHA da implementação / baseline |
| --- | --- | --- |
| [Agent CLI](https://github.com/rfdetoni/kitt-agent-cli) | **0.82.0** | `f094d7e8c5d8a75b97a27d45ffd44d4383912b9d` |
| [Reverse Proxy](https://github.com/rfdetoni/kitt-reverse-proxy) | **4.8.0** | `3991849a89b6d0b535d1b014c4248cd51c6247ca` |
| [Protocol](https://github.com/rfdetoni/kitt-protocol) | **0.7.0** | `23bb4d12ec006b534776fe51ec1fef9753d1ff0c` |
| [Memory](https://github.com/rfdetoni/kitt-memory) | 0.7.0 | `084b1bb698403b3c746a0f9d69ef2a1e498ae788` |
| [Toolbox](https://github.com/rfdetoni/kitt-toolbox) | 0.2.9 | `bf58cfa5b9ae9b8ab8a4231184cee2619e9546f2` |
| [AI Workers](https://github.com/rfdetoni/kitt-ai-workers) | 0.1.40 | `96b2437acf28fec33ffde2bc285ca3233d9c30df` |
| [Assistant](https://github.com/rfdetoni/kitt-assistant) | 0.1.15 / runtime 0.2.27 | `3ef5074da04e934b33e93a33ab09a3dbd02a7da3` |
| [Distribuição](https://github.com/rfdetoni/kitt) | **0.11.0** | Commit que contém este documento |

Os quatro componentes alterados receberam bump. Memory, Toolbox, Workers e Assistant não tiveram mudanças artificiais de código ou versão. A tabela registra a composição avaliada; o instalador continua seguindo `main` e resolvendo SHAs por execução. Instalações existentes devem atualizar Agent, Protocol e Proxy juntos. O Agent oferece erro de incompatibilidade quando a descoberta de capabilities identifica um Proxy sem `host_execution_state_v1`.

## Mudanças por responsabilidade

| Área | Implementação | Garantia / limite |
| --- | --- | --- |
| Decomposição | `plan.submit/inspect/next/checkpoint`, DAG persistido no EventLedger | Um plano por turno; até 12 tarefas, 32 KiB, 64 arquivos concretos e 24 checks distintos |
| Delegação | `plan.dispatch` pelo child manager existente; linhagem task/parent/request | Política e leases existentes; filhos leaf; papéis intersectam capacidades do pai |
| Maker/checker | `plan.verify`, checks do BuildDetector, sintaxe e digests | Até 3 tentativas; check ausente não aprova; resultado do filho exige verificação do workspace integrado |
| Conclusão | `HostExecutionState` e evidência de ferramentas com escopo | Texto do modelo/stdout não atesta sucesso; todos os efeitos pendentes e tarefas devem ser verificados |
| Checkpoints | Checkpoint proativo no Agent; cadence antecipada para budgets maiores no Proxy | Não reinicia orçamento global; repetição de falhas bloqueia loops sem progresso |
| Ciclo de filhos | Admissão e transições serializadas, timeouts finitos limitados pela lease, cancelamento de tokens/processos | Cancelamento terminal não pode ser sobrescrito por resultado tardio |
| Perda abrupta do pai | Watchdog POSIX com cleanup e saída limitada | Testado com pai/worker/comando reais; Job Objects Windows continuam pendentes |
| Rollback | Digests e precondições antes de restaurar snapshot | Preserva alterações mais novas e reporta conflito |
| Aprovação | Pausa de duração ativa enquanto aguarda decisão | Consumo de ferramentas/modelo/tokens/custos permanece contabilizado |
| Contratos | Proposal, report, verification status e host facts em Python/Rust/TypeScript; `agent_role`, `parent_request_id`, `task_id` opcionais | Papéis existentes `DISCOVER/ARCHITECT/IMPLEMENT/VERIFY/REVIEW`; schemas, fixtures e paridade de campos |
| Proxy | Validação de contexto host único, confiável e correlacionado; capabilities de features/limites | Gateway não possui DAG, memória, leases ou autoridade de execução |
| Observabilidade | `kitt sessions --json` deriva métricas do ledger | Revisão, contagem/profundidade do plano, verified, checkpoints, spawn/reports e tentativas por tarefa |
| Distribuição | Versões/documentação atualizadas; integração executa pytest completo e smoke de contratos | Mantém composição de namespaces e resolução main-first |

Processos genéricos têm efeitos de escopo desconhecido; checagens de um arquivo não os validam. Checks registrados de workspace podem liberar a pendência. Verificação sintática comprova sintaxe, não cobertura semântica do objetivo. Digests cobrem os arquivos declarados; snapshots reproduzíveis de ambiente e dependências permanecem fora deste incremento.

## Correções e validação

A revisão agressiva de autoridade, concorrência, recursos e integridade encontrou e corrigiu: delegação por filhos, corrida na admissão/registro de processo, ressurgimento após cancelamento, comandos iniciados com token cancelado, processo de ferramenta sobrevivendo à perda do pai, rollback sobre conteúdo mais novo, conclusão por stdout ou checagem de escopo diferente, sucesso aparente com runner indisponível e orçamento consumido pelo tempo de aprovação humana.

A revisão detalha severidade, confiança, localização, impacto, correção e validação em [AGENTIC_PLANNING.md](https://github.com/rfdetoni/kitt-agent-cli/blob/f094d7e8c5d8a75b97a27d45ffd44d4383912b9d/docs/AGENTIC_PLANNING.md).

| Validação | Evidência |
| --- | --- |
| Agent local | **1.316 passed, 5 skipped, 1 deselected, 64 subtests**; Python 3.14, Memory daemon compilado e namespace Assistant |
| Agent estático | compileall; guard clean-room; ruff crítico; mypy em 18 fronteiras: sucesso |
| Processo real | Pai encerrado abruptamente; worker cancela comando antes da mutação atrasada; teste POSIX |
| Proxy local | **363 passed**, build TypeScript e verify |
| Protocol | Testes Rust/Python, fmt, Clippy, schemas/fixtures e paridade SDK; Python: **11 passed** |
| Distribuição local | **77 testes**; política main-first; arquitetura; sintaxe shell; smoke Agent/Protocol |
| Protocol CI | [run 36917879444](https://github.com/rfdetoni/kitt-protocol/actions/runs/36917879444), sucesso; release automática [run 36917938932](https://github.com/rfdetoni/kitt-protocol/actions/runs/36917938932), sucesso |
| Proxy CI | [run 36919719287](https://github.com/rfdetoni/kitt-reverse-proxy/actions/runs/36919719287), sucesso |
| Agent CI do SHA | [run 36919814855](https://github.com/rfdetoni/kitt-agent-cli/actions/runs/36919814855) |
| Integração da distribuição | [Actions ecosystem-integration](https://github.com/rfdetoni/kitt/actions/workflows/ecosystem-integration.yml); resolve SHAs por run e valida componentes e instalação |

O único teste excluído localmente é `TestExtensionLoader.test_default_plugin_runs_in_worker_and_proxies_registered_tool`: o ambiente de autoria proíbe criar socket AF_UNIX. Não foi enfraquecido nem desativado no repositório; a CI executa a suíte completa. Testes agora bloqueiam HTTP externo real, e a construção do catálogo usa cache/builtins sem refresh automático; atualização explícita do catálogo continua disponível.

Os links de CI identificam a execução do SHA. Uma execução em andamento ou uma lista vazia de commit statuses não constitui aprovação. Builds de containers e testes de integração não substituem provider autenticado.

## Matriz E2E e itens adiados

Os **30 requisitos permanecem PENDING** em [AGENTIC_RUNTIME_ACCEPTANCE.md](https://github.com/rfdetoni/kitt-agent-cli/blob/f094d7e8c5d8a75b97a27d45ffd44d4383912b9d/docs/AGENTIC_RUNTIME_ACCEPTANCE.md). Faltam os registros prescritos com provider real autenticado, SHA, workflow/run ID e logs. A implementação e os testes de regressão não foram apresentados como esses registros.

Próximas validações prioritárias: #1 ContextEnvelope/provider lowering, #7 replay sem repetir efeito, #8 Ctrl+C seguido de novo prompt e #14 controle de processo com AuthoritySnapshot original. Para cada gate, preservar o log real e só então alterar seu status.

| Proposta original | Decisão neste incremento | Condição para ampliar |
| --- | --- | --- |
| `DECOMPOSE` obrigatório / rota `PLANNER` | Plano opcional e papéis existentes | Evidência de benefício de custo/latência e cobertura do objetivo |
| Novo `OrchestratorAgent` / fila autônoma | Host coordinator fino + child manager existente | Scheduler durável com invariantes de crash/admissão/leases |
| Default de timeout 30 min / nova env | Timeout atual, positivo/finito, limitado pela lease | Necessidade operacional medida; evitar configuração duplicada |
| Retry automático após timeout | Task BLOCKED, decisão explícita do host | Reconciliação de efeitos e idempotência antes de relançar |
| Cache do DAG entre turnos | Planos pertencem ao turno | Protocolo de continuação com invalidação por objetivo/escopo/evidência |
| Heartbeat/reattach via Proxy | Adiado | Lease e reconciliação pertencentes ao host; Proxy permanece transporte |
| Comunicação direta entre filhos | Não acrescentada ao plano | Reports agregados pelo host evitam dependência lateral |
| Garantia após hard kill no Windows | Adiada | Job Objects e teste real de processo/árvore |
| Roteamento forte/barato por role | Role correlacionada no metadata; não impõe modelo | Política de custo validada por capacidades e benchmarks |

Esses limites são parte explícita da release, não funcionalidades declaradas concluídas.
