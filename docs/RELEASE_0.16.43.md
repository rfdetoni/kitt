# KITT Ecosystem 0.16.43 — continuidade de Goals por checkpoint

## Correção incluída

Agent CLI 0.88.42 acrescenta um resultado durável `CHECKPOINT` quando uma etapa de Goal atinge um limite **do turno** com uma razão emitida pelo host (`Execution budget checkpoint:`). O item volta para `PENDING` sem consumir uma tentativa de falha. O `GoalScheduler` reprograma a mesma etapa; a contagem global de turnos, duração, custo e tokens permanece ativa.

Respostas sem essa origem não podem usar `CHECKPOINT` para contornar o limite de tentativas. Evidências existentes e itens concluídos permanecem preservados, sem alargar permissões nem relaxar políticas de sandbox.

## Validação e escopo

A regressão exercita a passagem entre turnos de uma etapa com limite de uma tentativa e prova que o orçamento global continua sendo debitado. Os testes dos componentes, o CI e a verificação de versões e pins devem concluir antes da integração.

A release também fixa Assistant Runtime 0.4.32, com dependência, uv.lock e CI sincronizados com Agent CLI 0.88.42. Mantém Reverse Proxy 5.4.18 e os pins dos demais componentes. Não altera o Chrome, não remove limite total de Goals e não comprova desempenho nem autonomia nas VMs do operador. A compatibilidade real do Windows Oracle continua sujeita a validação independente.
