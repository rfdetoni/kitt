# KITT Ecosystem 0.16.23 — function calling nativo e seguro

## Component pins
- **Agent CLI 0.88.19**, `dc625e53ea580f409aec9aceff891936a7cdade9` ([PR #124](https://github.com/rfdetoni/kitt-agent-cli/pull/124)).
- **Reverse Proxy 5.4.13**, `82c4c5931e9170b5d12d1af9948596e49fb470c3` ([PR #97](https://github.com/rfdetoni/kitt-reverse-proxy/pull/97), que inclui [PR #96](https://github.com/rfdetoni/kitt-reverse-proxy/pull/96)).
- Os demais componentes conservam os pins do manifesto 0.16.22.

## Comportamento
- Contrato Agent v5 permanece ativo. Provedores de rede que explicitamente anunciam ferramentas nativas podem receber os schemas mesmo quando `parallel_tool_calls=false`. O CLI e o Proxy não permitem mais de uma chamada por turno; autorizações, schema e limites permanecem no host.
- Provedores WebChat usam um único envelope explícito `<tool_call>`; a captura DOM preserva delimitadores e impede transformar o conteúdo do envelope em resposta final. Respostas finais continuam JSON.
- O agent-loop do CLI só executa ações canônicas completas. Exemplo de comando em prosa ou markdown não é uma tool call.
- `repo.batch_read` já permite até oito leituras independentes e autorizadas por chamada; não há suporte para paralelismo arbitrário de mutações.

## Validação e limites
Os workflows CI e Docker de cada componente foram aprovados antes de fixar os SHAs. A integração HTTP nativa foi exercitada com provedor/lease simulados em testes de regressão; os workflows `ecosystem-main` e `ecosystem-integration` verificam os pins, compilação e instalação, mas **não** demonstram ganho de latência em WebChat autenticado.

Para medir empiricamente, use workload pareado antes/depois com prompts, provedor, contexto e permissões equivalentes, capturando `chat.timing`, `agent.contract.validation.detail`, `tool_loop.discovery_metric` e contadores de tokens reportados pelo provedor. Não declare percentuais de melhoria com base somente em bytes ou no tempo de parser.
