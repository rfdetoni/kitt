# Revisão pragmática do KITT 0.15.26 — escopo verificável

Data: 2026-10-13. A investigação cobriu os caminhos
`kitt/runtime/read_batch.py`, `core_runtime.py`,
`safe_runtime.py`, `retrieval_guard.py`, `revision_refs.py` e
`WorkspaceFileSystem.atomic_write`, além dos testes relevantes.

## P1 — estado de deduplicação compartilhado por workers

**Local:** Agent CLI `kitt/runtime/retrieval_guard.py`,
`RetrievalGuard.observe`, `invalidate` e `_prune`.

**Evidência:** `repo.batch_read` invoca `runtime.execute` com
`ThreadPoolExecutor(max_workers<=4)`; `runtime.execute` usa a mesma
instância `retrieval_guard`. Antes da correção, `observe` e
`invalidate` mutavam `OrderedDict`, contadores e geração sem exclusão
mútua, expondo a repetição de leituras a transições inconsistentes.
A revisão inicial de `core_runtime._dispatch` isolado foi insuficiente;
a implementação real de `repo.list` encontra-se em
`safe_runtime.SafeRuntime._dispatch` e foi preservada.

**Correção:** `RLock` protege a seção crítica; chamada real de I/O
continua fora do lock. O teste instrumenta `_prune` e afirma que a seção
de estado não é executada simultaneamente quando oito leituras são
submetidas ao lote.

**Status:** corrigido, tests/PR checks verdes na revisão do Agent.

## P2 — prefixos UTF-8 de revisão em limites de bytes

**Local:** `kitt/runtime/revision_refs.py`,
`execute_revision_ref` (`repo.ref.read`).

**Evidência:** cortar o buffer antes de `decode(errors="replace")`
transformava um caractere UTF-8 válido, mas incompleto no limite, em
U+FFFD (dado inexistente no arquivo).

**Correção:** decodificador incremental com `final=false` apenas nos
prefixos truncados, mantendo erro substituído em arquivo completo
ilegível. Regressões verificam limite por byte sem alterar o digest
SHA-256 do arquivo original.

**Status:** corrigido e testado.

## Riscos e pendências não encerrados

- A implementação de CAS do filesystem realiza verificações de hash
  antes da substituição atômica. Não foi comprovada exclusão entre
  escritores concorrentes de processos distintos; um resultado
  `committed` não deve ser interpretado como transação distribuída.
- Os grandes módulos de Agent, Proxy, Assistant e Memory não passaram
  por uma revisão estática+dinâmica completa de alcance de símbolos e
  todas as chamadas. Não há base para remover código morto global.
- A captura ChatGPT Web precisa ser exercitada no navegador logado do
  operador, acompanhando as métricas sanitizadas de correlação
  CDP/DOM. O ambiente CI não possui a mesma sessão.
- Negociação de versões KAP e terminação antecipada de streaming
  não foram habilitadas e exigem definição de contrato, segurança e
  implantação conjunta.

**Parecer limitado:** nos caminhos modificados, os checks de CI do Agent
não encontraram bloqueadores. Não constitui auditoria exaustiva nem
validação operacional da captura do Proxy.
