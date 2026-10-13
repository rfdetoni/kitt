# KITT 0.15.9 — Correção dos contratos MCP do REA

## Versões coordenadas

- Agent CLI **0.86.12**: corrige identificadores de ferramentas `rea_workflow` para corresponder aos contratos reais do REA 6.4.0, sem adicionar wrappers, shell remoto ou autorização automática.
- Assistant runtime **0.3.10**: somente atualização de dependência e lock do Agent.
- Ecossistema **0.15.9**: fixa os commits aprovados e mantém o instalador `--preset full` que já instala REA 6.4.0 por padrão.

## O que permanece igual

- Toolbox Docker/Podman Linux `full` já inclui REA 6.4.0, Node.js 24, Ghidra, Frida e Wine, publicado sob tags **0.86.10** (sem rebuild, pois a imagem não mudou).
- Os perfis `base` e `wine` continuam menores; o modo de programação normal não ativa REA ou VM automaticamente.
- Ativação do MCP: `kitt plugins enable kitt-rea`; `rea_workflow` apenas sugere ferramentas e não executa o REA sem a política de aprovação do KITT.

## Validação

Testes do Agent conferem os nomes de ferramentas e os contratos MCP; CI da release verifica locks/pins e a instalação coordenada. Um teste real de QEMU no host e investigação Windows/Linux completa continuam separados.
