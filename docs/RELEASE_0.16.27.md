# K.I.T.T. Ecosystem 0.16.27 — allow-all por workspace

## Revisões fixadas no manifesto release

- Agent CLI 0.88.23: `fa1ab23e9bbdb497f945517813d9aa9e06649f66` (PR [#129](https://github.com/rfdetoni/kitt-agent-cli/pull/129)).
- Assistant Runtime 0.4.17: `f332320d3ed092c6daa99ed2697c9277b94af021` (PR [#56](https://github.com/rfdetoni/kitt-assistant/pull/56)).
- Protocol, Memory, Toolbox, AI Workers e Reverse Proxy: pins anteriores mantidos.

## Comportamento

O perfil `autonomous` é o padrão para workspaces novos. O usuário pode escolher `supervised` (perguntar) ou `read_only` (bloquear ações de escrita/execução) no menu de autonomia, persistindo suas escolhas.

No modal de aprovação, `A` concede a ação pendente e ativa o modo autônomo no workspace para ações futuras; `w` mantém a aprovação lembrada somente para a ferramenta escolhida; `s` limita a lembrança à sessão. A ordem preserva o snapshot da autoridade da ação pendente.

`allow-all` não revoga restrições de escopo, capacidades, rede, sistema hospedeiro, isolamento nem proibições explícitas do operador. Comandos automáticos no host podem falhar se não houver sandbox forte disponível. Isso é um bloqueio de ambiente, não uma autorização humana pendente. As VMs seguem os limites de identidade e canal autenticado.

## Verificações

- CI das PRs Agent CLI #129 e Assistant #56: concluído com sucesso.
- Verificação final do manifesto `ecosystem.release.json`: os sete SHAs apontam para os componentes esperados; `VERSION` e `ecosystem_version` devem coincidir.
- Fluxo de instalação release usa o manifesto de SHAs imutáveis. Testes de integração do instalador e CI da PR do ecossistema devem passar antes da promoção.
