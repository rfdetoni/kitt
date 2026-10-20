# KITT Ecosystem 0.16.24 — modais e recuperação controlada

## Componentes fixados

- **Agent CLI 0.88.20** — commit `4a454888864cd28341fe534e2ac8659dd1eccfad`, [PR #125](https://github.com/rfdetoni/kitt-agent-cli/pull/125).
- **Reverse Proxy 5.4.14** — commit `9dc9e788d77827eb5df04775a1c1b58a231764b5`, [PR #98](https://github.com/rfdetoni/kitt-reverse-proxy/pull/98).
- Protocol, Memory, Toolbox, Assistant e AI Workers preservam os pins imutáveis da versão 0.16.23.

## Correções

- Modais: teclas `A/a` aprovam permanentemente no workspace na tela de aprovação; `A/a/1`, `S/s/2` e `D/d/3` selecionam os perfis de autonomia. Os atalhos têm precedência sobre editores de texto quando o modal correspondente está ativo; permissões continuam condicionadas ao host/daemon.
- Resultados grandes: o CLI fornece uma prévia limitada e um identificador do artefato original; `artifacts.read`/`hydrate`/`retrieve` não criam novos artefatos ao serem consumidos.
- Negativas do host: chamadas idênticas previamente negadas pela PolicyEngine na mesma iteração não são repetidas.
- Contrato v5: `request_tools` recebe no máximo um lembrete quando o catálogo de ferramentas já veio do host. Com catálogo vazio, nenhum acesso novo é inventado.
- Instrumentação: adiciona contagem de rodadas de modelo, sem prometer ganho percentual de latência.

## Gates e limitações

CI e Docker dos componentes devem passar antes da promoção, seguidos por `ecosystem-main` e `ecosystem-integration` do manifesto atualizado. Os testes de UI usam entrada real `prompt_toolkit` com pipe; a validação autenticada de ChatGPT/Gemini Web ainda não foi reproduzida por CI. Nenhum benchmark de latência em sessão WebChat foi registrado nesta release.
