# KITT 0.16.46 — Begin Patch contextual navigation

## Evidências do incidente de 21/10/2026

O KITT RE / projeto `mbs-wine` conseguiu criar arquivos e diretórios de preparação, mas a execução de `git -C mbs-wine rev-parse --show-toplevel` foi negada pelo `PolicyEngine`. O comando inclui a flag `-C`, que é explicitamente proibida pela política. Para tarefas Git que exijam uma pasta de trabalho específica, utilize `process.run` com `cwd: "mbs-wine"` e `argv: ["git", "rev-parse", "--show-toplevel"]`, respeitando a política de sandbox e as autorizações normais. Clones com acesso à rede devem continuar usando o campo `network: true` e todas as capacidades necessárias.

Posteriormente, um patch em `mbs-wine/bootstrap.py` começou com `@@` seguido de ` def main():` e outro `@@`, e falhou com `parse_failure`, apesar de conter três hunks de modificação. A execução parou em `ui_capture_unverified`: o Chrome confirmou o envio do prompt, mas nem CDP nem DOM provaram uma resposta nova atribuível ao pedido. Não há autorização para replay automático desse prompt.

## Correção incluída

- Agent CLI 0.88.45: interpretação segura dos hunks contextuais de navegação sem mutação; as modificações continuam usando a operação transacional existente, com verificações de correspondência única e caminhos protegidos.
- Assistant Runtime 0.4.34: faixa de dependência, lock do Agent e referências de CI sincronizados com a nova versão.
- Reverse Proxy 5.4.20 mantido.

## Verificação e escopo

A suíte de regressão testa o patch representativo do `bootstrap.py`, os formatos inválidos e a rejeição de patches sem mudança. Todos os checks do Agent, Assistant e instalador são obrigatórios antes da integração. O resultado não afirma que o Wine/Wine-Staging foi clonado, que o repositório Git foi inicializado, que o inventário foi completado ou que qualquer stub foi implementado.

## Pendências do host

Reexecutar com permissões de processo/capacidades verificadas; utilizar `cwd` em vez de `git -C`; conferir se o `mbs-wine/bootstrap.py` original escrito parcialmente já existe; não executar novamente pedidos enviados ao ChatGPT Web sem conferir seu resultado autenticado. Validar a presença do Windows Oracle, compilador e VM antes de marcar tarefas como DONE.
