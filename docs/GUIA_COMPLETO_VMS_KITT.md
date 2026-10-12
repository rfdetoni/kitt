# Guia completo de máquinas virtuais no K.I.T.T.

> **Escopo:** Agent CLI 0.86.8 / ecossistema 0.15.6, host Linux com QEMU.
> Este documento descreve os comandos **existentes** e distingue os fluxos disponíveis daqueles que ainda exigem provisionamento manual ou validação com máquinas reais.
>
> **Importante:** o helper não baixa ISOs, não fabrica Tiny11, não instala automaticamente Windows/Linux a partir de uma ISO e não dá acesso do guest aos arquivos privados do host.

**Novo no 0.15.6:** o assistente também aceita `--backend docker` ou `--backend podman`. Para QEMU dentro de contêiner, visualização no navegador, imagens Linux `base/wine/full` pré-construídas e instalação opcional, consulte o **[Guia Docker/Podman + RE Toolbox](VM_CONTAINERS_DOCKER_PODMAN.md)**. O QEMU nativo continua o padrão.

## Índice

1. [Mapa de possibilidades e estado atual](#1-mapa-de-possibilidades-e-estado-atual)
2. [Requisitos e instalação do KITT](#2-requisitos-e-instalação-do-kitt)
3. [Helper unificado `kitt vm create`](#3-helper-unificado-kitt-vm-create)
4. [Windows: ISO oficial, Tiny11 ou QCOW2](#4-windows-iso-oficial-tiny11-ou-qcow2)
5. [Linux: distro e perfil de engenharia reversa](#5-linux-distro-e-perfil-de-engenharia-reversa)
6. [Agente autônomo em VM separada](#6-agente-autônomo-em-vm-separada)
7. [Laboratório de engenharia reversa e evidências](#7-laboratório-de-engenharia-reversa-e-evidências)
8. [Referência de flags, recursos e diretórios](#8-referência-de-flags-recursos-e-diretórios)
9. [Segurança, rede, backups e snapshots](#9-segurança-rede-backups-e-snapshots)
10. [Receitas práticas](#10-receitas-práticas)
11. [Solução de problemas](#11-solução-de-problemas)
12. [Limitações e próximos passos](#12-limitações-e-próximos-passos)

## 1. Mapa de possibilidades e estado atual

O KITT oferece **três funções distintas**, que não devem ser confundidas:

| Finalidade | Entrada | Imagem de origem | Resultado | Estado |
| --- | --- | --- | --- | --- |
| Assistente geral para guests | `kitt vm create` (ou `kitt vm wizard`) | ISO/QCOW2 **do usuário** | Configuração e disco de VM Windows ou Linux | Implementado |
| QEMU em Docker/Podman | `kitt vm create --backend podman` | ISO/QCOW2 **do usuário** | QEMU com noVNC e disco privado persistente | Implementado no Agent 0.86.8; teste real de guest ainda pendente |
| Linux RE toolbox (contêiner) | `kitt vm container build/pull/toolbox` | Imagem Debian pré-construída | Ghidra, Frida, Wine, GDB etc. conforme perfil | Implementado; não é uma VM |

| Windows de referência/teste | `kitt vm windows prepare/install/start` | ISO ou QCOW2 **do usuário** | Windows com UEFI/TPM e VNC local | Implementado; instalação do OS interativa |
| Linux para engenharia reversa | `kitt vm linux prepare/install/start` | ISO ou QCOW2 **do usuário** | Linux com perfil de ferramentas sugerido | Implementado; instalação do OS interativa |
| Agente KITT isolado | `kitt vm doctor/run` | QCOW2 **já preparada**, com KITT/SSH | Execução de missão em snapshot descartável | Supervisor implementado; guest deve ser provisionado |
| Verificar dependências VM pelo instalador | `--with-vm-lab` | Nenhuma | Verifica QEMU/OpenSSH | Implementado; **não** instala pacotes do host |
| Provisionamento automático de Debian para o **agente** | `kitt vm prepare` | Debian Cloud | Instalação e preparação de imagem-base | **Não faz parte da versão release 0.15.5**; não confundir com os assistentes existentes |
| Integração E2E Windows/Wine/Ghidra/Frida | Ferramentas de laboratório | Guests configurados | Experimentação real | Adaptadores iniciais; **não validado de ponta a ponta** |

A VM **Linux de engenharia reversa** é independente da VM **Linux do agente**. A primeira é um laboratório para ferramentas e amostras; a segunda dá ao KITT autonomia sobre seu próprio ambiente descartável.

O modo habitual `kitt` / `kitt -p` **não usa automaticamente uma VM** nem muda suas permissões por causa desses comandos opcionais.

## 2. Requisitos e instalação do KITT

### Requisitos do host

- **Linux x86_64**. Os assistentes de VM QEMU foram desenvolvidos para o host Linux; o modo Windows dentro da VM não significa que o host pode ser Windows.
- `qemu-system-x86_64` e `qemu-img`; `/dev/kvm` acessível é recomendado para desempenho, mas QEMU pode usar emulação TCG (muito mais lenta).
- Cliente VNC para instalar/administrar guests gráficos. Somente o endereço **127.0.0.1** é utilizado pelos wizards.
- Para **Windows**, firmware UEFI **OVMF** e emulador de TPM **swtpm**.
- Para o **agente autônomo**, cliente OpenSSH, imagem QCOW2 standalone previamente provisionada, chave SSH privada e known_hosts fixados.
- Uma ISO ou QCOW2 que você tem direito de usar e espaço em disco suficiente; não é necessário carregar a imagem inteira em memória.

Em Debian/Ubuntu, os nomes de pacotes costumam ser:

```sh
sudo apt update
sudo apt install qemu-system-x86 qemu-utils ovmf swtpm openssh-client
```

Para visualizar a instalação, use seu cliente VNC preferido. Nomes e versões de pacotes podem diferir na sua distribuição.

### Instalar o KITT

Exemplo usando o canal de release:

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh \
  | sh -s -- --preset full --channel release --yes
```

A opção de instalação abaixo **apenas verifica** os pré-requisitos da VM do agente (QEMU e SSH) e inclui o Agent CLI. Ela **não cria** imagens Debian/Windows, não instala pacotes com sudo e não modifica configurações de firewall:

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh \
  | sh -s -- --preset full --channel release --with-vm-lab --yes
```

Para conferir a versão e os comandos disponíveis na sua instalação:

```sh
kitt --version
kitt vm --help
kitt vm create --help
kitt vm windows --help
kitt vm linux --help
```

**Canais:** `release` usa commits fixados em `ecosystem.release.json`; uma instalação antiga pode não conter `kitt vm create`. O comando do helper depende do Agent CLI **0.86.7 ou superior**. Atualize usando o instalador antes de testar.

## 3. Helper unificado `kitt vm create`

### Uso interativo

```sh
kitt vm create
```

`kitt vm wizard` é um alias equivalente:

```sh
kitt vm wizard
```

O assistente conduz, nesta ordem:

1. Escolher **1 — Windows** ou **2 — Linux**.
2. Digitar o caminho de um arquivo **.iso** ou **.qcow2** existente (aceita `~/...` e nomes com espaços).
3. Checar existência, formato pela extensão e rejeitar links simbólicos.
4. Encaminhar para o wizard específico: edição Windows ou distro/perfil Linux; memória, CPUs, disco e destino.
5. Exibir um resumo e solicitar confirmação.
6. Criar o diretório da VM, seu disco QCOW2 e `profile.json`, e mostrar o próximo comando de instalação.

O helper **não** inicializa automaticamente a instalação do guest nem oferece shell irrestrito ao host. Se a imagem já for uma QCOW2 com sistema instalado, basta criar a cópia e usar `start` diretamente.

### Uso sem interação: scripts e CI

**Windows oficial (ISO):**

```sh
kitt vm create \
  --os windows \
  --source "$HOME/ISOs/Windows11.iso" \
  --variant official \
  --memory-mib 4096 --cpus 2 --disk-gib 64 \
  --yes
```

**Tiny11 ou Tiny11 Core previamente construído pelo usuário:**

```sh
kitt vm create --os windows \
  --source "$HOME/ISOs/tiny11.iso" --variant tiny11 \
  --destination "$HOME/.local/share/kitt/vm/windows-tiny" --yes
```

A opção `--variant tiny11` **não** executa o Tiny11 Builder: é uma etiqueta da imagem fornecida. Para Tiny11 Core, use `--variant tiny11-core`.

**Linux Debian com perfil Wine:**

```sh
kitt vm create --os linux \
  --source "$HOME/ISOs/debian.iso" \
  --distro debian --tools wine \
  --destination "$HOME/.local/share/kitt/vm/linux-wine" \
  --memory-mib 4096 --cpus 2 --disk-gib 64 --yes
```

**Linux a partir de um QCOW2 já instalado:**

```sh
kitt vm create --os linux \
  --source "$HOME/VMs/ubuntu-base.qcow2" \
  --kind qcow2 --distro ubuntu --tools re \
  --destination "$HOME/.local/share/kitt/vm/ubuntu-re" --yes
```

Regras do modo não interativo:

- Passe **`--os windows|linux`**, **`--source CAMINHO`** e **`--yes`**.
- `--kind` é opcional; quando informado, deve corresponder a `.iso` ou `.qcow2`.
- `--variant` pertence apenas ao Windows; `--distro` e `--tools` pertencem apenas ao Linux.
- Se o diretório de destino já existir, o assistente **recusa sobrescrever** a VM e seus dados.

## 4. Windows: ISO oficial, Tiny11 ou QCOW2

### Fontes suportadas

- ISO oficial do Windows 11, fornecida pelo usuário.
- ISO Tiny11/Tiny11 Core já obtida ou construída pelo usuário (o KITT **não** constrói Tiny11).
- Disco QCOW2 de Windows já instalado, **sem backing file externo**, sem arquivo de dados externo e não criptografado.

Você é responsável pelo licenciamento do Windows e pela procedência da imagem. Para comparações fiéis de APIs Win32, use **Windows oficial** como principal referência: versões reduzidas podem remover funcionalidades relevantes.

### Comando especializado de preparação

```sh
kitt vm windows prepare
```

Com opções explícitas:

```sh
kitt vm windows prepare \
  --source "$HOME/ISOs/Windows11.iso" \
  --kind iso --variant official \
  --memory-mib 6144 --cpus 4 --disk-gib 80 \
  --destination "$HOME/.local/share/kitt/vm/windows-reference" \
  --yes
```

O comando cria o disco separado `windows.qcow2`, copia uma imagem inicial de variáveis UEFI, prepara diretório para o estado de TPM 2.0 e grava `profile.json` com hash SHA-256 da mídia original. A ISO permanece somente leitura e não é alterada.

O wizard procura modelos OVMF em locais conhecidos. Caso seu Linux instale em outro local, o comando especializado `windows prepare` admite `--ovmf-code` e `--ovmf-vars` (ambos juntos); o helper unificado pode ser complementado pelo comando especializado quando esses parâmetros forem necessários.

### Instalar Windows pela primeira vez

```sh
kitt vm windows install \
  --profile "$HOME/.local/share/kitt/vm/windows-reference/profile.json" \
  --vnc-display 1
```

Abra o cliente VNC em **127.0.0.1:5901** e complete o Windows Setup. O assistente não pula automaticamente a seleção de edição, credenciais ou termos da licença.

Depois da instalação:

```sh
kitt vm windows start \
  --profile "$HOME/.local/share/kitt/vm/windows-reference/profile.json"
```

O disco instalado, NVRAM UEFI e estado TPM são **persistentes**. Guarde uma cópia limpa depois da instalação para experimentos recuperáveis. Não confunda essa VM mutável com os snapshots descartáveis do supervisor do agente.

**Windows offline:** a VM é iniciada com `-nic none` (sem placa de rede virtual), VNC exposto somente em loopback, sem montagem de diretórios do host. O helper Windows não configura compartilhamento de arquivos, acesso à rede interna nem integração automática de Frida.

### Importar Windows já instalado

```sh
kitt vm windows prepare \
  --source "$HOME/VMs/windows11.qcow2" \
  --kind qcow2 --variant official \
  --destination "$HOME/.local/share/kitt/vm/windows-import" --yes

kitt vm windows start \
  --profile "$HOME/.local/share/kitt/vm/windows-import/profile.json"
```

A imagem QCOW2 é **copiada**, não usada diretamente; dados externos, backing chains e criptografia não são aceitos pelo wizard. Importar uma imagem não garante que ela tenha drivers compatíveis, boot configurado, licença ativada ou SSH/guest agent disponível.

## 5. Linux: distro e perfil de engenharia reversa

### Distros disponíveis no menu

`debian`, `ubuntu`, `kali`, `fedora`, `arch`, `other`. A escolha identifica o **modelo de script de pacotes**; não baixa a distro nem prova que uma ISO corresponde ao rótulo informado.

### Perfis disponíveis

| Perfil | O que entrega |
| --- | --- |
| `minimal` | VM básica, com roteiro mínimo; adicionar ferramentas manualmente |
| `re` | Script de instalação de compiladores, GDB, binutils, strace, clang/LLDB, Java/Python, CMake etc. |
| `wine` | Perfil de RE com tentativa de incluir pacotes de Wine da distro |
| `full` | RE + Wine; **Ghidra e Frida continuam exigindo instalação específica** |

Os perfis geram o arquivo `setup-re-tools.sh`. O wizard **não executa esse script no host ou no guest**, não instala pacotes automaticamente e não promete disponibilidade idêntica entre versões das distros. Revise e transfira o roteiro para dentro do guest apenas quando necessário.

### Preparar Linux

```sh
kitt vm linux prepare
```

Ou fornecer parâmetros:

```sh
kitt vm linux prepare \
  --source "$HOME/ISOs/kali.iso" \
  --kind iso --distro kali --tools full \
  --memory-mib 4096 --cpus 2 --disk-gib 64 \
  --destination "$HOME/.local/share/kitt/vm/kali-re" --yes
```

Por padrão, o disco `linux.qcow2` é privado e persistente para você instalar a distribuição. O caminho do script gerado será:

```text
~/.local/share/kitt/vm/kali-re/setup-re-tools.sh
```

### Instalar, iniciar e habilitar rede temporariamente

```sh
kitt vm linux install \
  --profile "$HOME/.local/share/kitt/vm/kali-re/profile.json"
```

Use VNC em **127.0.0.1:5902** para concluir o instalador da distro.

```sh
kitt vm linux start \
  --profile "$HOME/.local/share/kitt/vm/kali-re/profile.json"
```

Normalmente a VM inicia **sem interface de rede**. Para baixar pacotes dentro dela, existe a opção explícita de NAT:

```sh
kitt vm linux start \
  --profile "$HOME/.local/share/kitt/vm/kali-re/profile.json" \
  --network
```

**Aviso:** `--network` habilita rede de saída por NAT. Utilize somente para setup confiável e reinicie **sem** essa flag antes de investigar binários potencialmente maliciosos. O perfil de rede temporária não é uma garantia de contenção de um guest comprometido.

### Linux QCOW2 importado

```sh
kitt vm linux prepare --source "$HOME/VMs/debian-re.qcow2" \
  --kind qcow2 --distro debian --tools re \
  --destination "$HOME/.local/share/kitt/vm/linux-import" --yes

kitt vm linux start \
  --profile "$HOME/.local/share/kitt/vm/linux-import/profile.json"
```

Nesse caso o sistema já deve estar instalado no QCOW2. Não use `linux install` com um `--kind qcow2`: a instalação a partir de ISO só é válida com ISO fornecida.

## 6. Agente autônomo em VM separada

Esse fluxo é **diferente** dos dois assistentes de ISO. A ideia é executar o KITT com maior autonomia **dentro** de um ambiente cujo acesso a arquivos, rede e credenciais foi limitado pelo host.

### Pré-requisitos

- Uma imagem QCOW2 independente preparada pelo operador, sem backing file, com Linux, KITT e SSH.
- Conta SSH sem root, com chave autorizada por um comando remoto fixo (`kitt.vm_worker`), chave privada `0600` e host key previamente confiada.
- Workspace **dentro** da imagem, e gateway de IA controlado pelo host, se for necessário usar modelo remoto.
- Uma política do supervisor que verifica digest SHA-256 da imagem, CPUs/memória, prazos e encaminhamentos.

O projeto de **bootstrap automático Debian Minimal para o agente** é distinto deste guia e **ainda não foi promovido à release 0.15.5**. `--with-vm-lab` não cria a imagem.

### Exemplo de perfil do supervisor

Crie `~/.kitt/vm/profile.json` com permissão `0600` e substitua os caminhos/hash conforme a sua VM:

```json
{
  "version": 1,
  "image": "/home/usuario/VMs/kitt-agent.qcow2",
  "sha256": "SUBSTITUA_PELO_SHA256_REAL_COM_64_CARACTERES_HEXADECIMAIS",
  "ssh_key": "/home/usuario/.ssh/kitt-vm",
  "known_hosts": "/home/usuario/.ssh/kitt-known-hosts",
  "ssh_user": "kitt",
  "host_key_alias": "kitt-sandbox",
  "memory_mib": 4096,
  "cpus": 2,
  "timeout_seconds": 1200,
  "boot_seconds": 120,
  "gateway_port": 3000
}
```

O texto do `sha256` acima é propositalmente **inválido**: calcule o digest do seu arquivo e substitua. Não use a amostra diretamente.

```sh
sha256sum "$HOME/VMs/kitt-agent.qcow2"
chmod 600 "$HOME/.kitt/vm/profile.json"
kitt vm doctor --profile "$HOME/.kitt/vm/profile.json"
```

### Executar uma missão autônoma

```sh
kitt vm run \
  --profile "$HOME/.kitt/vm/profile.json" \
  --goal "Compilar o projeto, implementar a tarefa e executar os testes necessários"
```

O QEMU cria um snapshot gravável **descartável** da imagem-base, usa rede `restrict=on` (com IPv6 desabilitado), oferece SSH **somente por uma porta loopback** e, se autorizado por `gateway_port`, um encaminhamento específico para o gateway local de IA.

O guest executa um contrato do Agent CLI por meio de um comando SSH fixo, sem interpretar o objetivo como uma linha de shell no host. A VM é encerrada ao final. A saída é **resultado de execução**, não uma promoção automática de alterações ao repositório confiável.

- `gateway_port = 0`: desabilita encaminhamento ao gateway do host; modelo remoto normalmente fica inacessível.
- Porta não zero: permite somente o encaminhamento configurado; o gateway deve aplicar autenticação, limites de tokens e proteção contra saída de dados.
- `--allow all` *no worker guest* não concede acesso à máquina host ou autorização automática de push. Nunca trate isso como isolador suficiente sem QEMU/SSH/firewall corretamente configurados.

**Atenção:** o supervisor não transfere automaticamente seu workspace do host para dentro do guest, nem devolve um patch verificado para o host. Se você não preparou esses dados na imagem, a VM não terá o projeto a modificar. Alterações feitas apenas no snapshot descartável não são preservadas.

## 7. Laboratório de engenharia reversa e evidências

O ecossistema também inclui um plugin MCP opcional de engenharia reversa e ferramentas executadas por **operador** nos guests. Esses componentes são diferentes do `kitt vm create`.

### Habilitar plugin opcional

```sh
kitt plugins enable kitt-reverse-engineering
```

Reinicie o Agent. O plugin MCP oferece superfícies de inspeção **somente leitura**, como análise de metadados PE/ELF, comparação de evidências, consulta de observações e planejamento de missões; não concede um shell remoto arbitrário.

### Ciclo de investigação recomendado

1. Prepare a **VM Windows oficial de referência**, a **VM Linux/Wine candidata** e, opcionalmente, a VM do agente autônomo.
2. Faça um snapshot limpo dos sistemas instalados **fora do fluxo de configuração inicial**.
3. Compile pequenos probes Win32 autorizados e registre o mesmo digest do executável em manifestos locais dos guests.
4. Execute o probe original no Windows e o candidato no Linux/Wine.
5. Registre observações JSON limitadas, valide digest/identidade de probe e compare divergências.
6. Utilize a evidência para propor mudanças no código-fonte e testar novamente; só publique após avaliação independente.

O controlador de comparação usa SSH com **forced command**. Seus perfis e manifestos exigem provisionamento prévio; o wizard que cria discos Windows/Linux **não** instala automaticamente o executor remoto ou organiza o laboratório.

### Ferramentas disponíveis separadamente

- **Ghidra Headless**: adaptador de guest para exportar um conjunto limitado de funções/endereço; requer Ghidra instalado e guest isolado.
- **Frida**: adaptador de guest com script fixo para observar nomes de chamadas Win32; requer Frida instalado e amostra autorizada por SHA.
- **Wine**: runner de probes Windows em Linux com prefixo temporário e deadline.
- **Evidências**: recibos verificáveis por hash e banco local SQLite de observações, que pode ser consultado de forma limitada pelo MCP.

**O que ainda não está demonstrado:** inicialização autônoma de toda a cadeia Windows + Linux/Wine + Ghidra + Frida, instrumentação de uma aplicação Windows real e correção de comportamento de ponta a ponta. Um hash de recibo também **não** comprova a identidade ou integridade do guest.

Detalhes adicionais no código-fonte do Agent:
[guia de laboratório](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/REVERSE_ENGINEERING_GUEST_LAB.md),
[missões autônomas](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/REVERSE_ENGINEERING_AUTONOMY.md) e
[modelo de segurança](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/VM_AUTONOMY_SECURITY.md).

## 8. Referência de flags, recursos e diretórios

### Comandos

| Comando | Uso |
| --- | --- |
| `kitt vm create` | Helper interativo para Windows ou Linux |
| `kitt vm wizard` | Alias de `create` |
| `kitt vm windows prepare` | Wizard específico da VM Windows |
| `kitt vm windows install` | Inicia ISO Windows via QEMU/VNC |
| `kitt vm windows start` | Inicia disco Windows instalado |
| `kitt vm linux prepare` | Wizard específico da VM Linux RE |
| `kitt vm linux install` | Inicia ISO da distro via QEMU/VNC |
| `kitt vm linux start` | Inicia disco Linux instalado |
| `kitt vm doctor` | Valida perfil/imagem do agente autônomo |
| `kitt vm run` | Executa uma missão dentro da VM descartável do agente |

### Flags do helper `create` / `wizard`

| Flag | Valor | Aplicação |
| --- | --- | --- |
| `--os` | `windows`, `linux` | Seleção do guest; obrigatória no modo não interativo |
| `--source` | Caminho ISO/QCOW2 | Mídia fornecida pelo usuário |
| `--kind` | `iso`, `qcow2` | Opcional, deve corresponder à extensão |
| `--destination` | Diretório | Estado da VM; não sobrescreve existente |
| `--memory-mib` | Inteiro em MiB | Memória RAM; padrão 4096 |
| `--cpus` | Inteiro | vCPUs; padrão 2 |
| `--disk-gib` | Inteiro em GiB | Disco a criar para ISO; padrão 64 |
| `--variant` | `official`, `tiny11`, `tiny11-core`, `custom` | Só Windows |
| `--distro` | `debian`, `ubuntu`, `kali`, `fedora`, `arch`, `other` | Só Linux |
| `--tools` | `minimal`, `re`, `wine`, `full` | Só Linux |
| `--yes` | Sem valor | Pula perguntas; requer `--os` e `--source` |

Recursos aceitos nos wizards:

| Guest | RAM | vCPUs | Disco para ISO |
| --- | --- | --- | --- |
| Windows | 4096–16384 MiB | 2–8 | 32–256 GiB |
| Linux RE | 1024–16384 MiB | 1–8 | 16–256 GiB |

Os limites do **supervisor do agente** são outros e vêm do perfil JSON; não são substituídos pelos flags `create`.

### Flags especializadas

- `kitt vm windows prepare --ovmf-code CAMINHO --ovmf-vars CAMINHO`: modelos UEFI customizados.
- `kitt vm windows install/start --vnc-display N`: display VNC de 1 a 99; padrão 1.
- `kitt vm linux install/start --vnc-display N`: display VNC de 1 a 99; padrão 2.
- `kitt vm linux install/start --network`: habilita NAT temporariamente; **não** usar com executáveis suspeitos.
- `kitt vm doctor --profile PERFIL`: preflight do supervisor de agente.
- `kitt vm run --profile PERFIL --goal TEXTO`: executa objetivo dentro da VM do agente.
- `--with-vm-lab`: opção do instalador para verificação de pré-requisitos, não um substituto de `vm create`.

### Diretórios padrões

```text
~/.local/share/kitt/vm/
├── windows-oracle/
│   ├── profile.json
│   ├── windows.qcow2
│   ├── OVMF_VARS.fd
│   └── tpm/
└── linux-re/
    ├── profile.json
    ├── linux.qcow2
    └── setup-re-tools.sh
```

Esses diretórios são independentes do possível `~/.kitt/vm/profile.json` usado pelo **supervisor da VM do agente**. É possível criar múltiplas VMs de referência usando `--destination` diferente para cada uma.

## 9. Segurança, rede, backups e snapshots

### Controles existentes nos wizards

- Os diretórios de estado são privados para o usuário; arquivos de perfil e disco são protegidos conforme o host Linux.
- Fontes devem ser arquivos regulares; links simbólicos e caminhos com delimitadores inseguros para QEMU são rejeitados.
- QCOW2 com backing chain/arquivo externo é rejeitado. A mídia original não é editada.
- Windows usa UEFI e TPM virtual, sem placa de rede, montagem do host ou encaminhamento de portas.
- Linux inicia offline; NAT só é habilitado com `--network`.
- VNC escuta somente em `127.0.0.1`; **não tem autenticação adicional** nessa configuração. Não repasse essa porta a redes públicas.

### Cuidados adicionais

- **Não confunda um disco persistente dos wizards com sandbox descartável.** Faça baseline/snapshot próprio antes de instrumentar executáveis desconhecidos.
- Não exponha `~/.ssh`, Docker/Podman socket, compartilhamentos graváveis ou tokens GitHub dentro de uma VM não confiável.
- Não use o host principal para executar amostras potencialmente maliciosas.
- Fixe a procedência de ISOs/discos por digest obtido de fonte confiável. O hash gerado pelo wizard identifica os bytes fornecidos, mas **não garante autenticidade**.
- Com Windows reduzido, resultados negativos de APIs podem indicar componentes ausentes, não incompatibilidade do Linux; mantenha uma referência oficial.
- Revise os scripts de pacotes antes de executar dentro do guest, especialmente em distribuições rolling release.
- Mantenha hipervisor, firmware, kernel e pacotes da host atualizados. VM não é uma garantia absoluta contra escapes.

### Persistência e restauração

| Modalidade | Mutações do guest |
| --- | --- |
| `vm windows start/install` | Persistem no QCOW2 da VM Windows |
| `vm linux start/install` | Persistem no QCOW2 da VM Linux RE |
| `vm run` (agente) | Snapshot temporário; alterações não são promovidas automaticamente |

Para manter um baseline de guest instalado, desligue a VM normalmente e copie o disco/estado de firmware com a VM parada, garantindo que não existam processos QEMU ativos. Não modifique arquivos QCOW2 em uso.

## 10. Receitas práticas

### A. Preparar referência Windows oficial + Linux Wine

```sh
kitt vm create --os windows --source "$HOME/ISOs/Windows11.iso" \
  --variant official --destination "$HOME/.local/share/kitt/vm/windows-reference" --yes
kitt vm create --os linux --source "$HOME/ISOs/debian.iso" \
  --distro debian --tools wine \
  --destination "$HOME/.local/share/kitt/vm/debian-wine" --yes

kitt vm windows install \
  --profile "$HOME/.local/share/kitt/vm/windows-reference/profile.json"
# Após concluir o instalador e desligar a VM Windows:
kitt vm linux install \
  --profile "$HOME/.local/share/kitt/vm/debian-wine/profile.json"
```

Após ambas as instalações, configure ferramentas e o runner de experimentos dentro dos guests por um processo autorizado. O wizard, sozinho, não prepara as APIs nem executa comparações.

### B. Tiny11 apenas como teste secundário

```sh
kitt vm create --os windows --source "$HOME/ISOs/tiny11.iso" \
  --variant tiny11 \
  --destination "$HOME/.local/share/kitt/vm/tiny11-test" --yes

kitt vm windows install \
  --profile "$HOME/.local/share/kitt/vm/tiny11-test/profile.json"
```

Use `--variant tiny11-core` para uma ISO Core já fornecida. **Não** utilize o Core como fonte exclusiva da semântica das APIs Windows.

### C. Importar uma distro Linux RE já preparada

```sh
kitt vm create --os linux --source "$HOME/VMs/re-baseline.qcow2" \
  --distro debian --tools full \
  --destination "$HOME/.local/share/kitt/vm/re-copy" --yes

kitt vm linux start \
  --profile "$HOME/.local/share/kitt/vm/re-copy/profile.json"
```

### D. Criar uma VM somente pelo terminal, sem desktop no host

O host pode continuar **headless**. A instalação inicial via ISO precisa de um cliente VNC que alcance o loopback do host (por exemplo, por um túnel SSH administrado externamente). O KITT não abre um servidor VNC público nem faz automaticamente um instalador desassistido.

Se você já possui um QCOW2 inicializado e corretamente configurado, `start` pode dispensar instalação via ISO.

### E. Usar o KITT para programar normalmente

```sh
cd /caminho/do/meu/projeto
kitt
# ou
kitt -p "Corrija a validação e rode os testes essenciais"
```

Nenhum dos comandos acima cria uma VM. O fluxo de VM é explicitamente `kitt vm ...`.

## 11. Solução de problemas

| Sintoma | Causa provável / ação |
| --- | --- |
| `kitt vm create` não aparece | Agent antigo; verificar `kitt --version` e atualizar para 0.86.7+ |
| "requires a Linux QEMU host" | Você está no Windows/macOS; executar o wizard num host Linux apropriado |
| `qemu-system-x86_64` ou `qemu-img` ausente | Instalar pacotes QEMU de sua distro |
| "UEFI OVMF firmware not found" | Instalar `ovmf` ou passar `--ovmf-code` e `--ovmf-vars` ao wizard Windows especializado |
| `swtpm` ausente | Instalar emulador TPM virtual no host Linux |
| "ISO/QCOW2 ... arquivo regular" | Conferir caminho, existência e links simbólicos; usar arquivo real não symlink |
| "Unknown source format" | Apenas extensões `.iso` e `.qcow2` no helper unificado |
| "kind mismatch" | `--kind iso` deve acompanhar `.iso`; `qcow2` deve acompanhar `.qcow2` |
| "QCOW2 backing file" | Converter/achatar o disco para uma cópia standalone confiável, com o guest desligado |
| "destination exists" | Reutilizar a VM existente com `start` ou escolher outro `--destination`; o wizard não sobrescreve |
| VNC não conecta | QEMU deve estar rodando; usar 127.0.0.1:5901 para Windows, :5902 para Linux; verificar porta ocupada |
| Windows 11 reclama de TPM | Verificar `swtpm`, OVMF e o perfil criado; executar em host compatível |
| VM está muito lenta | Confirmar KVM disponível; emulação TCG pode ser lenta, especialmente Windows |
| Linux não tem internet | É intencional; se necessário, iniciar **Linux** com `--network` só durante setup |
| `setup-re-tools.sh` não instalou ferramentas | O script é **gerado**, não executado automaticamente; levar ao guest e executar com autorização |
| Ghidra/Frida ausentes | Não são instalados pelo wizard; requerem processo de instalação separado |
| `vm doctor` rejeita `profile.json` do wizard | Perfis **diferentes**: `vm doctor/run` aceitam o perfil do agente, não dos guests Windows/Linux |
| `vm run` terminou e perdi minhas mudanças | Snapshot do agente é descartável; recuperação/promoção de patches não está automatizada |
| Preciso usar várias VMs | Passe um `--destination` exclusivo para cada Windows/Linux guest |

## 12. Limitações e próximos passos

Esta documentação descreve os comandos efetivamente implementados no Agent 0.86.7:

- Criação e importação de discos/estados de guests Windows/Linux, por helper único ou comandos especializados.
- Inicialização gráfica offline e instalação **interativa** do sistema via ISO.
- Supervisor Linux para execução autônoma com imagem **preparada previamente**.
- Ferramentas isoladas de engenharia reversa e registro/comparação inicial de evidências.

**Não implementado ou não validado completamente:** download e instalação automáticos de Windows/Tiny11; instalação desassistida de qualquer ISO genérica; injeção e atualização do runner dentro das VMs criadas pelos wizards; instalação garantida de Ghidra/Frida; snapshots automatizados dos guests Windows/Linux; transferência segura de projeto/patches entre host e VM do agente; bateria E2E real com QEMU + Windows + Wine + Ghidra/Frida.

O propósito do helper é **facilitar o setup do laboratório sem comprometer o modo tradicional de programação do KITT e sem ampliar a autoridade do guest sobre o host**.

---
**Referências no Agent CLI:** [helper Windows/Linux](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/VM_CREATION_HELPER.md) · [VM Windows](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/WINDOWS_VM_WIZARD.md) · [VM Linux RE](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/LINUX_RE_VM_WIZARD.md) · [supervisor autônomo](https://github.com/rfdetoni/kitt-agent-cli/blob/main/docs/VM_SUPERVISOR.md).
