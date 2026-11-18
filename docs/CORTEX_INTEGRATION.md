# Projeto Córtex no ecossistema KITT

O Projeto Córtex evolui o KITT existente; **não** instala um segundo
orquestrador ou substitui o Agent. Esta integração é incremental e opt-in.

## Distribuição de responsabilidades

| Componente | Responsabilidade |
| --- | --- |
| kitt-assistant-runtime | Ingestão autenticada de eventos e estado contextual |
| kitt-agent-cli | Planejamento DAG, orçamentos e única autoridade para execução |
| kitt-protocol | Contratos CortexEvent/CortexDelivery/Preflight nos SDKs |
| kitt-memoryd | Memória semântica durável; não armazena os eventos transitórios do Córtex |
| kitt-reverse-proxy | Acesso a provedores e sessões temporárias sem alterar permissões |
| nodexlm | System One local para aconselhamento; não autoriza ferramentas |
| kitt-ai-workers | Processamento especializado sob demanda |

## Uso (canal edge após inclusão do Assistant)

O runtime Python `kitt-assistant-runtime` expõe o comando `kitt-cortex`.
Ele se conecta ao mesmo daemon KITT, usa o IPC autenticado e respeita o
workspace. Não publica um novo endpoint web aberto.

```sh
kitt daemon status
kitt-cortex --workspace . status
kitt-cortex --workspace . publish saas.error.500 \
  --source monitor --severity 4 \
  --payload '{"service":"billing","status":500}'
kitt-cortex --workspace . claim plugin-saas-sre --limit 10
```

A resposta de `claim` contém o identificador do evento e o token de lease.
Após processar a entrega com o **Agent**, o consumidor pode confirmar:

```sh
kitt-cortex --workspace . settle plugin-saas-sre \
  EVENT_ID LEASE_TOKEN
```

Em caso de falha, passe `--failed`; a entrega é reagendada com backoff.
Nenhuma ação de infraestrutura, acesso a arquivos ou ferramenta é executada
pela camada de eventos. Cada efeito real precisa de autorização do Agent e
de um receipt idempotente.

### Estado contextual

```sh
kitt-cortex --workspace . context-set activity_state DEEP_WORK
kitt-cortex --workspace . context-get
```

Campos intencionalmente pequenos: `location`, `activity_state` e
`active_channel`. Cada valor tem origem e expiração. Limites de orçamento
permanecem no ledger do Agent, e não no estado global do Córtex.

### NodexLM (opcional)

```sh
export KITT_CORTEX_DECISION_URL=http://127.0.0.1:8787
export KITT_CORTEX_DECISION_MODEL=ollaya/laya:multilingual
# NODEXLM_API_KEY em secret store ou ambiente de serviço protegido
```

O modelo e o runtime System One precisam estar disponíveis no NodexLM.
A chamada de classificação não compartilha o corpo do evento. Eventos de
sensibilidade pessoal, privada ou secreta permanecem limitados a rotas locais.
O sinal do modelo nunca define aprovações ou permissões.

## Departamentos iniciais

As assinaturas estáticas registradas no código cobrem:
`home.*` → segurança residencial;
`saas.*` → SRE;
`communications.*`, `calendar.*`, `user.*` → Chief of Staff;
`dev.*`, `repo.*` → Staff Engineer.

Essa entrega implementa **transporte e contratos**, não conectores ativos.
A coleta MQTT/RTSP/IMAP/Calendar, o registro dinâmico de plugins, o scheduler
proativo com aprovações e o Control Center de Córtex requerem etapas de
implementação e testes adicionais. Não confundir classes de eventos com
ações automáticas já em funcionamento.

## Verificação para publicação

- CI do kitt-assistant-runtime: Python 3.14, testes, Linux/Windows/macOS,
  compilação do daemon e segurança do IPC.
- CI do kitt-protocol: Rust e SDKs Python/TypeScript, contratos entre plataformas.
- Aceitação manual com NodexLM/Android (hardware real), sensores e provedores.
- Revisar licenças quando distribuir o NodexLM (AGPL-3.0-only).

As releases fixas em `ecosystem.release.json` não passam a incluir
automaticamente código novo da `main`. Use o canal edge para testar a versão
recente, ou publique uma release imutável coordenada após os gates.
