from datetime import date

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS, OWL, PROV, RDF, RDFS, VANN, XSD

from transparencia_es_rdf.config import AUTOR, IDIOMA, URL_BASE_DADOS, VERSAO_GRAFO

PREFIXOS = {
    'dcat': DCAT,
    'dcterms': DCTERMS,
    'owl': OWL,
    'prov': PROV,
    'rdf': RDF,
    'rdfs': RDFS,
    'vann': VANN,
    'xsd': XSD,
}

def criar_grafo_vazio() -> Graph:

    grafo = Graph()

    for prefixo, namespace in PREFIXOS.items():
        grafo.bind(prefixo, namespace)

    return grafo

def descrever_grafo_convertido(cabecalho : Graph, uris: dict, recurso: dict, 
                               pacote: dict, nome_base: str, data_criacao: date) -> None:

    sujeito = URIRef(uris['grafo'])

    cabecalho.add((sujeito, RDF.type, DCAT.Dataset))
    cabecalho.add((sujeito, OWL.versionIRI, URIRef(uris['versao_grafo'])))
    cabecalho.add((sujeito, OWL.versionInfo, Literal(VERSAO_GRAFO)))

    titulo = f'{recurso["name"]} em RDF'
    comentario = (f'Conversão para RDF do recurso {recurso["name"]} 'f'do Portal da Transparência do ES.')
    cabecalho.add((sujeito, DCTERMS.title, Literal(titulo, lang=IDIOMA)))
    cabecalho.add((sujeito, RDFS.comment, Literal(comentario, lang=IDIOMA)))

    cabecalho.add((sujeito, DCTERMS.creator, Literal(AUTOR)))
    cabecalho.add((sujeito, DCTERMS.created, Literal(data_criacao.isoformat(), datatype=XSD.date)))
    cabecalho.add((sujeito, DCTERMS.language, Literal(IDIOMA)))
    cabecalho.add((sujeito, DCTERMS.license, URIRef(pacote['license_url'])))

    namespace_vocabulario = f'{URL_BASE_DADOS}/vocab/{nome_base}#'
    cabecalho.add((sujeito, VANN.preferredNamespacePrefix, Literal(nome_base)))
    cabecalho.add((sujeito, VANN.preferredNamespaceUri, Literal(namespace_vocabulario, datatype=XSD.anyURI)))

    cabecalho.add((sujeito, PROV.wasDerivedFrom, URIRef(uris['distribuicao'])))


def descrever_distribuicao(cabecalho: Graph, uris: dict, recurso: dict) -> None:
   
    sujeito = URIRef(uris['distribuicao'])

    if not recurso.get('last_modified'):
        raise ValueError(f'O recurso {recurso["id"]} veio sem last_modified.')

    cabecalho.add((sujeito, RDF.type, DCAT.Distribution))
    cabecalho.add((sujeito, DCTERMS.identifier, Literal(recurso['id'])))
    cabecalho.add((sujeito, DCTERMS.title, Literal(recurso['name'])))
    cabecalho.add((sujeito, DCTERMS.format, Literal(recurso['format'])))
    cabecalho.add((sujeito, DCTERMS.modified, Literal(recurso['last_modified'], datatype=XSD.dateTime)))
    cabecalho.add((sujeito, DCTERMS.isPartOf, URIRef(uris['pacote'])))
    cabecalho.add((sujeito, DCAT.downloadURL, URIRef(recurso['url'])))


def descrever_pacote(cabecalho: Graph, uris: dict, pacote: dict) -> None:
    
    sujeito = URIRef(uris['pacote'])
    nome_orgao = pacote['organization']['title']

    cabecalho.add((sujeito, RDF.type, DCAT.Dataset))
    cabecalho.add((sujeito, DCTERMS.identifier, Literal(pacote['id'])))
    cabecalho.add((sujeito, DCTERMS.title, Literal(pacote['title'])))
    cabecalho.add((sujeito, DCTERMS.publisher, Literal(nome_orgao)))
    cabecalho.add((sujeito, DCAT.distribution, URIRef(uris['distribuicao'])))

def montar_cabecalho(recurso: dict, pacote: dict, uris: dict, nome_base: str, data_criacao: date) -> Graph:

    cabecalho = criar_grafo_vazio()
    
    descrever_grafo_convertido(cabecalho, uris, recurso, pacote, nome_base, data_criacao)
    descrever_distribuicao(cabecalho, uris, recurso)
    descrever_pacote(cabecalho, uris, pacote)
    
    return cabecalho