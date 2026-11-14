from transparencia_es_rdf.config import URL_BASE_DADOS, URL_PORTAL, VERSAO_GRAFO

def montar_uris(recurso: dict, nome_base: str) -> dict[str, str]:

    id_pacote = recurso['package_id']
    id_recurso = recurso['id']

    uri_pacote = f'{URL_PORTAL}/dataset/{id_pacote}'
    uri_distribuicao = f'{uri_pacote}/resource/{id_recurso}'
    uri_grafo = f'{URL_BASE_DADOS}/id/{nome_base}/grafo/{id_recurso}'
    uri_versao_grafo = f'{uri_grafo}/{VERSAO_GRAFO}'

    return {
        'pacote': uri_pacote,
        'distribuicao': uri_distribuicao,
        'grafo': uri_grafo,
        'versao_grafo': uri_versao_grafo,
    }