"""Os endereços que o RDF usa: os da ontologia, os padrões da web e o dos dados.

Os namespaces da ontologia têm de ser idênticos, caractere por caractere, aos
que os arquivos de ontologia/out/ttl/ declaram (base-receitas.ttl,
base-despesas.ttl e nucleo.ttl), inclusive o "#" do final. Se a ontologia
mudar de endereço, só muda aqui.
"""

from urllib.parse import quote

from transparencia_es_rdf.config import URL_BASE_DADOS

# Namespaces da ontologia congelada em ontologia/: base-receitas do commit
# 15ffde5; base-despesas e nucleo do commit 90c3354.
NAMESPACE_RECEITAS = 'https://example.org/ontologia-portal-transparencia-es/base-receitas#'
NAMESPACE_DESPESAS = 'https://example.org/ontologia-portal-transparencia-es/base-despesas#'
NAMESPACE_NUCLEO = 'https://example.org/ontologia-portal-transparencia-es/nucleo#'

# Vocabulários padrão: rdf:type e os dois tipos de literal do XML Schema.
RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
XSD_DECIMAL = 'http://www.w3.org/2001/XMLSchema#decimal'
XSD_DATETIME = 'http://www.w3.org/2001/XMLSchema#dateTime'

# Começo das URIs dos dados (receitas, registros, UGs...): http://localhost:8000/id/
BASE_DAS_URIS_DE_DADOS = f'{URL_BASE_DADOS}/id/'


def propriedade(namespace: str, classe: str, atributo: str) -> str:
    """URI de uma propriedade do jeito que o .ttl escreve: Classe.atributo.

    Exemplo: propriedade(NAMESPACE_RECEITAS, 'ContaContabil', 'codigo') devolve
    'https://example.org/ontologia-portal-transparencia-es/base-receitas#ContaContabil.codigo'.
    """
    return f'{namespace}{classe}.{atributo}'


def uri_de_dado(*partes: str) -> str:
    """URI de um recurso dos dados: a base mais as partes, separadas por "/".

    O quote() troca por %XX o que não pode aparecer numa URI (espaço, acento,
    "/" dentro de um código). Exemplo:
    uri_de_dado('conta-contabil', '621200000') devolve
    'http://localhost:8000/id/conta-contabil/621200000'.
    """
    return BASE_DAS_URIS_DE_DADOS + '/'.join(quote(parte, safe='') for parte in partes)