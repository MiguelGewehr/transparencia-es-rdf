import requests

from transparencia_es_rdf.config import TIMEOUT_SEGUNDOS, URL_API_CKAN

def chamar(acao :str, **parametros) -> dict:

    resposta = requests.get(f'{URL_API_CKAN}/{acao}', params=parametros, timeout=TIMEOUT_SEGUNDOS)

    resposta.raise_for_status()

    corpo = resposta.json()

    if not corpo.get('success'):
        raise RuntimeError(f'A API recusou a {acao}: {corpo.get("error")}')

    return corpo['result']

def buscar_recurso(id_recurso: str) -> dict:
    return chamar('resource_show', id=id_recurso)

def buscar_pacote(id_pacote: str) -> dict:
    return chamar('package_show', id=id_pacote)