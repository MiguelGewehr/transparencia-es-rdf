from urllib.parse import quote

from transparencia_es_rdf.config import URL_BASE_DADOS

NAMESPACE_RECEITAS = 'https://example.org/ontologia-portal-transparencia-es/base-receitas#'
NAMESPACE_NUCLEO = 'https://example.org/ontologia-portal-transparencia-es/nucleo#'

RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
XSD_DECIMAL = 'http://www.w3.org/2001/XMLSchema#decimal'
XSD_DATETIME = 'http://www.w3.org/2001/XMLSchema#dateTime'

BASE_DAS_URIS_DE_DADOS = f'{URL_BASE_DADOS}/id/'

def propriedade(namespace: str, classe: str, atributo: str) -> str:
    return f'{namespace}{classe}.{atributo}'

def uri_de_dado(*partes: str) -> str:
    return BASE_DAS_URIS_DE_DADOS + '/'.join(quote(parte, safe='') for parte in partes)

