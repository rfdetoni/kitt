# KITT 0.16.46 — integrações opcionais e versões fixadas

## Escopo

Atualiza o manifesto do canal `release` para o Agent CLI **0.88.44**, mantendo
os demais componentes em seus commits aprovados. Não duplica serviços de
memória, provedores ou mecanismos de pentest.

- `kitt setup recommend`: recomenda hooks, MCP e skills com inspeção local somente leitura;
- `kitt integrations configure-freellmapi`: configura um perfil OpenAI-compatible
  com segredo referenciado por variável de ambiente e origem explicitamente confiável;
- `kitt security strix scan`: invoca o Strix já instalado, somente para alvo autorizado;
- `kitt memory doctor`: consulta o `kitt-memoryd` existente.

## Controle de dependências

O `ecosystem.release.json` fixa os sete componentes por SHA completo.
O Agent CLI conserva `uv.lock`, a versão de pacote e o fallback de versão
sincronizados em **0.88.44**; `kitt-protocol` permanece fixado no SHA
`ac9baf8b4b8f03e839471c7bbb7d5e52e970a9ec`.

Dependências opcionais **não** são instaladas automaticamente:
FreeLLMAPI **v0.16.7** (commit
`ecdc9cbe27aa3db5e3d8935be13a5a17b9a513b1`) e
Strix **1.7.0** (commit
`55bc07991aacb1c26a81b43e7ca53148730d2019`).
O guia completo de integração é:
https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/OPTIONAL_AGENT_ECOSYSTEM.md

## Validação

Antes do merge, os checks do Agent CLI e o CI do ecossistema devem passar,
incluindo instalação real com o manifesto de release e verificação de pins.
Não declarar funcionalidades externas funcionando sem instância FreeLLMAPI
configurada ou pentest Strix executado em alvo autorizado.
