# KITT 0.16.45 — continuidade de sessão sob pressão de memória

## Diagnóstico (logs de 21/10/2026)

O Agent CLI concluiu o planejamento, criou `mbs-wine` e pediu aprovação de acesso à rede para um clone Git. Após uma chamada aprovada, três novas chamadas com o **mesmo** `X-Kitt-Session-Id` receberam `session_limit_exceeded` sem executar o modelo. O Chromium já consumia 912 MiB, acima do orçamento configurado de 768 MiB. O gerenciador anterior podia reciclar uma sessão nomeada imediatamente após ela ficar ociosa, incluindo a pausa entre ferramenta host e retorno ao modelo.

## Atualização

- **Reverse Proxy 5.4.19:** reciclagem por pressão de RSS/páginas somente após uma tolerância de ociosidade de até cinco minutos para sessões nomeadas, respeitando o timeout de sessão configurado. Chamadas com o mesmo ID preservado reutilizam a sessão sem criar navegador novo.
- Novas sessões continuam sujeitas a limite de memória, páginas e quantidade. A substituição ao atingir apenas o limite de quantidade continua usando a reciclagem LRU.
- Depois de reciclar por pressão de recursos, o proxy verifica novamente RSS/páginas; fechar uma aba não prova liberação imediata de memória.
- Evento `session.capacity.resource_pressure_rejection` mostra a capacidade e a tolerância aplicada para facilitar o diagnóstico.

## Validação

Regressões para pausa de ferramenta, reutilização do ID, negativa a outra sessão e reciclagem após janela de ociosidade. CI, Docker e instalação ponta a ponta da release exigidos antes de merge.

## Limites

Não reduz o RSS real do Chromium e não dispensa a verificação operacional no host do operador. A atividade no Wine/Win32u e os clones ainda precisam ser confirmados pelo KITT RE e pelas VMs. O pedido de aprovação para Git com `network=true` é uma proteção separada e não deve ser contornado.
