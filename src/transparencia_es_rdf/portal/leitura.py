import csv
from pathlib import Path

def conferir_cabecalho(cabecalho: list[str], colunas_esperadas: list[str]) -> None:

    faltam = sorted(set(colunas_esperadas) - set(cabecalho))
    sobram = sorted(set(cabecalho) - set(colunas_esperadas))

    if faltam or sobram:
        raise ValueError(f'O cabeçalho do CSV não é o esperado. Faltam: {faltam}. Sobram: {sobram}.')

def ler_linhas(caminho: Path, colunas_esperadas: list[str], separador: str, codificacao: str):

    with open(caminho, encoding=codificacao, newline='') as arquivo:
        
        leitor = csv.DictReader(arquivo, delimiter=separador)

        conferir_cabecalho(leitor.fieldnames, colunas_esperadas)

        for linha in leitor:
            yield linha

