# K.I.T.T. — Ecossistema

Instalador e manifesto de versões do ecossistema K.I.T.T. A versão atual do canal release é **0.16.73**.

## Instalação

O entrypoint do instalador é [`install.sh`](install.sh). Consulte as opções e os pré-requisitos no script e na documentação correspondente antes de instalar ou reinstalar componentes.

**Dica (Ubuntu/Linux):** se o KITT indicar `Strong sandbox profile ... requires functional bubblewrap >= 0.12` ou `bwrap: setting up uid map: Permission denied`, consulte [Diagnóstico do Bubblewrap e AppArmor](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/BUBBLEWRAP_APPARMOR.md). A configuração do perfil AppArmor deve corresponder ao executável realmente utilizado; não desative a restrição de namespaces globalmente.

## Instalação completa com laboratório RE (Linux)

O exemplo instala o canal `release` com todos os módulos, REA e dependências
dos AI Workers, provisiona o RE lab com Linux Docker/Ghidra/Frida e Windows 11
Dockur, e baixa as imagens opcionais de VM em containers:

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- \
  --preset full --channel release --yes --with-rea --with-ai-workers \
  --with-re-lab --re-runtime docker --re-profile full \
  --re-windows dockurr --re-windows-version 11 --re-oracle-bootstrap \
  --accept-windows-license --with-vm-containers \
  --vm-container-runtime docker --vm-container-image-profile full --vm-pull-images
