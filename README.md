# K.I.T.T. — Ecossistema

Instalador e manifesto de versões do ecossistema K.I.T.T. A versão atual do canal release é **0.16.61**.

## Instalação

O entrypoint do instalador é [`install.sh`](install.sh). Consulte as opções e os pré-requisitos no script e na documentação correspondente antes de instalar ou reinstalar componentes.

**Dica (Ubuntu/Linux):** se o KITT indicar `Strong sandbox profile ... requires functional bubblewrap >= 0.12` ou `bwrap: setting up uid map: Permission denied`, consulte [Diagnóstico do Bubblewrap e AppArmor](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/BUBBLEWRAP_APPARMOR.md). A configuração do perfil AppArmor deve corresponder ao executável realmente utilizado; não desative a restrição de namespaces globalmente.

## Sandbox autônomo

O Agent CLI 0.88.94 aceita comandos de desenvolvimento via `sandbox.run` e
roteia `process.run` automaticamente para um executor isolado quando o workspace
está no modo `autonomous` e dispõe das capacidades `process.run` e `repo.write`.
O instalador Linux prepara a imagem Docker do Agent CLI se houver Docker funcional;
caso contrário, o runtime usa Bubblewrap funcional (>=0.12). Nenhuma execução
não isolada é autorizada como fallback.

A preparação Docker cobre o **Agent nativo** que acessa o daemon do host. O
serviço Agent no Compose não monta o socket Docker e não possui um broker remoto
nesta versão; não se deve prometer execução autônoma de shell nesse modo até
haver um executor isolado dedicado. Rede requer `network.access` delegado.

## Componentes e versões

O arquivo [`ecosystem.release.json`](ecosystem.release.json) fixa os commits do Agent CLI, Reverse Proxy, Protocol, Memory, Toolbox, Assistant e AI Workers para instalações reproduzíveis.

## Reverse Engineering Clean-Room

A release inclui validação de contratos de caixa-preta, revisão assinada e pipeline offline em ambiente OCI isolado. **O código gerado ainda exige validação diferencial real com o Windows Oracle; CI verde não significa certificação Clean-Room.**

- [Fluxo e controles do RE Clean-Room](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/CLEANROOM_RE.md)
- [Notas técnicas da versão 0.16.61](docs/RELEASE_0.16.61.md)

## Histórico

Todas as mudanças de versões ficam em [`CHANGELOG.md`](CHANGELOG.md). Os detalhes técnicos de cada entrega ficam em `docs/RELEASE_*.md`.
