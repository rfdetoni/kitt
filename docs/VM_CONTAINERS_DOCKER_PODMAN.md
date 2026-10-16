> **KITT 0.16.10:** O caminho canônico é `./install.sh --preset full --with-re-lab --yes --accept-windows-license`, que chama `kitt re lab setup` no Agent CLI 0.88.7. Para apagar dados, use exclusivamente `kitt re lab recreate --scope windows --destroy-data --dry-run` e execute com `--confirm TOKEN --accept-license`. As opções antigas `--re-oracle-recreate` do instalador são rejeitadas. Verificação Windows/KVM real permanece **UNVERIFIED** até `kitt re lab verify --full` no host autorizado.

## Atualização 0.15.7 — segurança e coordenação entre VMs

O console noVNC passa a exigir senha aleatória por VM, inclusive para acesso
pela rede Docker. Consulte explicitamente:

```sh
kitt vm container credentials --profile /caminho/da/vm/profile.json
```

`kitt vm container start` aguarda prontidão do console; logs persistem
após falhas e são arquivados antes de um novo start. A VM usa o digest da
imagem QEMU configurado em vez de depender de tag mutável.

Snapshots offline, com validação SHA-256 do disco e cópia UEFI/TPM:

```sh
kitt vm container snapshot --profile /caminho/da/vm/profile.json --action save --name clean
kitt vm container snapshot --profile /caminho/da/vm/profile.json --action restore --name clean --yes
```

Canal opcional, somente host → guest, para testes SSH por forced command:

```sh
kitt vm create --os windows --backend podman --source ~/ISOs/Windows11.iso --probe-port 18008 --yes
kitt vm lab doctor --hosts /caminho/hosts.json
kitt vm lab run --workspace /projeto --mission /projeto/mission.json --hosts /caminho/hosts.json
```

É necessário configurar autenticação SSH e o executor de probes dentro
do guest; a porta restrita não instala SSH nem libera shell remoto.
Sem `--probe-port`, a VM permanece sem NIC.

Os perfis da versão 0.86.8 não contêm os novos segredos e pins; preserve
os discos e recrie os perfis pelo wizard, sem editar o JSON manualmente.

**O pull de imagem opcional não anula uma instalação do KITT bem-sucedida:**
o instalador informa a falha de download separadamente.

# VMs Windows/Linux em Docker ou Podman — imagens Linux RE pré-construídas

Este recurso está disponível a partir do **KITT Agent CLI 0.86.11** e é **opcional**. O KITT continua usando QEMU nativo por padrão. Há dois conceitos separados: **QEMU dentro do contêiner**, que inicia um Windows/Linux completo a partir de mídia fornecida pelo usuário, e **toolbox Linux Debian pronta**, que contém ferramentas de análise mas não é uma VM.

## 1. Imagens pré-construídas

| Imagem | Finalidade | Conteúdo |
| --- | --- | --- |
| `kitt/qemu-vm:0.86.10` | Executar Windows/Linux no QEMU via Docker/Podman | QEMU + UEFI/TPM virtual + noVNC |
| `kitt/linux-re:base-0.86.10` | Análise e desenvolvimento | GDB, LLDB, GCC/clang, Java, Python, Git, binutils, CMake etc. |
| `kitt/linux-re:wine-0.86.10` | Teste Wine e cross-compile Win32 | Base + Wine64 + MinGW |
| `kitt/linux-re:full-0.86.10` | Reverse engineering geral | Wine + Frida 17.23.3 + Ghidra 12.1.4 (SHA-256 verificado) + REA 6.4.0 e Node.js 24.11 |

Essas imagens são construídas pela CI e configuradas para publicação no GHCR após merge na `main` do Agent. A disponibilidade pública do pacote depende de a publicação ter sido concluída; em caso de falha, há build local.

## 2. Instalar backend opcional

É preciso um host Linux com Docker Engine ou Podman funcionando. Para VMs com boa performance, o usuário deve poder acessar `/dev/kvm`.

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh \
  | sh -s -- --preset full --channel release --with-vm-containers \
      --vm-container-runtime podman --yes
