# KITT 0.16.73 — resolução de falhas do editor WebChat

## Evidência dos logs (2026-10-28)

A requisição com `turn_id=98d658e345f4` usou o editor
`div[role=textbox,contenteditable=true]`. O preenchimento Playwright
`fill` de 14.413 caracteres estourou o prazo, e a leitura encontrou 0.
O Reverse Proxy enviou `ui_automation_error`; o Agent CLI gerou
`ProviderProtocolError` sem interceptação, terminando o turno com traceback.
Na requisição seguinte, a recuperação existente `rich_dom_replace`
foi verificada e a resposta teve contrato válido.

## Alterações

- Reverse Proxy 5.4.30: usa a escrita DOM já validada diretamente quando um
  editor rico recebe um prompt de 8 KiB ou mais, em vez de tentar `fill`
  primeiro; mantém duas verificações da integridade e proíbe envio sem a
  confirmação do conteúdo do editor.
- Agent CLI 0.89.9: captura `ProviderProtocolError` durante o streaming,
  registra `TurnBlocked`, preserva recibos das ferramentas anteriores
  e não faz replay automático de chamadas ambíguas à UI.
- No verificador, `python.targeted-tests` obrigatório com alteração
  documental passa a executar testes Python reais já presentes no workspace.
  Não transforma a ausência de testes em sucesso.

## Manifesto imutável

- `reverse-proxy`: `05d8527c54551caf1e7f525a14a78ee4e7a86acf`
- `agent-cli`: `74f8bf6c534bdffc16ef4ab73c6cca596c981982`

Sem mudanças nos outros pins, no controle da memória do Chrome ou nos
privilégios do sandbox. Nenhuma execução do binário `2.1.308` está
envolvida nas correções.

## Verificação

Os PRs dos componentes passaram pelos testes de contratos, Chromium/CDP,
Docker, Podman e Windows. O ecossistema valida os pins em CI, realiza a
instalação limpa e o smoke do canal release. O teste no navegador do usuário
após atualizar deve confirmar o comportamento na sessão longa real.
