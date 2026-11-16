"""Linha de comando do projeto.

Uso:
    transparencia-es-rdf metadados receitas 2025
    transparencia-es-rdf metadados despesas 2024 --arquivo restos-a-pagar
    transparencia-es-rdf converter receitas dados/receitas/amostra/amostra-receitas.csv saida/amostra-receitas.nt
    transparencia-es-rdf converter despesas dados/despesa/amostra/amostra-despesas.csv saida/amostra-despesas.nt
    transparencia-es-rdf converter despesas dados/despesa/bruto/RestosAPagar-2024.csv saida/restos-a-pagar-2024.nt.gz
    transparencia-es-rdf formas despesas
    transparencia-es-rdf validar despesas dados/despesa/amostra/amostra-despesas.csv

Em Despesas, o mesmo comando converte qualquer um dos quatro arquivos
(Despesas, RestosAPagar, OrcamentosDespesa e OrcamentosExecucoes): o
cabeçalho do CSV diz qual é.

Este arquivo só liga as peças: lê o que foi digitado, chama as funções das
outras pastas na ordem certa e mostra o resultado. Nenhuma regra de RDF mora aqui.
"""

import argparse
import csv
import time
from datetime import date
from pathlib import Path

from transparencia_es_rdf.config import PASTA_SAIDA
from transparencia_es_rdf.despesas import arquivo as arquivo_despesas
from transparencia_es_rdf.despesas import conversor as conversor_despesas
from transparencia_es_rdf.despesas import conversor_orcamentos_despesa, conversor_orcamentos_execucoes
from transparencia_es_rdf.despesas import conversor_restos_a_pagar
from transparencia_es_rdf.metadados.cabecalho import montar_cabecalho
from transparencia_es_rdf.metadados.uris import montar_uris
from transparencia_es_rdf.portal.api import buscar_pacote, buscar_recurso
from transparencia_es_rdf.portal.leitura import ler_cabecalho, ler_linhas
from transparencia_es_rdf.rdf.ntriples import abrir_saida
from transparencia_es_rdf.receitas import arquivo as arquivo_receitas
from transparencia_es_rdf.receitas import conversor as conversor_receitas
from transparencia_es_rdf.rdf.turtle import gravar_em_turtle
from transparencia_es_rdf.validacao.formas import gerar_formas, ler_ontologia
from transparencia_es_rdf.validacao.validador import validar_linhas

# Cada base tem a sua pasta, com os mesmos nomes de arquivo.
ARQUIVO_DA_BASE = {
    'despesas': arquivo_despesas,
    'receitas': arquivo_receitas,
}
CONVERSOR_DA_BASE = {
    'despesas': conversor_despesas,
    'receitas': conversor_receitas,
}

# Os quatro arquivos de Despesas, cada um com o seu conversor. Os nomes são os
# de despesas/arquivo.py.
CONVERSOR_DO_ARQUIVO_DE_DESPESAS = {
    'despesas': conversor_despesas,
    'restos-a-pagar': conversor_restos_a_pagar,
    'orcamentos-despesa': conversor_orcamentos_despesa,
    'orcamentos-execucoes': conversor_orcamentos_execucoes,
}


def milhares(numero: int) -> str:
    """1234567 vira '1.234.567'."""
    return f'{numero:,}'.replace(',', '.')


def gerar_metadados(nome_base: str, ano: int, nome_do_arquivo: str | None = None) -> Path:
    """Busca o recurso e o pacote na API, monta o cabeçalho e grava o .ttl.

    Em Despesas, nome_do_arquivo diz qual dos quatro arquivos ('despesas',
    'restos-a-pagar'...); sem ele, vale o arquivo Despesas. Em Receitas, não se usa.
    """
    if nome_base == 'despesas':
        nome_do_arquivo = nome_do_arquivo or 'despesas'
        ids_por_ano = arquivo_despesas.ID_RECURSO_POR_ARQUIVO_E_ANO[nome_do_arquivo]
        nome_da_saida = nome_do_arquivo
    elif nome_do_arquivo is not None:
        raise SystemExit('A opção --arquivo só vale para despesas.')
    else:
        ids_por_ano = ARQUIVO_DA_BASE[nome_base].ID_RECURSO_POR_ANO
        nome_da_saida = nome_base
    if ano not in ids_por_ano:
        anos = ', '.join(str(a) for a in sorted(ids_por_ano))
        raise SystemExit(f'Não há recurso de {nome_da_saida} para {ano}. Anos cadastrados: {anos}.')

    recurso = buscar_recurso(ids_por_ano[ano])
    pacote = buscar_pacote(recurso['package_id'])

    uris = montar_uris(recurso, nome_base)
    cabecalho = montar_cabecalho(recurso, pacote, uris, nome_base, data_criacao=date.today())

    PASTA_SAIDA.mkdir(exist_ok=True)
    caminho = PASTA_SAIDA / f'{nome_da_saida}-{ano}.metadados.ttl'
    cabecalho.serialize(destination=caminho, format='turtle')
    print(f'{len(cabecalho)} triplas gravadas em {caminho}')
    return caminho