```

Para também solicitar download **explícito** das imagens pré-construídas:

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh \
  | sh -s -- --preset full --channel release --with-vm-containers \
      --vm-container-runtime podman --vm-pull-images \
      --vm-container-image-profile full --yes
```

`--with-vm-containers` não instala Docker/Podman, não concede root e não executa contêineres privilegiados. `--vm-pull-images` é opcional e pode falhar se GHCR estiver inacessível; nesse caso faça build local.

## 3. Preparar imagens localmente (Docker ou Podman)

```sh
kitt vm container doctor --runtime podman
kitt vm container build --runtime podman --image qemu
kitt vm container build --runtime podman --image toolbox --profile full
```

Substitua `podman` por `docker` se desejar. O perfil `full` é pesado, pois Ghidra e Frida são incluídos na imagem. Para menos espaço, utilize `base` ou `wine`.

## 4. Criar VM Windows a partir de sua ISO

```sh
kitt vm create --os windows --backend podman \
  --source "$HOME/ISOs/Windows11.iso" --memory-mib 4096 \
  --cpus 2 --disk-gib 64 --port 18006 --yes
kitt vm container start \
  --profile "$HOME/.local/share/kitt/vm-containers/windows-podman/profile.json" --install
```

Abra **http://127.0.0.1:18006/vnc.html** para completar o Windows Setup. Após desligar Windows, inicie sem `--install` para utilizar o disco persistente.

## 5. Criar VM Linux com Docker

```sh
kitt vm create --os linux --backend docker \
  --source "$HOME/ISOs/debian.iso" --memory-mib 2048 \
  --cpus 2 --disk-gib 32 --port 18007 --yes
kitt vm container start \
  --profile "$HOME/.local/share/kitt/vm-containers/linux-docker/profile.json" --install
```

Abra **http://127.0.0.1:18007/vnc.html**. Depois de instalar a distribuição, inicie sem `--install`.

```sh
kitt vm container status --profile /caminho/do/profile.json
kitt vm container logs --profile /caminho/do/profile.json
kitt vm container stop --profile /caminho/do/profile.json
```

## 6. Abrir toolbox Linux com ferramentas já prontas

```sh
kitt vm container toolbox --runtime podman --profile full \
  --workspace "$HOME/projetos/binarios-autorizados"
```

Esse toolbox é um contêiner, **não uma VM**. Ele compartilha o kernel Linux do host. É adequado para analisar arquivos autorizados, mas não para executar amostras potencialmente maliciosas; estas exigem VM isolada descartável. A execução do toolbox usa rede desativada e capabilities removidas.

## 7. Segurança e limites atuais

- QEMU guest inicia **sem placa de rede**, mas o **contêiner QEMU** utiliza bridge networking para servir noVNC somente em `127.0.0.1`. Isso não bloqueia automaticamente a saída de rede do contêiner; utilize firewall do host quando necessário.
- NoVNC exige autenticação por VM: não exponha a porta publicamente.
- Contêineres não usam `--privileged` ou socket de engine compartilhado. Acesso a `/dev/kvm` é opcional e depende de permissões já existentes; `--allow-tcg` permite emulação lenta, de forma explícita.
- ISO e QCOW2 são fornecidos pelo operador; KITT não baixa Windows, não executa Tiny11 Builder e não instala automaticamente aplicativos dentro da ISO.
- Disco do guest é persistente entre reinicializações; snapshots offline estão disponíveis com `kitt vm container snapshot`, mas testes reais em seu host ainda são necessários.

Para especificações e opções avançadas, leia também o [guia técnico completo no Agent CLI](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/VM_DOCKER_PODMAN.md) e o [guia geral de VMs do KITT](GUIA_COMPLETO_VMS_KITT.md).

## REA disponível diretamente no toolbox `full` (0.15.8)

A imagem Linux `full` inclui `rea-agents@6.4.0` e Node.js 24.11, instalados em estágio separado no build Docker/Podman. Os perfis `base` e `wine` não recebem Node/REA. O launcher 0.86.11 fornece um HOME/XDG temporário gravável mesmo sob UID não root, sem expor o diretório pessoal do host. Isso não instala o REA automaticamente na VM Windows, na ISO Linux ou no host onde o KITT executa.

