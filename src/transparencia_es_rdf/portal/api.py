"""Consulta à API do CKAN, o sistema por trás do dados.es.gov.br.

Só o comando metadados usa a API. A conversão lê o CSV já baixado.
"""

import requests

from transparencia_es_rdf.config import TIMEOUT_SEGUNDOS, URL_API_CKAN


def _chamar_api(acao: str, **parametros) -> dict:
    """Chama uma ação da API (resource_show, package_show) e devolve o 'result' da resposta.

    Para com um erro se a API não responder, se a resposta não for 200 ou se o
    CKAN disser que a ação falhou (success = false).
    """
    resposta = requests.get(f'{URL_API_CKAN}/{acao}', params=parametros, timeout=TIMEOUT_SEGUNDOS)
    resposta.raise_for_status()
    corpo = resposta.json()
    if not corpo.get('success'):
        raise RuntimeError(f'A API recusou a {acao}: {corpo.get("error")}')
    return corpo['result']


def buscar_recurso(id_recurso: str) -> dict:
    """O recurso (um arquivo CSV do portal): nome, formato, link, data de modificação..."""
    return _chamar_api('resource_show', id=id_recurso)


def buscar_pacote(id_pacote: str) -> dict:
    """O pacote (o conjunto de arquivos de uma base): título, órgão e licença."""
    return _chamar_api('package_show', id=id_pacote)
