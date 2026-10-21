# KITT 0.16.49 — continuidade de agente filho sob pressão de memória

## Diagnóstico a partir dos logs de 21/10/2026

A tarefa `mbs-wine` entrou em uma sessão principal do ChatGPT Web, tentou inspecionar o Git com `git -C mbs-wine status --short --branch` e recebeu `Execution denied by PolicyEngine`. Esta situação foi corrigida separadamente no Agent CLI 0.88.48, já incluído no KITT 0.16.48.

Mais tarde, `children.spawn` criou um diagnóstico delegado, mas `children.inspect` retornou `FAILED` com `session_limit_exceeded`. O Proxy 5.4.20 registrou aproximadamente 1,10 GiB de memória no processo Chromium, cap de 768 MiB, uma sessão nomeada ocupada e nenhuma sessão nomeada ociosa reciclável. O Chromium já começara acima do limite configurado, com baseline perto de 1,16 GiB. Não houve verificação de clones, de ranking de DLLs ou de implementação de stubs.

## Correção

- **Reverse Proxy 5.4.21** permite uma **segunda e última sessão nomeada** durante o estado de pressão quando o Chromium já nasce acima do cap, respeitando estritamente a margem fixa do baseline inicial + 512 MiB e os limites de quantidade de sessões e páginas.
- O terceiro pedido simultâneo, o crescimento excessivo de memória, os pedidos acima dos limites rígidos e a tentativa de reciclar uma sessão ocupada continuam bloqueados. A exceção não constitui correção de vazamento de memória.
- Preserva o Agent CLI 0.88.48 e Assistant 0.4.37, já atualizados para permitir inspeção Git de leitura com `-C` em diretórios internos válidos.

## Validação

Regressões executam duas conversas ativas de uma vez (agente principal e filho), confirmam a negativa a uma terceira e simulam ultrapassagem da margem fixa. CI do Proxy, Docker e instalação ponta a ponta do ecossistema são obrigatórios antes de integrar o instalador.

## Limites operacionais

A configuração de memória do navegador continua em 768 MiB. Se o Chromium crescer além do headroom, o KITT deve bloquear a nova sessão e registrar a pressão, não exceder os limites indefinidamente. O resultado ainda precisa ser validado no host real; a ferramenta não executou clones ou Win32 Oracle neste ambiente.
