# KITT 0.16.70 — Reverse Proxy não gerencia memória do Chromium

- Reverse Proxy `5.4.28`, pin `b3caa28a1997a624e88db7422c69e94b02f3997b`.
- Agent CLI `0.89.6` e todos os outros componentes mantêm os pins da versão `0.16.69`.

## Alterações

O Reverse Proxy deixou de capturar RSS/PSS do processo do Chrome/Chromium. Não rejeita sessões nem encerra conversas ociosas prematuramente **em razão da memória**. Conversas ChatGPT Web extensas podem aumentar seu consumo normalmente.

Foram removidos `--max-rss-mb`, `PROXY_MAX_RSS_MB`, a exceção de headroom por RAM e os campos de RAM dos snapshots da API de capacidades. Os limites de quantidade de sessões e páginas, o encerramento normal por inatividade, o isolamento entre conversas e a proteção de sessões aguardando resultados de ferramentas continuam ativos.

A dependência transitiva `qs` foi atualizada no lock do Reverse Proxy para `6.16.1`, resolvendo o novo alerta do `npm audit`. Nenhum outro componente foi atualizado nesta release.

## Validação

O PR [rfdetoni/kitt-reverse-proxy#111](https://github.com/rfdetoni/kitt-reverse-proxy/pull/111) passou em duas execuções de CI e no build Docker, com verificações de TypeScript, testes, browser/CDP e auditoria de dependências. A publicação do instalador depende de passar nos checks de integração e dos pins imutáveis.

## Instalação

Use o comando documentado no `README.md` para o canal `release` e o preset `full` com `--with-re-lab`; o instalador permanece responsável por REA, Linux RE, Ghidra/Frida e Dockur Windows 11. O provisionamento Windows e a validação do Oracle permanecem independentes desta mudança.