def escolher_conversor(nome_base: str, entrada: Path):
    """As colunas, o conversor e o módulo arquivo.py da base, para o CSV de entrada.

    Em Despesas, o cabeçalho do CSV diz qual dos quatro arquivos é este.
    """
    if not entrada.is_file():
        raise SystemExit(f'Arquivo não encontrado: {entrada}')

    arquivo_da_base = ARQUIVO_DA_BASE[nome_base]
    if nome_base == 'despesas':
        cabecalho = ler_cabecalho(entrada, arquivo_da_base.SEPARADOR, arquivo_da_base.CODIFICACAO)
        nome_do_arquivo = arquivo_da_base.identificar_arquivo(cabecalho)
        print(f'Arquivo de Despesas: {nome_do_arquivo}')
        return (arquivo_da_base.COLUNAS_POR_ARQUIVO[nome_do_arquivo],
                CONVERSOR_DO_ARQUIVO_DE_DESPESAS[nome_do_arquivo], arquivo_da_base)
    return arquivo_da_base.COLUNAS, CONVERSOR_DA_BASE[nome_base], arquivo_da_base


def converter(nome_base: str, entrada: Path, saida: Path) -> dict:
    """Lê o CSV da base, escreve as triplas em N-Triples e mostra o relatório."""
    colunas, conversor_da_base, arquivo_da_base = escolher_conversor(nome_base, entrada)
    linhas = ler_linhas(entrada, colunas, arquivo_da_base.SEPARADOR, arquivo_da_base.CODIFICACAO)
    inicio = time.perf_counter()
    with abrir_saida(saida) as destino:
        relatorio = conversor_da_base.converter_linhas(linhas, destino)
    segundos = time.perf_counter() - inicio

    print(f'{milhares(relatorio["linhas_lidas"])} linhas lidas de {entrada}')
    print(f'{milhares(relatorio["triplas_escritas"])} triplas gravadas em {saida} ({segundos:.0f} s)')
    if 'linhas_repetidas' in relatorio:       # só Receitas junta linhas repetidas
        print(f'Linhas repetidas, escritas uma vez só: {milhares(relatorio["linhas_repetidas"])}')
    print('Entidades por classe:')
    for classe, quantidade in relatorio['entidades_por_classe'].items():
        print(f'  {classe:<46}{milhares(quantidade):>10}')
    return relatorio

def gravar_formas(nome_base: str) -> Path:
    """Gera as formas SHACL da base a partir da ontologia e grava em Turtle."""
    formas = gerar_formas(ler_ontologia(nome_base), nome_base)
    PASTA_SAIDA.mkdir(exist_ok=True)
    caminho = PASTA_SAIDA / f'formas-{nome_base}.ttl'
    formas.serialize(destination=caminho, format='turtle')
    print(f'{milhares(len(formas))} triplas gravadas em {caminho}')
    return caminho


