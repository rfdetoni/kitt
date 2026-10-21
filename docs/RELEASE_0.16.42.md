# KITT Ecosystem 0.16.42 — correções de runtime (2026-10-21)

## Componentes atualizados

- **Agent CLI 0.88.41:** parser SEARCH/REPLACE mantém o caminho explícito por arquivo; versões como `11.20` não se tornam caminhos. `repo.batch_read` informa falhas por ID com resultados parciais preservados. Orçamento padrão de chamadas de ferramentas por turno passa de 24 para 64, mantendo limites de tempo/modelo e isolamento. Instruções de `handles.resolve` e prevenção de releituras redundantes mais claras.
- **Reverse Proxy 5.4.18:** admissão excepcional de uma sessão nomeada sob pressão de memória passa a depender do RSS capturado na inicialização + até 512 MiB, ou do orçamento configurado, o que for maior. O evento de admissão relata o baseline e o headroom. O limite não impede crescimento de memória em sessões existentes; não é uma correção comprovada de vazamento Chromium.

## Segurança e verificação

As correções não removem políticas de autorização, sandbox, isolamento por workspace, verificação de mudanças, limite de recursos nem validação de contratos. PRs devem passar no CI de seus componentes antes de atualizar o manifesto de SHAs, para preservar a instalação reproduzível. O Windows guest Oracle e testes diferenciais de DLLs permanecem independentes.

## Instalação

`install.sh` usa os SHAs de `ecosystem.release.json` no canal de release. Reinstale ou atualize os módulos com o instalador, conforme o modo de instalação. Não substitua os pins por versões presumidas; confira o manifesto.
