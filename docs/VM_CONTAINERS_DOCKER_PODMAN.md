# VMs Windows/Linux em Docker ou Podman — imagens Linux RE pré-construídas

Este recurso está disponível a partir do **KITT Agent CLI 0.86.8** e é **opcional**. O KITT continua usando QEMU nativo por padrão. Há dois conceitos separados: **QEMU dentro do contêiner**, que inicia um Windows/Linux completo a partir de mídia fornecida pelo usuário, e **toolbox Linux Debian pronta**, que contém ferramentas de análise mas não é uma VM.

## 1. Imagens pré-construídas

| Imagem | Finalidade | Conteúdo |
| --- | --- | --- |
| `kitt/qemu-vm:0.86.8` | Executar Windows/Linux no QEMU via Docker/Podman | QEMU + UEFI/TPM virtual + noVNC |
| `kitt/linux-re:base-0.86.8` | Análise e desenvolvimento | GDB, LLDB, GCC/clang, Java, Python, Git, binutils, CMake etc. |
| `kitt/linux-re:wine-0.86.8` | Teste Wine e cross-compile Win32 | Base + Wine64 + MinGW |
| `kitt/linux-re:full-0.86.8` | Reverse engineering geral | Wine + Frida 17.23.3 + Ghidra 12.1.4 (SHA-256 verificado) |

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
- NoVNC não tem autenticação adicional: não exponha a porta publicamente.
- Contêineres não usam `--privileged` ou socket de engine compartilhado. Acesso a `/dev/kvm` é opcional e depende de permissões já existentes; `--allow-tcg` permite emulação lenta, de forma explícita.
- ISO e QCOW2 são fornecidos pelo operador; KITT não baixa Windows, não executa Tiny11 Builder e não instala automaticamente aplicativos dentro da ISO.
- Disco do guest é persistente entre reinicializações; snapshot/rollback verificado e testes reais em seu host ainda são etapas separadas.

Para especificações e opções avançadas, leia também o [guia técnico completo no Agent CLI](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/VM_DOCKER_PODMAN.md) e o [guia geral de VMs do KITT](GUIA_COMPLETO_VMS_KITT.md).
