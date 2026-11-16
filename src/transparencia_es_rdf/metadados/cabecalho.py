"""O cabeçalho de metadados: de onde vieram os dados convertidos.

Descreve três coisas, cada uma com os seus metadados:

    grafo convertido (dcat:Dataset) --prov:wasDerivedFrom--> distribuição
    distribuição (dcat:Distribution, o CSV) --dcterms:isPartOf--> pacote
    pacote (dcat:Dataset, a base no portal) --dcat:distribution--> distribuição

As informações vêm das respostas da API (resource_show e package_show). O
cabeçalho é pequeno (24 triplas), então é montado na rdflib e gravado em Turtle.
"""

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


def _criar_grafo_vazio() -> Graph:
    """Um grafo da rdflib com os prefixos do cabeçalho."""
    grafo = Graph()
    for prefixo, namespace in PREFIXOS.items():
        grafo.bind(prefixo, namespace)
    return grafo


def _descrever_grafo_convertido(cabecalho: Graph, uris: dict, recurso: dict,
                                pacote: dict, nome_base: str, data_criacao: date) -> None:
    """O grafo gerado pela ferramenta: título, versão, autor, data, licença e de onde veio."""
    sujeito = URIRef(uris['grafo'])

    cabecalho.add((sujeito, RDF.type, DCAT.Dataset))
    cabecalho.add((sujeito, OWL.versionIRI, URIRef(uris['versao_grafo'])))
    cabecalho.add((sujeito, OWL.versionInfo, Literal(VERSAO_GRAFO)))

    titulo = f'{recurso["name"]} em RDF'
    comentario = f'Conversão para RDF do recurso {recurso["name"]} do Portal da Transparência do ES.'
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


def _descrever_distribuicao(cabecalho: Graph, uris: dict, recurso: dict) -> None:
    """O arquivo CSV do portal: identificador, nome, formato, data de modificação e link."""
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


def _descrever_pacote(cabecalho: Graph, uris: dict, pacote: dict) -> None:
    """O pacote do portal: identificador, título e o órgão que publica."""
    sujeito = URIRef(uris['pacote'])
    nome_orgao = pacote['organization']['title']

    cabecalho.add((sujeito, RDF.type, DCAT.Dataset))
    cabecalho.add((sujeito, DCTERMS.identifier, Literal(pacote['id'])))
    cabecalho.add((sujeito, DCTERMS.title, Literal(pacote['title'])))
    cabecalho.add((sujeito, DCTERMS.publisher, Literal(nome_orgao)))
    cabecalho.add((sujeito, DCAT.distribution, URIRef(uris['distribuicao'])))


def montar_cabecalho(recurso: dict, pacote: dict, uris: dict, nome_base: str, data_criacao: date) -> Graph:
    """O cabeçalho completo, a partir das respostas da API e das URIs de metadados/uris.py."""
    cabecalho = _criar_grafo_vazio()
    _descrever_grafo_convertido(cabecalho, uris, recurso, pacote, nome_base, data_criacao)
    _descrever_distribuicao(cabecalho, uris, recurso)
    _descrever_pacote(cabecalho, uris, pacote)
    return cabecalho
