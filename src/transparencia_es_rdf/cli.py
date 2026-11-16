"""Linha de comando do projeto: o comando transparencia-es-rdf.

Uso (na raiz do repositório):
    transparencia-es-rdf converter receitas dados/receitas/amostra/amostra-receitas.csv saida/rdf/amostra-receitas.nt
    transparencia-es-rdf converter despesas dados/despesas/bruto/despesas2025.csv saida/rdf/despesas-2025.nt.gz
    transparencia-es-rdf turtle saida/rdf/amostra-receitas.nt saida/rdf/amostra-receitas.ttl
    transparencia-es-rdf metadados receitas 2025
    transparencia-es-rdf metadados despesas 2024 --arquivo restos-a-pagar
    transparencia-es-rdf formas despesas
    transparencia-es-rdf validar despesas dados/despesas/amostra/amostra-despesas.csv

Em Despesas, o mesmo comando converte e valida qualquer um dos quatro
arquivos (Despesas, RestosAPagar, OrcamentosDespesa e OrcamentosExecucoes):
o cabeçalho do CSV diz qual é.

Este arquivo só liga as peças: lê o que foi digitado, chama as funções das
outras pastas na ordem certa e mostra o resultado. Nenhuma regra de RDF mora aqui.
"""

import argparse
import csv
import time
from datetime import date
from pathlib import Path

from transparencia_es_rdf.config import PASTA_FORMAS, PASTA_METADADOS, PASTA_VALIDACAO
from transparencia_es_rdf.despesas import arquivo as arquivo_despesas
from transparencia_es_rdf.despesas import (conversor_despesas, conversor_orcamentos_despesa,
                                           conversor_orcamentos_execucoes, conversor_restos_a_pagar)
from transparencia_es_rdf.metadados.cabecalho import montar_cabecalho
from transparencia_es_rdf.metadados.uris import montar_uris
from transparencia_es_rdf.portal.api import buscar_pacote, buscar_recurso
from transparencia_es_rdf.portal.leitura import ler_cabecalho, ler_linhas
from transparencia_es_rdf.rdf.ntriples import abrir_saida
from transparencia_es_rdf.rdf.turtle import gravar_em_turtle
from transparencia_es_rdf.receitas import arquivo as arquivo_receitas
from transparencia_es_rdf.receitas import conversor as conversor_receitas
from transparencia_es_rdf.validacao.formas import gerar_formas, ler_ontologia
from transparencia_es_rdf.validacao.validador import validar_linhas

# Cada base tem a sua pasta, e o arquivo.py dela descreve o CSV.
ARQUIVO_DA_BASE = {
    'despesas': arquivo_despesas,
    'receitas': arquivo_receitas,
}
BASES = sorted(ARQUIVO_DA_BASE)

# Receitas tem um arquivo só. Despesas tem quatro, cada um com o seu
# conversor; os nomes são os de despesas/arquivo.py.
CONVERSOR_DO_ARQUIVO_DE_DESPESAS = {
    'despesas': conversor_despesas,
    'restos-a-pagar': conversor_restos_a_pagar,
    'orcamentos-despesa': conversor_orcamentos_despesa,
    'orcamentos-execucoes': conversor_orcamentos_execucoes,
}


def _milhares(numero: int) -> str:
    """1234567 vira '1.234.567'."""
    return f'{numero:,}'.replace(',', '.')


def _escolher_conversor(nome_base: str, entrada: Path):
    """As colunas, o conversor e o arquivo.py da base, para o CSV de entrada.

    Em Despesas, o cabeçalho do CSV diz qual dos quatro arquivos é este.
    """
    if not entrada.is_file():
        raise SystemExit(f'Arquivo não encontrado: {entrada}')

    arquivo_da_base = ARQUIVO_DA_BASE[nome_base]
    if nome_base == 'receitas':
        return arquivo_receitas.COLUNAS, conversor_receitas, arquivo_da_base

    cabecalho = ler_cabecalho(entrada, arquivo_da_base.SEPARADOR, arquivo_da_base.CODIFICACAO)
    nome_do_arquivo = arquivo_despesas.identificar_arquivo(cabecalho)
    print(f'Arquivo de Despesas: {nome_do_arquivo}')
    return (arquivo_despesas.COLUNAS_POR_ARQUIVO[nome_do_arquivo],
            CONVERSOR_DO_ARQUIVO_DE_DESPESAS[nome_do_arquivo], arquivo_da_base)


# ---------------------------------------------------------------------------
# Um comando por função, na ordem em que costumam ser usados.
# ---------------------------------------------------------------------------

