import argparse
from datetime import date
from pathlib import Path

from transparencia_es_rdf.config import PASTA_SAIDA
from transparencia_es_rdf.metadados.cabecalho import montar_cabecalho
from transparencia_es_rdf.metadados.uris import montar_uris
from transparencia_es_rdf.portal.api import buscar_pacote, buscar_recurso
from transparencia_es_rdf.receitas import arquivo as arquivo_receitas

ARQUIVO_DA_BASE = {
    'receitas' : arquivo_receitas
}

def gerar_metadados(nome_base: str, ano: int) -> Path:

    ids_por_ano = ARQUIVO_DA_BASE[nome_base].ID_RECURSO_POR_ANO

    if ano not in ids_por_ano:
        anos = ', '.join(str(a) for a in sorted(ids_por_ano))
        raise(SystemExit(f'Não há recurso de {nome_base} para {ano}. 'f'Anos cadastrados: {anos}.'))

    recurso = buscar_recurso(ids_por_ano[ano])
    pacote = buscar_pacote(recurso['package_id'])

    uris = montar_uris(recurso, nome_base)
    cabecalho = montar_cabecalho(recurso, pacote, uris, nome_base, data_criacao=date.today())

    PASTA_SAIDA.mkdir(exist_ok=True)
    caminho = PASTA_SAIDA / f'{nome_base}-{ano}.metadados.ttl'
    cabecalho.serialize(destination=caminho, format='turtle')
    print(f'{len(cabecalho)} triplas gravadas em {caminho}')
    return caminho

def main() -> None:

    parser = argparse.ArgumentParser(
        prog='transparencia-es-rdf',
        description='Converte bases do Portal de Dados Abertos do ES para RDF.'
    )

    subcomandos = parser.add_subparsers(dest='comando', required=True)

    comando_metadados = subcomandos.add_parser('metadados', help='grava o cabeçalho de metadados de uma base e ano')
    comando_metadados.add_argument('base', choices=sorted(ARQUIVO_DA_BASE), help='nome da base, ex.: receitas')
    comando_metadados.add_argument('ano', type=int, help='ano do arquivo, ex.: 2025')

    argumentos =  parser.parse_args()

    if argumentos.comando == 'metadados':
        gerar_metadados(argumentos.base, argumentos.ano)