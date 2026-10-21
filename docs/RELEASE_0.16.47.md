# KITT 0.16.47 — autonomia corrigida para checkout Git público

## Evidência: Agent CLI e Reverse Proxy 21/10/2026

A sessão da tarefa `mbs-wine` estava em `autonomous`, com operações locais aprovadas automaticamente. A chamada `process.run` `["git", "submodule", "add", "https://gitlab.winehq.org/wine/wine.git", "wine"]`, `cwd=mbs-wine`, `network=true` retornou aprovação necessária por falta de `network.access`. O operador aprovou depois de cerca de 110 segundos; a execução do comando consumiu cerca de 180 segundos, enquanto o daemon recebeu várias chamadas adicionais de aprovação. Os logs não comprovam o clone finalizado.

Houve também erros 404 dos perfis Ollama `qwen2.5:7b-instruct` e `qwen2.5:32b-instruct`; o Agent recorreu ao Reverse Proxy 5.4.20, com tempo elevado no planejamento. Esses dois problemas são independentes da aprovação do checkout.

## Correções

- **Agent CLI 0.88.47**: dois gates (SafeRuntime e ToolRegistry) compartilham regra restrita para Git de fontes públicas por HTTPS. Somente o contexto principal `USER:user_root` não restrito, sob `autonomous/allow-all`, pode executar `git clone` e `git submodule add` de `github.com`, `gitlab.com` ou `gitlab.winehq.org` em destinos relativos e contidos no workspace, se houver **sandbox forte** `workspace-write+network`.
- Não autoriza rede em Python, shell, subprocessos arbitrários, origens privadas, URLs com credenciais/query, caminhos de traversal, agentes descendentes nem em modo supervisionado.
- **Assistant Python Runtime 0.4.36** fixa commit imutável do Agent 0.88.47 via dependencia, `uv.lock` e CI.
- **Reverse Proxy 5.4.20** inalterado.

## Validação

Regressões comprovam o caminho da chamada real de clone, testes de recusas de rede, isolamento do principal e fallback para aprovação em ausência de sandbox forte. Release do instalador exige CI de todos os componentes e instalação ponta a ponta.

## Pendências reais

Reexecutar a instalação no host e confirmar o clone dentro do timeout; verificar o modelo local configurado ou remover fallback Ollama inexistente. Nenhuma implementação de DLL foi validada por esses logs. Cliques repetidos no modal foram observados como chamadas ao daemon, mas não equivalem, isoladamente, à prova de prompts repetidos gerados pelo sistema.
