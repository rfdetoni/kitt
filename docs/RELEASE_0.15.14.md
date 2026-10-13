# KITT 0.15.14 — login automático do Windows Dockur

## Padrões documentados

O [Dockur Windows](https://github.com/dockur/windows/blob/master/docs/environment.md) documenta `USERNAME=Docker`, `PASSWORD=admin` e `AUTOLOGIN=Y` como padrões. O [README oficial](https://github.com/dockur/windows#how-do-i-configure-the-username-and-password) confirma o usuário e a senha.

O KITT agora usa esses valores **na primeira instalação de um guest novo**, substituindo `USERNAME=Kitt`, senha aleatória de 32 caracteres e `AUTOLOGIN=N`. O login automático evita digitar senhas no noVNC, que nem sempre aceita colagem de texto no login Windows.

Essa conta fraca só é adequada a um laboratório de teste local, isolado de redes e dados reais. O console web continua publicado em `127.0.0.1:8006`, mas isso não garante isolamento de rede do Windows.

## Instalar

Requisitos: Linux, Docker Engine, `/dev/kvm`, `/dev/net/tun` e os pré-requisitos do build nativo KITT.

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh |
  sh -s -- \
    --preset full \
    --channel release \
    --with-re-lab \
    --re-runtime docker \
    --re-profile full \
    --re-windows dockurr \
    --re-windows-version 11 \
    --yes
```

Na primeira execução o Dockur ainda precisa baixar e instalar o Windows. Depois, o esperado é login automático. Para login manual: **usuário Docker, senha admin**. A configuração gerenciada fica em `~/.local/share/kitt/re-lab/windows.env`, modo `0600`.

## Migração de um Windows que já usa Kitt + senha aleatória

**Mudar variáveis Docker não redefine usuários ou o logon do Windows já instalado.** Para preservar o disco existente, o novo instalador recusa tratar o guest legado como se já tivesse aplicado os novos padrões.

Se deseja **substituir a VM Windows antiga por uma instalação limpa**, preservando o disco como backup, execute no host Linux:

```bash
set -euo pipefail
LAB="$HOME/.local/share/kitt/re-lab"
STAMP="$(date +%Y%m%d-%H%M%S)"
if docker container inspect kitt-re-win11 >/dev/null 2>&1; then
  docker update --restart=no kitt-re-win11
  docker stop -t 120 kitt-re-win11
  docker rm kitt-re-win11
fi
if [ -d "$LAB/windows" ]; then
  mv -- "$LAB/windows" "$LAB/windows.backup.$STAMP"
fi
if [ -f "$LAB/windows.env" ]; then
  mv -- "$LAB/windows.env" "$LAB/windows.env.backup.$STAMP"
fi
echo "Backup Windows preservado em: $LAB"
```

Em seguida execute o comando de instalação acima novamente. Ele mantém o KITT, o workspace e o contêiner Linux Full, reutilizando as imagens já disponíveis quando possível. Não execute essa migração se ainda precisa usar a VM antiga imediatamente; faça um backup externo adicional ou altere a conta dentro do próprio Windows.

O instalador não deleta discos automaticamente, não tenta modificar contas antigas e não promete validar o login real do Windows. A instalação e autenticação do guest devem ser confirmadas no host Docker/KVM.

## Verificação

```bash
docker ps --filter label=dev.kitt.re-lab=v1
docker logs -f kitt-re-win11
docker exec -it kitt-re-full /bin/sh
grep -E '^(USERNAME|PASSWORD|AUTOLOGIN)=' "$HOME/.local/share/kitt/re-lab/windows.env"
```

Essa release altera o instalador raiz, documentação e testes; os pins dos módulos continuam iguais aos da 0.15.13.
