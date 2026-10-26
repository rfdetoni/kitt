# K.I.T.T. — Ecossistema

Instalador e manifesto de versões do ecossistema K.I.T.T. A versão atual do canal release é **0.16.64**.

## Instalação

O entrypoint do instalador é [`install.sh`](install.sh). Consulte as opções e os pré-requisitos no script e na documentação correspondente antes de instalar ou reinstalar componentes.

**Dica (Ubuntu/Linux):** se o KITT indicar `Strong sandbox profile ... requires functional bubblewrap >= 0.12` ou `bwrap: setting up uid map: Permission denied`, consulte [Diagnóstico do Bubblewrap e AppArmor](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/BUBBLEWRAP_APPARMOR.md). A configuração do perfil AppArmor deve corresponder ao executável realmente utilizado; não desative a restrição de namespaces globalmente.

## Broker isolado no Docker Compose

A opção `--profile agent` inicia um sidecar `sandbox-broker` com socket Unix
compartilhado com o Agent, sem exposição de porta TCP. Somente o sidecar monta
`/var/run/docker.sock`. Ele descobre o bind mount do workspace a partir de
metadados do próprio container e cria workers persistentes por linguagem e
escopo de rede. Os workers não recebem o socket nem o estado de controle do
KITT. O broker é uma peça privilegiada: só execute este perfil em hosts
confiáveis.

Por padrão, `KITT_BROKER_ALLOW_NETWORK=false`. Para autorizar downloads de
dependências sem novas perguntas, defina também
`KITT_AUTOPILOT_DELEGATE_NETWORK=true` para o Agent. O broker mantém a segunda
barreira de rede independente; sem ambas as condições, não há egress. O perfil
sem Docker saudável falha fechado e nunca recorre ao shell irrestrito do host.

## Sandbox autônomo

O Agent CLI 0.89.1 aceita comandos de desenvolvimento via `sandbox.run` e
roteia `process.run` automaticamente para um executor isolado quando o workspace
está no modo `autonomous` e dispõe das capacidades `process.run` e `repo.write`.
O instalador Linux prepara a imagem Docker do Agent CLI se houver Docker funcional;
caso contrário, o runtime usa Bubblewrap funcional (>=0.12). Nenhuma execução
não isolada é autorizada como fallback.

A preparação Docker cobre o **Agent nativo** que acessa o daemon do host. O
serviço Agent no Compose não monta o socket Docker e não possui um broker remoto
nesta versão; não se deve prometer execução autônoma de shell nesse modo até
haver um executor isolado dedicado. Rede requer `network.access` delegado.

O executor Docker pode escolher automaticamente imagens oficiais Java 25/Maven,
Gradle/JDK 25, Node 24 ou Rust quando necessário. O broker confiável baixa as imagens
pré-definidas no primeiro uso; elas não podem ser selecionadas arbitrariamente
pelo modelo. O executor prefere Docker para ferramentas de build conhecidas, mesmo quando
Bubblewrap funciona, e mantém comandos genéricos no backend leve. Pacotes e
imagens permanecem dependentes da rede autorizada e do ambiente.

## Componentes e versões

O arquivo [`ecosystem.release.json`](ecosystem.release.json) fixa os commits do Agent CLI, Reverse Proxy, Protocol, Memory, Toolbox, Assistant e AI Workers para instalações reproduzíveis.

## Reverse Engineering Clean-Room

A release inclui validação de contratos de caixa-preta, revisão assinada e pipeline offline em ambiente OCI isolado. **O código gerado ainda exige validação diferencial real com o Windows Oracle; CI verde não significa certificação Clean-Room.**

- [Fluxo e controles do RE Clean-Room](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/CLEANROOM_RE.md)
- [Notas técnicas da versão 0.16.64](docs/RELEASE_0.16.64.md)

## Histórico

Todas as mudanças de versões ficam em [`CHANGELOG.md`](CHANGELOG.md). Os detalhes técnicos de cada entrega ficam em `docs/RELEASE_*.md`.