```sh
kitt vm container pull --runtime podman --image toolbox --profile full
kitt vm container toolbox --runtime podman --profile full --workspace "$HOME/projetos/analise-autorizada"
# Dentro do container:
rea --version
rea doctor --provider ghidra --json
rea analyze-javascript-application /workspace/aplicacao --json
rea inspect-managed-artifact /workspace/assembly.dll --json
```

O REA via MCP **no host** continua opt-in: instalar o CLI de forma independente no mesmo ambiente do processo KITT e depois executar `kitt plugins enable kitt-rea`. O novo `rea_workflow` fornece sugestões de operações do REA para binários nativos, JavaScript/Electron, .NET, comparação de versões, dumps e PCAP sem executar diretamente. As operações continuam passando por política de ferramentas e aprovação; evidências canônicas do REA e desconhecidos são preservados no Evidence v2 do KITT. Consulte a [documentação técnica do Agent](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/REA.md).

O toolbox é um contêiner com kernel compartilhado, não substitui QEMU para execução de binários suspeitos. Os testes de CI comprovam a construção e execução básica dos CLI; um ensaio com guest Windows/Linux reais continua necessário.

## REA no preset completo do instalador KITT

Além da imagem Docker/Podman `full`, o comando `--preset full` do instalador raiz agora instala `rea-agents@6.4.0` no prefixo privado do próprio KITT, caso um Node compatível e npm estejam disponíveis. Essa instalação não usa `npm install -g` no prefixo global e não habilita o MCP automaticamente. Para ativar no workspace autorizado, execute `kitt plugins enable kitt-rea`.

Para instalar REA com outro preset use `--with-rea`. Para excluir do preset completo use `--skip-rea`. A falta de Node/npm ou a falha de download não cancela a instalação já concluída dos componentes centrais do KITT: uma mensagem específica indica que o REA ficou pendente. Nenhuma instalação implícita modifica o Node ou o prefixo global do npm. Consulte [notas da release](RELEASE_0.15.8.md).

## Reproducible Windows 11 Oracle lab (next release)

The full installer can now automate the **initial** Windows OpenSSH
configuration and a benign SHA-pinned Win32 probe using Dockur /oem, without
changing the existing, default RE lab provisioning flow.

For a brand-new test lab:

    ./install.sh --preset full --channel release --with-re-lab \
      --re-runtime docker --re-oracle-bootstrap \
      --accept-windows-license --yes

For a disposable existing managed Windows lab (DELETES Windows disk/data):

    ./install.sh --preset full --channel release --with-re-lab \
      --re-runtime docker --re-oracle-bootstrap --re-oracle-recreate \
      --accept-windows-license --yes

The second command leaves the KITT-managed Linux toolbox intact. Both require
an explicit Windows license/consent flag. The installer delegates to
Agent CLI kitt re oracle bootstrap, which verifies the KITT-owned container
and its private storage, compiles the fixed event synchronization pilot in
the managed MinGW toolbox, pins generated SSH identities, creates OEM files,
and boots a new Windows 11 using the local Dockur image.

Only 127.0.0.1:8006 (console) and 127.0.0.1:2222 (probe-only Windows SSH) are
published. OpenSSH allows a nonadmin local user with public-key authentication
and ForceCommand bound to a read-only probe inventory or SHA-pinned probe.run.
The guest does not need a Python installation to serve requests.

Provisioning returns status PROVISIONING, **never oracle_ready=true**. The
operator checks its generated private hosts.json and manifest SHA using
kitt re oracle doctor, then invokes the opt-in fixed Windows/Wine pilot only
after the SSH handshake succeeds. Real first-boot Windows, firewall and
Features-on-Demand verification is not covered by an installer unit test.

No unknown binaries should be executed in the Linux toolbox, because Docker
shares its kernel with the host; isolated disposable QEMU VMs are required for
hostile or untrusted code. Private keys, Windows ISO/disk and credentials must
never be committed or included in telemetry.

The older --with-re-lab path **without** --re-oracle-bootstrap keeps the
existing Dockur guest intact and does not expose SSH. The new flags must not
be used on Windows guests whose data must be preserved.
