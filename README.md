# K.I.T.T. — Ecossistema

Instalador e manifesto de versões do ecossistema K.I.T.T. A versão atual do canal release é **0.16.30**.

## Instalação

O entrypoint do instalador é [`install.sh`](install.sh). Consulte as opções e os pré-requisitos no script e na documentação correspondente antes de instalar ou reinstalar componentes.

## Componentes e versões

O arquivo [`ecosystem.release.json`](ecosystem.release.json) fixa os commits do Agent CLI, Reverse Proxy, Protocol, Memory, Toolbox, Assistant e AI Workers para instalações reproduzíveis.

## Reverse Engineering Clean-Room

A release inclui validação de contratos de caixa-preta, revisão assinada e pipeline offline em ambiente OCI isolado. **O código gerado ainda exige validação diferencial real com o Windows Oracle; CI verde não significa certificação Clean-Room.**

- [Fluxo e controles do RE Clean-Room](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/CLEANROOM_RE.md)
- [Notas técnicas da versão 0.16.30](docs/RELEASE_0.16.30.md)

## Histórico

Todas as mudanças de versões ficam em [`CHANGELOG.md`](CHANGELOG.md). Os detalhes técnicos de cada entrega ficam em `docs/RELEASE_*.md`.
