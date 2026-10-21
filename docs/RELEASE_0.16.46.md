# KITT 0.16.46 — inicialização segura do índice SQLite

## Incidente

Iniciar outra interface KITT em `/home/toni/projects/mbs` falhava em `RepositoryIndex._init_db` com `sqlite3.OperationalError: database is locked` ao gravar a chave `schema_version` na tabela `index_meta`. O daemon KITT tem acesso aos arquivos `.kitt/index/index.db`, `index.db-wal` e `index.db-shm`. Isso confirma o compartilhamento do índice, mas manter os arquivos abertos não demonstra isoladamente uma transação de escrita ativa.

## Correção

- Agent CLI 0.88.46: espera SQLite de até 2 segundos, removendo `PRAGMA busy_timeout` conflitante do script de esquema.
- Se uma conexão persistente falhar **por SQLITE_BUSY/SQLITE_LOCKED**, encerra-se somente a conexão incompleta do novo processo, sem checkpoint/truncate do WAL alheio, e o índice desse processo passa a operar em memória. A pesquisa/indexação temporária funciona sem escrita no índice principal; não há sincronização desse índice temporário ao encerrar.
- Erros de SQLite que não sejam disputa de bloqueio continuam falhando explicitamente.
- Diagnóstico nos metadados: `index_storage: memory_fallback` e `index_fallback_reason`.
- Assistant Runtime Python 0.4.35 fixa o mesmo commit Agent CLI. Reverse Proxy 5.4.20 permanece igual.

## Testes

A regressão cria uma transação real de gravação no índice, abre um segundo `RepositoryIndex`, verifica que pesquisa/indexação temporárias funcionam, mantém a transação original intacta e demonstra que, após liberação, outra instância volta a usar o banco persistente.

A publicação no instalador requer CI do Agent, Assistant e integração end-to-end com pin imutável de cada repositório.

## Limites

A correção elimina a interrupção na **inicialização do índice** por contenção de escrita; não substitui uma validação com o daemon real no host e não promete que toda disputa futura de atualização do índice será automaticamente reconciliada. Não apague `index.db`, `index.db-wal` ou `index.db-shm` enquanto houver processos ativos.