def _converter(nome_base: str, entrada: Path, saida: Path) -> None:
    """Lê o CSV da base, escreve as triplas em N-Triples e mostra o relatório."""
    colunas, conversor, arquivo_da_base = _escolher_conversor(nome_base, entrada)
    linhas = ler_linhas(entrada, colunas, arquivo_da_base.SEPARADOR, arquivo_da_base.CODIFICACAO)

    inicio = time.perf_counter()
    with abrir_saida(saida) as destino:
        relatorio = conversor.converter_linhas(linhas, destino)
    segundos = time.perf_counter() - inicio

    print(f'{_milhares(relatorio["linhas_lidas"])} linhas lidas de {entrada}')
    print(f'{_milhares(relatorio["triplas_escritas"])} triplas gravadas em {saida} ({segundos:.0f} s)')
    if 'linhas_repetidas' in relatorio:       # só Receitas junta linhas repetidas
        print(f'Linhas repetidas, escritas uma vez só: {_milhares(relatorio["linhas_repetidas"])}')
    print('Entidades por classe:')
    for classe, quantidade in relatorio['entidades_por_classe'].items():
        print(f'  {classe:<46}{_milhares(quantidade):>10}')


def _gerar_turtle(entrada: Path, saida: Path) -> None:
    """Grava em Turtle um N-Triples pequeno, como a amostra, para leitura."""
    if not entrada.is_file():
        raise SystemExit(f'Arquivo não encontrado: {entrada}')
    quantidade = gravar_em_turtle(entrada, saida)
    print(f'{_milhares(quantidade)} triplas gravadas em {saida}')


def _gerar_metadados(nome_base: str, ano: int, nome_do_arquivo: str | None) -> None:
    """Busca o recurso e o pacote na API, monta o cabeçalho e grava em saida/metadados/.

    Em Despesas, nome_do_arquivo diz qual dos quatro arquivos ('despesas',
    'restos-a-pagar'...); sem ele, vale o arquivo Despesas. Em Receitas, não se usa.
    """
    if nome_base == 'despesas':
        nome_do_arquivo = nome_do_arquivo or 'despesas'
        ids_por_ano = arquivo_despesas.ID_RECURSO_POR_ARQUIVO_E_ANO[nome_do_arquivo]
    elif nome_do_arquivo is not None:
        raise SystemExit('A opção --arquivo só vale para despesas.')
    else:
        nome_do_arquivo = nome_base
        ids_por_ano = arquivo_receitas.ID_RECURSO_POR_ANO
    if ano not in ids_por_ano:
        anos = ', '.join(str(a) for a in sorted(ids_por_ano))
        raise SystemExit(f'Não há recurso de {nome_do_arquivo} para {ano}. Anos cadastrados: {anos}.')

    recurso = buscar_recurso(ids_por_ano[ano])
    pacote = buscar_pacote(recurso['package_id'])
    uris = montar_uris(recurso, nome_base)
    cabecalho = montar_cabecalho(recurso, pacote, uris, nome_base, data_criacao=date.today())

    PASTA_METADADOS.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_METADADOS / f'{nome_do_arquivo}-{ano}.ttl'
    cabecalho.serialize(destination=caminho, format='turtle')
    print(f'{len(cabecalho)} triplas gravadas em {caminho}')


def _gravar_formas(nome_base: str) -> None:
    """Gera as formas SHACL da base a partir da ontologia e grava em saida/formas/, para leitura.

    O comando validar não lê este arquivo: gera as formas de novo a cada vez.
    """
    formas = gerar_formas(ler_ontologia(nome_base), nome_base)
    PASTA_FORMAS.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_FORMAS / f'{nome_base}.ttl'
    formas.serialize(destination=caminho, format='turtle')
    print(f'{_milhares(len(formas))} triplas gravadas em {caminho}')


