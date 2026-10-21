# KITT 0.16.48 — leitura Git em subdiretórios sem bloqueio indevido

## Incidente

Os logs de 2026-10-21 19:52:30 em `~/projects/mbs` mostraram `autonomy=autonomous`, mas `process.run` com `argv=["git","-C","mbs-wine","status","--short","--branch"]` foi rejeitado por `PolicyEngine` como `DENY`. A leitura direta de `.git` também foi rejeitada corretamente pelo controle de caminhos protegidos. O agente reescreveu `mbs-wine/README.md` diversas vezes, sem validar o checkout Wine, concluir Wine-Staging, calcular as três DLLs ou registrar commits Git.

## Correção

- **Agent CLI 0.88.48**: interpreta `git -C <pasta>` quando a pasta existe dentro do workspace e a operação é uma consulta read-only autorizada pelas verificações originais do Git (`status`, `diff`, `log`, `branch` leitura). Nega `-C` absoluto, `..`, symlink externo, diretório `.git`, `reset`, `push`, flags `--git-dir` e similares.
- **Assistant Python Runtime 0.4.37** fixa a versão acima no lock e CI.
- **Reverse Proxy 5.4.20** permanece inalterado. A regra anterior de checkout de Git HTTPS público via sandbox forte segue válida.

## Validação e limites

CI do Agent verifica o comando observado e os casos de segurança, além de contratos críticos e runtime Docker/Podman/Windows. CI do Assistant e do ecossistema verificam dependências e instalação release.

Os mesmos logs também registraram `session.capacity.resource_pressure_rejection`: memória medida de cerca de 1.10 GB diante do limite configurado de 768 MB, impedindo uma sessão filha por `session_limit_exceeded`. A proteção de memória deve permanecer; usar menos sessões/menos paralelismo é um contorno operacional, não prova de correção. A latência de chamadas Web e o comportamento do agente que reescreve README repetidamente permanecem oportunidades independentes de melhoria.

O código foi validado em CI, mas é necessária nova execução no host para confirmar progresso do inventário Wine e operação das VMs.
