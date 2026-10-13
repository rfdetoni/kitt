# KITT 0.15.10 — Snapshot de VM e atualização do Reverse Proxy

## Componentes da release

- **KITT Agent CLI 0.86.13** — corrige a validação do estado UEFI/TPM ao criar e restaurar snapshots de VMs QEMU em Docker/Podman. Rejeita links simbólicos e tipos de arquivo inesperados, inclusive antes de substituir o disco durante uma restauração. A PR [Agent #94](https://github.com/rfdetoni/kitt-agent-cli/pull/94) passou nas pipelines do Agent.
- **Reverse Proxy 5.1.2** — atualiza o pin imutável da release de 5.1.1 para 5.1.2, incluindo a recuperação fail-closed de respostas Gemini FINAL interrompidas, sem confiar em rascunhos conflitantes.
- **Assistant runtime 0.3.10** — permanece na revisão já validada. A faixa declarada de dependência `kitt-agent-cli>=0.86.12,<0.87` inclui 0.86.13; não há necessidade de republicação sem alteração no Assistant.
- **KITT instalador 0.15.10** — atualiza as revisões imutáveis no `ecosystem.release.json` e retorna código de erro quando a instalação solicitada de REA ou o download de imagens QEMU/toolbox falha, sem ocultar uma instalação parcial dos módulos principais. Protocol, Memory, Toolbox e AI Workers permanecem fixados nos commits anteriores.

## Escopo preservado

- O preset `full` mantém REA 6.4.0 opcional para o Agent normal, com opção de não instalar via `--skip-rea`.
- As imagens Linux RE em Docker/Podman seguem nas tags **0.86.10**: não houve alteração de Dockerfile nem rebuild necessário para a correção Python de snapshots.
- O Agent de programação normal não ativa automaticamente VMs, REA nem execução de binários não confiáveis.

## Validação

- A PR do Agent executou com sucesso `PR Checks` e `Docker`, incluindo os testes de regressão de snapshot.
- O workflow de integração do ecossistema deve verificar a instalação `release` com os novos SHAs, o isolamento das dependências e os contratos entre Agent, Assistant, Protocol e Proxy.
- **Pendente em infraestrutura externa:** execução de laboratório de engenharia reversa entre guests Windows/Linux e contêineres QEMU em host real com Podman, KVM e as imagens do operador.

A correção impede a cópia de symlinks em estado normal e detecta snapshots adulterados antes da troca do disco. Não promete atomicidade transacional entre disco, UEFI e TPM em falhas de hardware ou concorrência externa maliciosa na pasta de estado.
