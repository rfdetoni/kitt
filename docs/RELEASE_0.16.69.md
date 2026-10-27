# KITT 0.16.69 — Checkpoint do orçamento de modelo

## Versões e pins

- Instalador KITT: `0.16.69`.
- Agent CLI: `0.89.6`, commit imutável `69df41adee0c41354b0fd2768d658ff097c76bc8`.
- Reverse Proxy: `5.4.27`, sem alterações nesta release.
- Protocol, Memory, Toolbox, Assistant e AI Workers mantêm os pins da release 0.16.68.

## Evidência de produção

Nos logs de 27/10/2026 o turno `da6199fb0f87` executou 24 operações do host e, ao tentar nova chamada de modelo, `reserve_model_attempts` gerou `ExecutionBudgetExceeded: model call budget exceeded`. O handler genérico de dispatch produziu erro em vez de checkpoint.

## Correção

O loop de ferramentas captura o esgotamento de orçamento após as validações do host, emite `tool_loop.budget_checkpoint` e encerra o turno com `TurnBlocked`. Os comandos e mutações anteriores continuam registrados. Não são acrescentados privilégios, limites de chamadas ou retentativas da mesma solicitação.

A mudança inclui teste de regressão no TurnProcessor e atualização sincronizada de `pyproject.toml`, `kitt/__init__.py` e `uv.lock`.

## Pontos independentes

No mesmo conjunto de logs, o Reverse Proxy registrou pressão de memória (1.277.756.416 bytes medidos contra 805.306.368 bytes configurados) e erro de escrita do composer Chromium com um prompt extenso (~22 mil caracteres). São problemas separados, não corrigidos por esta release. O operador deve avaliar memória física, configuração de `--max-rss-mb` e integridade do Chromium antes de elevar limites. Os logs estavam configurados explicitamente com `--log-content full`.

## Instalação

O `README.md` mantém o comando completo `curl | sh` para o canal `release` com REA, AI Workers, Ghidra/Frida, Linux Docker RE, Dockur Windows 11 e imagens de VM. A validação do Oracle Windows segue necessária depois do provisionamento.

## Validação

Agent CLI PR #199 passou nos workflows PR Checks e Docker, incluindo regressões, Docker, Podman e smoke Windows. O instalador requer o gate de integração e validação dos pins antes do merge.
