"""Leitura dos arquivos CSV do portal, linha a linha.

As linhas são entregues uma de cada vez (yield), sem carregar o arquivo
inteiro na memória: o arquivo de Despesas de 2025 tem 1,5 GB.
"""

import csv
from pathlib import Path

# Coluna que a leitura acrescenta a cada linha: a posição dela no arquivo,
# contando de 1 a partir da primeira linha depois do cabeçalho. Receitas usa
# esse número nas URIs, porque o arquivo não tem uma coluna de identificador.
COLUNA_NUMERO_DA_LINHA = 'numeroDaLinha'


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
    """Confere o cabeçalho e entrega cada linha do CSV como um dicionário coluna -> texto.

    Cada linha ganha também a coluna numeroDaLinha, com a sua posição no
    arquivo. A numeração é feita aqui, e não no conversor, porque o validar
    converte o arquivo em lotes, e um contador no conversor recomeçaria em 1
    a cada lote.
    """
    with open(caminho, encoding=codificacao, newline='') as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=separador)
        _conferir_cabecalho(leitor.fieldnames, colunas_esperadas)
        for numero, linha in enumerate(leitor, start=1):
            linha[COLUNA_NUMERO_DA_LINHA] = str(numero)
            yield linha
