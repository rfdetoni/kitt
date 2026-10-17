# Política de versionamento e changelog do ecossistema K.I.T.T.

1. **README.md é documentação de produto**: visão geral, instalação, arquitetura, configuração, segurança e links. Não acrescentar anúncio de nova release, cronologia de versões, ou blocos `# Product X.Y.Z` ao README.
2. **CHANGELOG.md concentra TODAS as releases**, mais recente primeiro, com versão, mudanças, limites, regressões, migrações e link para as notas técnicas. Não descartar entradas antigas.
3. **docs/RELEASE_X.Y.Z.md** contém detalhes técnicos e evidência dos checks. README aponta para CHANGELOG e, opcionalmente, para a versão atual, sem copiar a nota inteira.
4. Mudança de pacote/código/pin/lock requer novo bump semântico nos componentes afetados. Sincronizar Python `pyproject.toml`/`uv.lock`, Rust `Cargo.toml`/`Cargo.lock`, TypeScript/npm `package.json`/`package-lock.json` e metadados de runtime conforme o caso. Não mudar tags imutáveis.
5. Atualizar a matriz de pins por SHA no `ecosystem.release.json`, depois de validar os componentes; preservar a correspondência com os consumidores e seus locks.
6. **CI antes de afirmar sucesso**: verificar lint, testes, builds e integração. Assinalar explicitamente `UNVERIFIED` para infraestrutura não executada (Windows Oracle, imagens/modelos offline, identidade e proveniência dos revisores, isolamento de SO, E2E real).
7. Publicar alterações na `main` somente com autorização; uma atualização documental do CHANGELOG ou README não justifica novo bump da versão de pacote se o tag imutável e os artefatos funcionais permanecem idênticos.

Este padrão vale para os oito repositórios do manifesto: KITT, Agent CLI, Reverse Proxy, Protocol, Assistant, AI Workers, Memory e Toolbox.
