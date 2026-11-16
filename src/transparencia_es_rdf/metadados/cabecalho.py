from datetime import date

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS, OWL, PROV, RDF, RDFS, XSD

from transparencia_es_rdf.config import AUTOR, IDIOMA, VERSAO_GRAFO
from transparencia_es_rdf.rdf.vocabularios import NAMESPACE_DESPESAS, NAMESPACE_NUCLEO, NAMESPACE_RECEITAS

PREFIXOS = {
    'dcat': DCAT,
    'dcterms': DCTERMS,
    'owl': OWL,
    'prov': PROV,
    'rdf': RDF,
    'rdfs': RDFS,
    'xsd': XSD,
}

# Os módulos da ontologia que os dados de cada base usam: o da base e o núcleo.
# A URI de um módulo é o namespace sem o "#" do final, como no owl:Ontology
# que abre cada .ttl de ontologia/out/ttl/.
MODULOS_DA_BASE = {
    'receitas': [NAMESPACE_RECEITAS, NAMESPACE_NUCLEO],
    'despesas': [NAMESPACE_DESPESAS, NAMESPACE_NUCLEO],
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

    # Os dados seguem a ontologia: dcterms:conformsTo é o jeito do DCAT de
    # apontar o modelo que um conjunto de dados segue.
    for namespace in MODULOS_DA_BASE[nome_base]:
        cabecalho.add((sujeito, DCTERMS.conformsTo, URIRef(namespace.rstrip('#'))))

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