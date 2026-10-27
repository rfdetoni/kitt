# KITT 0.16.68 — Reverse Proxy local e ambiente RE

## Componentes

- Agent CLI `0.89.5`, pin `7ab87087f321f2f13ef4207d6573ed12a303ae3b`, atualizado em `main`.
- Reverse Proxy `5.4.27`, pin anterior `6d3a1910c0df1163d926bb6f90fb6cc16c651fa3` (sem mudança nesta release).
- Outros módulos preservam SHAs existentes no `ecosystem.release.json`; o lock Python do Agent CLI foi sincronizado na respectiva release.

## Correções

- Prontidão do proxy local consultada via `/healthz` antes do primeiro POST; espera limitada a 30s, com cancelamento.
- Refresh explícito do cache de descoberta de capabilities quando o endpoint local responde.
- Sem retry automático de solicitações potencialmente submetidas a WebChat.
- Conteúdo sensível de conversas não é registrado por padrão nas instâncias do Reverse Proxy gerenciadas pelo Agent, mesmo no log TRACE.
- Mensagem do fluxo de ferramentas diferencia `flow.execute` (somente leitura) de `process.run` governado.
- A validação Python com fallback `unittest` já existia no Agent CLI e não foi reimplementada.

## Instalação e verificação

O `README.md` fornece o comando completo `curl | sh` para a instalação completa do laboratório RE. O `--with-re-lab` exige `--preset full`, Docker Engine com KVM/TUN e consentimento de licença do Windows. REA 6.4.0 é incluído por `--with-rea`. `--vm-pull-images` exige `--with-vm-containers`. A configuração inicial do Windows pode continuar no estado `PROVISIONING`; isso não equivale à validação do Oracle.

Após a instalação, use `kitt re lab status --json` e `kitt re lab verify --full`. A validação completa requer um Windows já instalado, inicializado e acessível pelos checks.

## Evidência de validação

O PR do Agent CLI [#198](https://github.com/rfdetoni/kitt-agent-cli/pull/198) passou pelos workflows `PR Checks` e `Docker`, incluindo testes de contratos e jobs com runtime Docker/Podman e smoke de empacotamento Windows. A atualização do manifesto é validada por CI do repositório instalador antes da publicação da release.

## Escopo

Nenhuma modificação do binário 2.1.308 e nenhuma execução do laboratório RE na máquina do usuário foram realizadas nesta release; o instalador somente prepara o ambiente no host em que for invocado.
