# -*- coding: utf-8 -*-
"""Carrega o ia/.env para dentro do ambiente.

Sem isto, os scripts leriam apenas variáveis exportadas no shell, e a
instrução do README ("coloque a chave em ia/.env") não funcionaria.
"""

import os
from pathlib import Path

ARQUIVO_ENV = Path(__file__).resolve().parent.parent / ".env"


def carregar_env() -> None:
    """Lê ia/.env, se existir, sem sobrescrever o que já veio do shell.

    A precedência importa: uma variável passada na linha de comando deve
    vencer o arquivo, para dar para testar uma configuração diferente sem
    editar o .env.
    """
    if not ARQUIVO_ENV.exists():
        return

    for linha in ARQUIVO_ENV.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        os.environ.setdefault(chave.strip(), valor.strip().strip("\"'"))
