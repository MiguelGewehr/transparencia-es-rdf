"""Leitura dos arquivos CSV do portal, linha a linha.

As linhas são entregues uma de cada vez (yield), sem carregar o arquivo
inteiro na memória: o arquivo de Despesas de 2025 tem 1,5 GB.
"""

import csv
from pathlib import Path


def _conferir_cabecalho(cabecalho: list[str], colunas_esperadas: list[str]) -> None:
    """Para com um erro se o CSV não tiver exatamente as colunas esperadas (em qualquer ordem).

    Se o portal mudar uma coluna, é melhor parar aqui do que converter errado.
    """
    faltam = sorted(set(colunas_esperadas) - set(cabecalho))
    sobram = sorted(set(cabecalho) - set(colunas_esperadas))
    if faltam or sobram:
        raise ValueError(f'O cabeçalho do CSV não é o esperado. Faltam: {faltam}. Sobram: {sobram}.')


def ler_cabecalho(caminho: Path, separador: str, codificacao: str) -> list[str]:
    """Só a primeira linha do CSV: os nomes das colunas."""
    with open(caminho, encoding=codificacao, newline='') as arquivo:
        return next(csv.reader(arquivo, delimiter=separador))


def ler_linhas(caminho: Path, colunas_esperadas: list[str], separador: str, codificacao: str):
    """Confere o cabeçalho e entrega cada linha do CSV como um dicionário coluna -> texto."""
    with open(caminho, encoding=codificacao, newline='') as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=separador)
        _conferir_cabecalho(leitor.fieldnames, colunas_esperadas)
        yield from leitor
