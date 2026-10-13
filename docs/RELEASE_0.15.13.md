# KITT 0.15.13 — corrigir detecção de Python no RE lab

## Falha observada

Após instalar o KITT Full e o REA com sucesso, o instalador retornava:

```text
K.I.T.T. installed; RE lab incomplete: KITT Agent CLI must be installed before provisioning RE lab
```

**Causa:** `installer/re_lab.py` rejeitava `~/.local/share/kitt/.venv-agent/bin/python` sempre que fosse link simbólico. O `python -m venv` em Linux normalmente cria `bin/python` como link para um interpretador válido. A checagem identificava erroneamente uma instalação concluída como ausente.

O mesmo defeito estava em `installer/vm_containers.py` no fluxo opcional de `--vm-pull-images`.

## Correção

Ambos os fluxos agora aceitam um link simbólico cujo destino seja um arquivo existente (verificado por `Path.is_file()`), preservando a rejeição de arquivos inexistentes e links quebrados. Nenhuma opção adicional nem modificação no Agent CLI é necessária.

Regressões: provisionar um laboratório RE com `bin/python` simbólico e realizar a preparação de pull de imagens QEMU/toolbox com o mesmo layout.

## Recuperar instalação anterior

Não apague os dados em `~/.local/share/kitt`, os discos Windows ou os volumes Docker existentes. Reexecute o **mesmo comando oficial** depois que a versão 0.15.13 estiver na `main`:

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

O instalador mantém os pins dos componentes da versão 0.15.12; somente o instalador raiz é alterado. O Docker, KVM, a instalação inicial do Windows e a autenticação real no guest ainda precisam ser validados no host do operador.
