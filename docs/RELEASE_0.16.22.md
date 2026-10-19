# KITT Ecosystem 0.16.22 — redução de turnos e contratos mais seguros

## Pins imutáveis do canal release

- **Agent CLI 0.88.18**: `e768fdfd92b8f5b255f38ccd337230e0a3e370a8` ([PR #122](https://github.com/rfdetoni/kitt-agent-cli/pull/122)).
- **Reverse Proxy 5.4.11**: `0b5cf52e3c5da10e918467739a139956dcc8ae06` ([PR #94](https://github.com/rfdetoni/kitt-reverse-proxy/pull/94)).
- Protocol, Memory, Toolbox, Assistant e AI Workers mantêm seus pins da versão 0.16.21; nenhuma alteração de protocolo compartilhado foi necessária.

## Entregas

### Agent CLI
- Extrai funções puras de identificação de chamadas, retorno de ferramentas, descoberta e telemetria do grande `turn_tool_loop.py` para `turn_tool_helpers.py`, preservando os consumidores.
- Evita repetir orientação genérica após cada retorno de ferramenta e bloqueia finalizações vazias do agent-loop.
- Corrige a geração dos schemas estruturados de ferramentas a partir do catálogo **efetivamente executado pelo SafeRuntime**, incluindo o `repo.batch_read` que já existia e é read-only, limitado a oito operações independentes sujeitas à política do host.
- Atualiza o `uv.lock` com a versão do projeto, sem alterar dependências desnecessariamente.

### Reverse Proxy
- Separa a validação estática de contratos de `agent-contract.ts`.
- Rejeita conclusão vazia e reparo de JSON que substitua argumentos inteiros quando o diagnóstico indicar um erro genérico.
- Atualiza `package.json`, `package-lock.json` e documentação sem churn de dependências.

## Validação e limitações

Os pipelines de CI do Reverse Proxy (verificação e Docker) e do Agent CLI (contratos críticos, regressões, smoke Windows, Docker e Podman) devem estar aprovados antes de promover os pins. Os testes que protegem execução, permissões, contrato e retomada foram preservados; apenas regressões críticas novas foram adicionadas.

As otimizações visam reduzir chamadas redundantes ao modelo; a redução real de duração/tokens no Gemini Web autenticado **não foi medida nesta release**. Não presumir que um teste de CI reproduza latência de um serviço web ao vivo. O instalador lê os hashes de `ecosystem.release.json`; não usa SHAs de branches móveis.