def _validar(nome_base: str, entrada: Path, linhas_por_lote: int) -> None:
    """Converte o CSV em lotes, valida cada lote com as formas e grava o resumo das violações.

    O resumo vai para a tela e para saida/validacao/<nome do CSV>.csv.
    """
    colunas, conversor, arquivo_da_base = _escolher_conversor(nome_base, entrada)
    ontologia = ler_ontologia(nome_base)
    formas = gerar_formas(ontologia, nome_base)
    linhas = ler_linhas(entrada, colunas, arquivo_da_base.SEPARADOR, arquivo_da_base.CODIFICACAO)

    inicio = time.perf_counter()
    resumo = validar_linhas(linhas, conversor, formas, ontologia, linhas_por_lote)
    segundos = time.perf_counter() - inicio

    print(f'{_milhares(resumo["linhas_lidas"])} linhas de {entrada} em {resumo["lotes"]} lote(s), '
          f'{_milhares(resumo["triplas_validadas"])} triplas validadas ({segundos:.0f} s)')
    violacoes = resumo['violacoes']
    if not violacoes:
        print('Nenhuma violação.')
    else:
        total = sum(violacao['quantidade'] for violacao in violacoes)
        print(f'{_milhares(total)} violações, em {len(violacoes)} regras:')
        for violacao in violacoes:
            print(f'  {_milhares(violacao["quantidade"]):>10}  {violacao["tipo"]:<22}'
                  f'{violacao["forma"]}  {violacao["regra"]}')

    PASTA_VALIDACAO.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_VALIDACAO / f'{entrada.stem}.csv'
    with open(caminho, 'w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=['forma', 'regra', 'tipo', 'quantidade', 'exemplo'])
        escritor.writeheader()
        escritor.writerows(violacoes)
    print(f'Resumo gravado em {caminho}')


def main() -> None:
    """Lê o que foi digitado no terminal e chama o comando pedido."""
    parser = argparse.ArgumentParser(
        prog='transparencia-es-rdf',
        description='Converte bases do Portal de Dados Abertos do ES para RDF.',
    )
    subcomandos = parser.add_subparsers(dest='comando', required=True)

    comando_converter = subcomandos.add_parser(
        'converter', help='converte o CSV de uma base em N-Triples')
    comando_converter.add_argument('base', choices=BASES, help='nome da base, ex.: receitas')
    comando_converter.add_argument('entrada', type=Path,
                                   help='CSV de entrada, ex.: dados/receitas/amostra/amostra-receitas.csv')
    comando_converter.add_argument('saida', type=Path,
                                   help='arquivo N-Triples de saída, ex.: saida/rdf/amostra-receitas.nt; '
                                        'se terminar em .gz, sai compactado')

    comando_turtle = subcomandos.add_parser(
        'turtle', help='grava em Turtle um N-Triples pequeno, como a amostra, para leitura')
    comando_turtle.add_argument('entrada', type=Path,
                                help='arquivo N-Triples, ex.: saida/rdf/amostra-receitas.nt')
    comando_turtle.add_argument('saida', type=Path,
                                help='arquivo Turtle de saída, ex.: saida/rdf/amostra-receitas.ttl')

    comando_metadados = subcomandos.add_parser(
        'metadados', help='grava o cabeçalho de metadados de uma base e ano (consulta a API do portal)')
    comando_metadados.add_argument('base', choices=BASES, help='nome da base, ex.: receitas')
    comando_metadados.add_argument('ano', type=int, help='ano do arquivo, ex.: 2025')
    comando_metadados.add_argument('--arquivo', choices=sorted(arquivo_despesas.COLUNAS_POR_ARQUIVO),
                                   help='só em despesas: qual dos quatro arquivos (sem a opção, o arquivo Despesas)')

    comando_formas = subcomandos.add_parser(
        'formas', help='grava as formas SHACL de uma base, geradas a partir da ontologia')
    comando_formas.add_argument('base', choices=BASES, help='nome da base, ex.: despesas')

    comando_validar = subcomandos.add_parser(
        'validar', help='converte o CSV de uma base em lotes e valida com as formas SHACL')
    comando_validar.add_argument('base', choices=BASES, help='nome da base, ex.: despesas')
    comando_validar.add_argument('entrada', type=Path,
                                 help='CSV de entrada, ex.: dados/despesas/amostra/amostra-despesas.csv')
    comando_validar.add_argument('--linhas-por-lote', type=int, default=10_000,
                                 help='linhas do CSV validadas de uma vez (padrão: 10000)')

    argumentos = parser.parse_args()
    if argumentos.comando == 'converter':
        _converter(argumentos.base, argumentos.entrada, argumentos.saida)
    elif argumentos.comando == 'turtle':
        _gerar_turtle(argumentos.entrada, argumentos.saida)
    elif argumentos.comando == 'metadados':
        _gerar_metadados(argumentos.base, argumentos.ano, argumentos.arquivo)
    elif argumentos.comando == 'formas':
        _gravar_formas(argumentos.base)
    elif argumentos.comando == 'validar':
        _validar(argumentos.base, argumentos.entrada, argumentos.linhas_por_lote)
