# KITT 0.16.44 — correção de patches no Agent CLI

## Componentes

- **Agent CLI 0.88.43:** aceita `*** Begin Patch`, `*** Update File` e hunks `@@` para arquivos existentes, reutilizando `EditBlock`, escopo do workspace, confirmação de políticas, correspondência única e rollback transacional.
- **Assistant Runtime 0.4.33:** sincroniza a dependência Python, o lock imutável e os dois checkouts do CI com o Agent CLI 0.88.43.
- **Reverse Proxy 5.4.18:** inalterado.

## Diagnóstico de origem

Os logs de 21/10/2026 registraram 20 propostas de ferramentas em uma etapa de `win32u.dll`. A proposta `patch.apply` da chamada 20 foi rejeitada porque o parser antigo não entendia `*** Begin Patch`. O parser novo resolve essa incompatibilidade sem ampliar permissões. Na mensagem seguinte houve `ui_capture_unverified`, uma resposta WebChat que não pôde ser associada ao pedido pelo CDP/DOM. A política de não reenviar automaticamente continua adequada para evitar duplicação.

## Validação

Os regressivos incluem o hunk `reports/t01-win32u-reconcile.py` capturado dos logs, mutação efetiva em arquivo temporário, vários hunks/arquivos e recusa de alterações fora do workspace ou sem contexto. Exigir CI de Agent, Assistant e instalador ponta a ponta, incluindo pinning da release.

## Limites

O suporte é propositalmente restrito a atualização de arquivos existentes. `*** Add File`, `*** Delete File` e `*** Move to` não são implementados por esse parser. A release não resolve automaticamente `ui_capture_unverified`, nem afirma que a implementação da `win32u.dll` foi concluída.
