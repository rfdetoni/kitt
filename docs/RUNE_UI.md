# Interface KITT com Rune (preview opt-in)

O KITT passa a ter uma camada visual compartilhada em Rust usando
[anomalyco/rune](https://github.com/anomalyco/rune), com um projeto isolado no
repositório [kitt-assistant/apps/kitt-rune](https://github.com/rfdetoni/kitt-assistant/tree/main/apps/kitt-rune).

## Estado confirmado

A nova interface possui telas Rune para saúde do ecossistema, Assistant,
modelos, Reverse Proxy, Córtex, agentes, memória, sessões e configurações.
No estágio atual, as informações reais exibidas vêm apenas dos endpoints de
status local do Control Center. Sessões, Córtex e configurações têm
navegação e apresentação, mas **ainda não possuem paridade operacional**
com as interfaces antigas.

Também há um HUD Rune opcional que recebe eventos de status/texto pelo IPC
autenticado de `kittd`. Imagens, overlays e recursos avançados continuam
na implementação anterior.

O PR [rfdetoni/kitt-assistant#75](https://github.com/rfdetoni/kitt-assistant/pull/75)
foi aprovado no CI Rust, WASM, Node e na suíte principal do Assistant.
Esta entrega é opt-in e não altera o canal de release imutável.

## Execução nativa (Linux, macOS e Windows)

Com um checkout atualizado do kitt-assistant:

```bash
cargo run --manifest-path apps/kitt-rune/Cargo.toml --bin kitt-rune
```

A interface acessa o Control Center em `127.0.0.1:41828`. A nova interface
é um cliente, não um daemon de execução. Ela busca status em segundo plano,
a cada 15 segundos, sem bloquear os frames da UI.

Para experimentar o HUD alternativo:

```bash
cargo run --manifest-path apps/kitt-rune/Cargo.toml --bin kitt-rune-hud
```

Ao executá-lo diretamente, o daemon deve fornecer as credenciais de IPC
necessárias. Para lançar automaticamente em resposta a uma solicitação,
configure `KITT_HUD_BIN` para o binário `kitt-rune-hud` compilado e reinicie
o serviço do Assistant. O HUD antigo deve continuar disponível como fallback.

## Web (WebGPU)

O alvo Web usa o mesmo código de interface compilado em WASM. Para build,
siga [apps/kitt-rune/README.md](https://github.com/rfdetoni/kitt-assistant/blob/main/apps/kitt-rune/README.md).

A ponte Web funciona apenas em loopback e tem três endpoints GET em allowlist.
Ela remove tokens, campos de configuração sensíveis e dados brutos antes de
enviar uma projeção ao canvas Rune. Não oferece POST/PUT, execução de
ferramentas ou acesso à API remota autenticada.

O frontend WebGpu é experimental. Não configure como único acesso operacional
sem validar GPU, navegador, foco, acessibilidade e fallbacks no ambiente real.

## Critérios para substituir as interfaces anteriores

1. Control Center: catálogo e campos, edição, diff, revisão, CSRF, gestão de
   modelos, configuração do Proxy e tratamento de concorrência.
2. Remote: login/pareamento, sessões, mensagens em streaming, upload,
   arquivos, tools, aprovações, agentes filhos, surfaces e histórico.
3. HUD: imagem+TTL, overlay, foco, acessibilidade, voz e reconexões.
4. Deploy: binários verificados nos três sistemas operacionais, testes WebGPU
   em browsers reais, atualização, rollback, testes de performance e revisão
   de licenças.

O acompanhamento completo está em
[rfdetoni/kitt#121](https://github.com/rfdetoni/kitt/issues/121).

**Não** desabilite a interface remota ou o Control Center atual antes dos
gates acima. Nenhum componente visual deve criar permissões sobre ferramentas
ou ultrapassar limites de orçamento e privacidade do Agent.
