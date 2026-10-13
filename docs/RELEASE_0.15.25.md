# KITT 0.15.25 — operações KAP/2 no host e captura ChatGPT Web

## Versões e SHAs imutáveis

- Root: **0.15.25** (pins em `ecosystem.release.json`).
- Agent CLI: **0.87.6**, com implementação de operações avançadas em cima do K2 T `kitt_runtime`.
- Reverse Proxy: **5.3.1**, com regressões de prompts grandes e recuperação estrutural de resposta já concluída.
- Protocol: **0.13.1**; Assistant Native **0.1.40** / Runtime **0.3.20**; Workers **0.1.60** (sem alterações).
- Os demais módulos continuam nos commits imutáveis declarados pelo manifesto.

## Implementado

1. **Lote de leitura somente leitura**: `repo.batch_read` aceita até oito consultas independentes, até quatro workers, validação por operação, IDs de correlação e limites de resposta.
2. **Argumentos posicionais com contrato fixo**: tabelas `calls[n]{id,operation,path}` exigem o SHA-256 da ordem definida pelo host; valores/esquemas inventados são rejeitados.
3. **Referências e recibos de revisão**: `repo.ref.create/read/write` com token por conversa, TTL, SHA-256, compare-and-swap no filesystem, caminhos explícitos para PolicyEngine, proteção contra replay.
4. **Planos diferenciais**: `plan.patch` usa `expected_revision`, valida dependências/permissões, altera apenas PENDING sem child lease e grava eventos com IDs determinísticos para rejeitar commits conflitantes.
5. **Descoberta de capacidades**: `kap.capabilities` relata precisamente os recursos ativos e os que não estão ativos.
6. **Captura ChatGPT Web**: o tap CDP verifica as mesmas três âncoras em arrays de fragmentos consecutivos do corpo da requisição; fallback estrutural estrito seleciona somente o último turno com conteúdo de assistente, rejeita prompt, mensagens anteriores e envelopes ambíguos. Adicionada telemetria por contagens e testes.
7. **Manutenibilidade**: `_op_plan`, aproximadamente 99 linhas de despacho e verificação, foi extraído de `core_runtime.py` para `kitt/runtime/plan_runtime.py`, sem mudar a assinatura pública nem relaxar as políticas. Confira a [auditoria de escopo](ARCHITECTURE_AUDIT_0.15.25.md).

## Segurança, aceitação e limites

Os recursos host usam o KAP/2 existente em um **único** `K2 T` por turno. Não existe um comando `K2 B` no parser, nem autorização vinda do envelope textual; os subcalls são tratados no Agent, sob as políticas originais.

**Não ativados**: negociação cross-transport para novo cabeçalho `K2/n` e interrupção antecipada da geração ao detectar `K2/END` antes de o transporte confirmar fim. Ambos exigem desenho, revisão de replay/ambiguidade e implantação coordenada; o endpoint de introspecção explicita `false` em vez de fingir suporte.

**Captura em navegador real**: os testes simulados no CI exercitam os casos observados, mas não conseguem reproduzir a sessão logada do usuário de 13/10/2026. A validação operacional precisa observar a próxima execução com Proxy 5.3.1. Não é correto declarar a ocorrência original definitivamente resolvida apenas por green CI.

**Auditoria arquitetural**: foi realizado inventário dos sete repositórios e revisão dirigida dos hotspots. Isso não constitui uma prova global de ausência de código morto ou subclasses desnecessárias. Nenhum símbolo sem uso foi removido sem rastreamento de consumidores.

## Gates de publicação

Promover somente após CI Agent CLI no SHA `3fe9a87`, CI Proxy no SHA `1390759`, `ecosystem-main` e `ecosystem-integration` na raiz para o mesmo HEAD, além da publicação automática do tag `v0.15.25`. Resultados de SHAs antigos não validam a composição nova.

Benchmarks fora de escopo, conforme solicitação anterior.