```

**Pré-requisitos:** Linux com Docker Engine operacional, `/dev/kvm`,
`/dev/net/tun`, Git e rede para baixar imagens; o instalador também verifica
e prepara outros pré-requisitos suportados. A flag
`--accept-windows-license` só deve ser usada por quem possui uma licença válida
do Windows 11 e autoriza os downloads. O laboratório não substitui nem apaga
um Windows já instalado sem autorização separada. O provisionamento não equivale
a verificar o Oracle: execute `kitt re lab status --json` e
`kitt re lab verify --full` após a instalação. `--channel edge` acompanha
as `main` mais recentes; `release` instala os commits imutáveis deste manifesto.

## Verificação Python sem acesso à rede no agente

O instalador prepara Ruff `0.14.3` dentro do mesmo ambiente virtual do
Agent CLI e valida seu executável. O verificador encontra a ferramenta mesmo
sem o ambiente virtual no `PATH` e executa os checks `python.lint` exigidos
pelo contrato, inclusive quando a tarefa modificou apenas documentação mas o
workspace contém scripts Python. A ausência real do linter continua sendo uma
falha de verificação; o agente não tenta instalá-lo via `process.run` com rede.

Os sockets Docker do host permanecem isolados dos comandos arbitrários
executados pelo agente. Para imagens e análise RE, use operações governadas
`re.lab.images` e `re.lab.analyze`, não `docker` ou `podman` dentro do Bubblewrap.

## Recuperação do Reverse Proxy

O Agent CLI 0.89.6 espera até 30 segundos por um Reverse Proxy local que ainda
não aceita conexões, com cancelamento e verificação `GET /healthz`.
A solicitação de chat não é reenviada depois de ser submetida. Após o proxy
ficar disponível, a negociação de capacidades é atualizada. Instâncias do proxy
iniciadas e gerenciadas pelo Agent utilizam `KITT_LOG_CONTENT=metadata` por
padrão, inclusive no nível TRACE; a captura de conteúdo completo é uma opção
explícita do operador. `flow.execute` permanece somente leitura: validação
por comandos utiliza `process.run` separadamente e mediante as políticas do host.

## Checkpoint por orçamento de modelo

O Agent CLI 0.89.6 trata esgotamento dos limites de chamadas ao modelo,
tokens, custo ou duração durante o loop como `TurnBlocked` com checkpoint.
O orçamento não é aumentado, resultados de ferramentas já concluídas não
são repetidos e o usuário pode continuar o item pendente em outro turno.
Essa alteração evita o traceback genérico após uma sequência longa de ações
de host verificadas.

Erros de preenchimento do Chromium com prompts muito extensos e
recusas por pressão de memória do Reverse Proxy têm causas diferentes;
os limites de memória e as verificações de integridade do editor não foram
desabilitados. Para diagnóstico, `KITT_LOG_CONTENT=metadata` evita gravar
o corpo completo dos prompts em instâncias do proxy iniciadas pelo Agent;
`full` exige configuração explícita.

## Memória do navegador gerenciada pelo próprio Chrome

O Reverse Proxy `5.4.28` não mede RSS/PSS do Chromium e não interrompe
conversas por consumo elevado de RAM. O Chrome e o sistema operacional
decidem como usar a memória, inclusive em sessões ChatGPT Web extensas.
As opções antigas `--max-rss-mb` e `PROXY_MAX_RSS_MB` foram removidas.
Permanecem os limites operacionais de sessões/abas, o encerramento por
inatividade e a proteção de sessões com operações ou ferramentas pendentes.
Em hosts com pouca RAM, o próprio navegador ou sistema pode ficar lento
ou encerrar processos; o proxy não substitui os controles do sistema.

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

## Tarefas isoladas por worktree

O Agent CLI 0.89.6 mantém a capacidade de iniciar `autopilot.transaction.start` em um
checkout Git limpo. A execução e os testes são direcionados a um worktree
isolado. Comandos nessa modalidade exigem Docker ou o broker confiável do
Compose, que monta apenas o diretório da tarefa; a execução não recai no
Bubblewrap que expõe partes do checkout principal.

`autopilot.transaction.status` acompanha a tarefa e
`autopilot.transaction.abandon` preserva uma cópia para auditoria sem alterar
o checkout original. A publicação remota continua opcional, requer aprovação
antecipada do operador, `autopilot.verify` aprovado e fingerprint inalterado.
Não existe promoção local automática nesta versão.

## Publicação remota verificada (opcional)

O Agent CLI 0.89.2 adiciona `autopilot.publish` para uma única branch e
repositório GitHub pré-autorizados pelo operador. Essa operação exige
`autopilot.verify` bem-sucedido, mesmo fingerprint do workspace e Git HEAD,
`network.access` delegado e credencial GitHub mantida fora do sandbox.
Nenhuma publicação ocorre quando `KITT_AUTOPILOT_PUBLISH_ENABLED=false`.

No Compose, configure o arquivo de token por um **override confiável** que monte
um segredo read-only apenas no container Agent; informe seu caminho por
`KITT_AUTOPILOT_GITHUB_TOKEN_FILE`. Nunca monte o token no workspace, broker
ou workers e nunca habilite Docker socket dentro do Agent. Branch protegida ou
sem autorização permanece bloqueada. Essa modalidade usa GitHub Git Data API
com atualização não forçada; não dispara `git push` no host.

## Sandbox autônomo

O Agent CLI 0.89.6 aceita comandos de desenvolvimento via `sandbox.run` e
roteia `process.run` automaticamente para um executor isolado quando o workspace
está no modo `autonomous` e dispõe das capacidades `process.run` e `repo.write`.
O instalador Linux prepara a imagem Docker do Agent CLI se houver Docker funcional;
caso contrário, o runtime usa Bubblewrap funcional (>=0.12). Nenhuma execução
não isolada é autorizada como fallback.

No **Agent nativo**, o executor usa Bubblewrap ou Docker conforme a ferramenta
e o ambiente. No **Agent do Compose**, o sidecar `sandbox-broker` executa comandos
em workers Docker persistentes sem montar o socket Docker no próprio Agent.
Acesso à rede exige autorização explícita do operador e capacidade
`network.access` no principal.

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
- [Notas técnicas da versão 0.16.72](docs/RELEASE_0.16.72.md)

## Histórico

Todas as mudanças de versões ficam em [`CHANGELOG.md`](CHANGELOG.md). Os detalhes técnicos de cada entrega ficam em `docs/RELEASE_*.md`.
