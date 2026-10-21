# KITT 0.16.45 — continuidade de sessão sob pressão de memória

## Diagnóstico (logs de 21/10/2026)

O Agent CLI concluiu o planejamento, criou `mbs-wine` e pediu aprovação de acesso à rede para um clone Git. Após uma chamada aprovada, três novas chamadas com o **mesmo** `X-Kitt-Session-Id` receberam `session_limit_exceeded` sem executar o modelo. O Chromium já consumia 912 MiB, acima do orçamento configurado de 768 MiB. O gerenciador anterior podia reciclar uma sessão nomeada imediatamente após ela ficar ociosa, incluindo a pausa entre ferramenta host e retorno ao modelo.

## Atualização

- **Reverse Proxy 5.4.20:** reciclagem por pressão de RSS/páginas somente após uma tolerância de ociosidade de até cinco minutos para sessões nomeadas, respeitando o timeout de sessão configurado. Chamadas com o mesmo ID preservado reutilizam a sessão sem criar navegador novo.
- Na admissão de novas sessões, o LRU ainda pode reciclar imediatamente uma sessão nomeada ociosa, permitindo duas rodadas de planejamento isoladas seguidas da execução. Sessões ocupadas/reservadas não são recicladas; a tolerância de cinco minutos vale para a varredura automática por pressão de memória.
- A substituição LRU de uma sessão ociosa mantém o limite de quantidade de sessões. O proxy não admite novos navegadores se não existe candidato reciclável e o RSS/páginas já excede as restrições; fechar uma aba não prova liberação imediata de memória.
- Evento `session.capacity.resource_pressure_rejection` mostra a capacidade e a tolerância aplicada para facilitar o diagnóstico.

## Validação

Regressões para pausa de ferramenta, reutilização do ID, sequência de sessões isoladas de planejamento, reciclagem LRU na admissão e reciclagem automática somente após a janela de ociosidade. CI, Docker e instalação ponta a ponta da release exigidos antes de merge.

## Limites

Não reduz o RSS real do Chromium e não dispensa a verificação operacional no host do operador. A atividade no Wine/Win32u e os clones ainda precisam ser confirmados pelo KITT RE e pelas VMs. O pedido de aprovação para Git com `network=true` é uma proteção separada e não deve ser contornado.