def validar(nome_base: str, entrada: Path, linhas_por_lote: int) -> dict:
    """Converte o CSV em lotes, valida cada lote com as formas e grava o resumo das violações.

    O resumo vai para a tela e para saida/<nome do CSV>.validacao.csv.
    """
    colunas, conversor_da_base, arquivo_da_base = escolher_conversor(nome_base, entrada)
    ontologia = ler_ontologia(nome_base)
    formas = gerar_formas(ontologia, nome_base)

    linhas = ler_linhas(entrada, colunas, arquivo_da_base.SEPARADOR, arquivo_da_base.CODIFICACAO)
    inicio = time.perf_counter()
    resumo = validar_linhas(linhas, conversor_da_base, formas, ontologia, linhas_por_lote)
    segundos = time.perf_counter() - inicio

    print(f'{milhares(resumo["linhas_lidas"])} linhas de {entrada} em {resumo["lotes"]} lote(s), '
          f'{milhares(resumo["triplas_validadas"])} triplas validadas ({segundos:.0f} s)')
    violacoes = resumo['violacoes']
    if not violacoes:
        print('Nenhuma violação.')
    else:
        total = sum(v['quantidade'] for v in violacoes)
        print(f'{milhares(total)} violações, em {len(violacoes)} regras:')
        for v in violacoes:
            print(f'  {milhares(v["quantidade"]):>10}  {v["tipo"]:<22}{v["forma"]}  {v["regra"]}')

    PASTA_SAIDA.mkdir(exist_ok=True)
    caminho = PASTA_SAIDA / f'{entrada.name.split(".")[0]}.validacao.csv'
    with open(caminho, 'w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=['forma', 'regra', 'tipo', 'quantidade', 'exemplo'])
        escritor.writeheader()
        escritor.writerows(violacoes)
    print(f'Resumo gravado em {caminho}')
    return resumo


def gerar_turtle(entrada: Path, saida: Path) -> None:
    """Grava em Turtle um N-Triples pequeno, como a amostra, para leitura."""
    if not entrada.is_file():
        raise SystemExit(f'Arquivo não encontrado: {entrada}')
    quantidade = gravar_em_turtle(entrada, saida)
    print(f'{milhares(quantidade)} triplas gravadas em {saida}')


def main() -> None:
    """Lê o que foi digitado no terminal e chama o comando pedido."""
    parser = argparse.ArgumentParser(
        prog='transparencia-es-rdf',
        description='Converte bases do Portal de Dados Abertos do ES para RDF.',
    )
    subcomandos = parser.add_subparsers(dest='comando', required=True)

    comando_metadados = subcomandos.add_parser(
        'metadados', help='grava o cabeçalho de metadados de uma base e ano')
    comando_metadados.add_argument('base', choices=sorted(ARQUIVO_DA_BASE),
                                   help='nome da base, ex.: receitas')
    comando_metadados.add_argument('ano', type=int, help='ano do arquivo, ex.: 2025')
    comando_metadados.add_argument('--arquivo', choices=sorted(arquivo_despesas.COLUNAS_POR_ARQUIVO),
                                   help='só em despesas: qual dos quatro arquivos (sem a opção, o arquivo Despesas)')

    comando_converter = subcomandos.add_parser(
        'converter', help='converte o CSV de uma base em N-Triples')
    comando_converter.add_argument('base', choices=sorted(CONVERSOR_DA_BASE),
                                   help='nome da base, ex.: receitas')
    comando_converter.add_argument('entrada', type=Path,
                                   help='CSV de entrada, ex.: dados/receitas/amostra/amostra-receitas.csv')
    comando_converter.add_argument('saida', type=Path,
                                   help='arquivo N-Triples de saída; se terminar em .gz, sai compactado')

    comando_turtle = subcomandos.add_parser(
        'turtle', help='grava em Turtle um N-Triples pequeno, como a amostra, para leitura')
    comando_turtle.add_argument('entrada', type=Path,
                                help='arquivo N-Triples, ex.: saida/amostra-receitas.nt')
    comando_turtle.add_argument('saida', type=Path,
                                help='arquivo Turtle de saída, ex.: saida/amostra-receitas.ttl')

    comando_formas = subcomandos.add_parser(
        'formas', help='gera as formas SHACL de uma base a partir da ontologia')
    comando_formas.add_argument('base', choices=sorted(CONVERSOR_DA_BASE),
                                help='nome da base, ex.: despesas')

    comando_validar = subcomandos.add_parser(
        'validar', help='converte o CSV de uma base em lotes e valida com as formas SHACL')
    comando_validar.add_argument('base', choices=sorted(CONVERSOR_DA_BASE),
                                 help='nome da base, ex.: despesas')
    comando_validar.add_argument('entrada', type=Path,
                                 help='CSV de entrada, ex.: dados/despesa/amostra/amostra-despesas.csv')
    comando_validar.add_argument('--linhas-por-lote', type=int, default=10_000,
                                 help='linhas do CSV validadas de uma vez (padrão: 10000)')

    argumentos = parser.parse_args()

    if argumentos.comando == 'metadados':
        gerar_metadados(argumentos.base, argumentos.ano, argumentos.arquivo)
    elif argumentos.comando == 'converter':
        converter(argumentos.base, argumentos.entrada, argumentos.saida)
    elif argumentos.comando == 'turtle':
        gerar_turtle(argumentos.entrada, argumentos.saida)
    elif argumentos.comando == 'formas':
        gravar_formas(argumentos.base)
    elif argumentos.comando == 'validar':
        validar(argumentos.base, argumentos.entrada, argumentos.linhas_por_lote)