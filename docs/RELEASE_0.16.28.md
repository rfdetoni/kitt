# K.I.T.T. Ecosystem 0.16.28 — planejamento e sandbox

## Pins imutáveis

- Agent CLI 0.88.24: `58ffe92a3e6322e47f3b5fa797cbc19851c04702` ([PR #130](https://github.com/rfdetoni/kitt-agent-cli/pull/130)).
- Assistant Runtime 0.4.18: `1beeeb56dc649df2223f80439604368eb721d48e` ([PR #57](https://github.com/rfdetoni/kitt-assistant/pull/57)).
- Protocol, Memory, Toolbox, AI Workers e Reverse Proxy permanecem nas revisões anteriores do manifesto release.

## Diagnósticos dos logs de 20/10/2026

O atalho A fez o daemon receber `runtime.set_autonomy`, e as ações seguintes foram aceitas pelo `PolicyEngine` como `autonomous`. Comandos `process.run` falharam por não existir Bubblewrap forte e funcional (>= 0.12), não por falta de permissão do usuário.

Os erros de `plan.submit` ocorreram porque chamadas com `arguments.tasks` não incluíam a estrutura exigida `arguments.proposal`; um plano curto foi rejeitado pela mesma razão. `plan.verify` foi chamado sem plano previamente submetido. A correção explica esses contratos diretamente no prompt e no retorno da operação, reduzindo retries inválidos.

O budget de execução continua independente da preferência de autonomia. A execução automática de comandos diretamente no host permanece bloqueada na ausência de sandbox obrigatório; execução em VM autenticada exige sua própria política de isolamento e autoridade.

## Validação

- Agent CLI #130: CI, regressões, smoke Windows, Docker e Podman passaram.
- Assistant #57: Python Runtime, Rust, HUD e testes de ciclo de vida em Linux/macOS/Windows passaram.
- Manifesto release deve ser validado por instalação ponta a ponta com SHAs imutáveis antes do merge.
