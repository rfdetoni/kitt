# KITT 0.16.72 — verificação Python pronta no host

## Causa

Nos logs de 28/10/2026, a validação independente do trabalho de engenharia
reversa do ELF `2.1.308` exigiu `python.lint`, mas o Ruff não existia no
ambiente virtual instalado. A tentativa do modelo de executar `pip install`
durante o turno foi bloqueada corretamente por ausência de `network.access`.
Buscas globais em `/opt/containerd` e invocações diretas de Docker/Podman
também falharam no sandbox por acesso ao host intencionalmente isolado.

## Correções

- O instalador do KITT provisiona Ruff `0.14.3` no venv do Agent CLI **antes**
  de iniciar a sessão e exige que `ruff --version` funcione no smoke.
- O Agent CLI `0.89.8` resolve o executável no próprio venv mesmo quando
  o diretório de scripts não está no `PATH`.
- Um check obrigatório `python.lint` com alvo somente Markdown executa
  `ruff check .` se o workspace contém fontes Python. Não é marcado como
  aprovado quando o verificador não existe ou falha.
- Falhas de Docker sem socket, Podman ausente e `find` fora do workspace
  retornam diagnósticos específicos e `retry_same_command=false`; o socket
  do host nunca é exposto ao processo arbitrário.
- Todas as demais revisões imutáveis do ecossistema permanecem fixadas.

## Validação

As alterações foram submetidas à CI de contratos do Agent CLI, Docker e
instalação integrada do ecossistema. O instalador também testa a presença do
binário Ruff. A análise estática do ELF continua sem executar o original.

## Instalação

Reexecute o instalador habitual `--preset full --channel edge`, incluindo
suas opções de REA, Docker RE lab e VMs. O canal `release` usa os SHAs
fixados no `ecosystem.release.json`; o canal `edge` acompanha a main.
