"""Gera as formas SHACL a partir da ontologia.

A ontologia (ontologia/out/ttl/) já diz como os dados devem ser: o Tonto
transforma cada multiplicidade do modelo, como o [1] de "data: const
datetime [1]", numa restrição OWL. Só que a OWL adota o mundo aberto e não
acusa um dado que falta. Este arquivo traduz as mesmas regras para SHACL,
que adota o mundo fechado e acusa. Assim as formas não são escritas à mão, e
basta rodar de novo quando a ontologia mudar.

Três tipos de forma saem daqui:

1. Cardinalidade: uma forma por classe que tem restrições, com uma regra por
   restrição, traduzida assim:

       OWL                                       SHACL
       owl:cardinality n                         sh:minCount n e sh:maxCount n
       owl:minCardinality n                      sh:minCount n
       owl:maxCardinality n                      sh:maxCount n
       owl:qualifiedCardinality n + onClass C    sh:minCount n, sh:maxCount n e sh:class C
       owl:maxQualifiedCardinality n + onClass C sh:maxCount n e sh:class C
       owl:someValuesFrom C                      sh:minCount 1 e sh:class C
       propriedade [ owl:inverseOf p ]           caminho [ sh:inversePath p ]
       propriedade derivada (owl:propertyChainAxiom) caminho com a sequência da cadeia

   Nas qualificadas, a tradução exata seria sh:qualifiedValueShape, que
   conta só os valores da classe C. Como toda propriedade da ontologia já tem
   a classe C como imagem (rdfs:range), contar todos os valores dá o mesmo
   resultado, e o relatório fica mais fácil de ler.

   As propriedades derivadas, como emitidaPor em Receitas, não são escritas
   pelo conversor: a ontologia diz de onde elas vêm (owl:propertyChainAxiom).
   "A receita é emitidaPor a UG" é o mesmo que "o registro que tem a receita
   tem a UG emitente". Então a regra segue esse caminho nos dados, em vez de
   procurar uma tripla emitidaPor que ninguém escreveu.

2. Domínio: quem usa a propriedade p tem de ser da classe do rdfs:domain de p.

3. Imagem: o valor de p tem de ser da classe, ou do tipo de dado, do rdfs:range de p.

Os nomes das formas são os nomes curtos das classes e das propriedades, sob
o endereço http://localhost:8000/formas/<base>#, para o relatório apontar de
onde veio cada violação.
"""

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, SH, XSD

from transparencia_es_rdf.config import PASTA_ONTOLOGIA, URL_BASE_DADOS
from transparencia_es_rdf.rdf.vocabularios import NAMESPACE_DESPESAS, NAMESPACE_NUCLEO, NAMESPACE_RECEITAS

# Os arquivos da ontologia que descrevem cada base: o módulo da base e o núcleo.
ARQUIVOS_DA_ONTOLOGIA = {
    'receitas': ['base-receitas.ttl', 'nucleo.ttl'],
    'despesas': ['base-despesas.ttl', 'nucleo.ttl'],
}

# Só as propriedades destes namespaces viram regras. As da gUFO, que a
# ontologia importa, descrevem o modelo e não os dados.
NAMESPACES_DA_ONTOLOGIA = (NAMESPACE_RECEITAS, NAMESPACE_DESPESAS, NAMESPACE_NUCLEO)


def ler_ontologia(nome_base: str) -> Graph:
    """Lê os arquivos da ontologia da base num grafo só."""
    ontologia = Graph()
    for nome_do_arquivo in ARQUIVOS_DA_ONTOLOGIA[nome_base]:
        ontologia.parse(PASTA_ONTOLOGIA / nome_do_arquivo, format='turtle')
    return ontologia


def _nome_curto(uri: URIRef) -> str:
    """O que vem depois do "#": .../base-despesas#RegistroDeDespesa vira RegistroDeDespesa."""
    return str(uri).split('#')[-1]


def _da_ontologia(uri) -> bool:
    return isinstance(uri, URIRef) and str(uri).startswith(NAMESPACES_DA_ONTOLOGIA)


def _numero(valor: int) -> Literal:
    return Literal(valor, datatype=XSD.integer)


def _passo(ontologia: Graph, propriedade) -> tuple:
    """Um passo do caminho: ('direta', p) ou ('inversa', p) quando é [ owl:inverseOf p ]."""
    inversa = ontologia.value(propriedade, OWL.inverseOf)
    return ('inversa', inversa) if inversa is not None else ('direta', propriedade)


def _caminho(ontologia: Graph, propriedade) -> list[tuple]:
    """O caminho nos dados para a propriedade, como uma lista de passos.

    Uma propriedade escrita pelo conversor é um passo só. Uma derivada vira os
    passos da cadeia de onde vem (owl:propertyChainAxiom). Ao contrário (a
    inversa de uma derivada), a cadeia é percorrida de trás para a frente.
    """
    direcao, base = _passo(ontologia, propriedade)
    cadeia = ontologia.value(base, OWL.propertyChainAxiom)
    if cadeia is None:
        return [(direcao, base)]
    passos = [_passo(ontologia, item) for item in Collection(ontologia, cadeia)]
    if direcao == 'inversa':
        oposto = {'direta': 'inversa', 'inversa': 'direta'}
        passos = [(oposto[tipo], p) for tipo, p in reversed(passos)]
    return passos


def _regra_da_restricao(ontologia: Graph, restricao) -> dict | None:
    """Traduz uma owl:Restriction na regra SHACL equivalente (tabela no começo do arquivo).

    Devolve o caminho e as contagens, ou None se a restrição usa uma forma
    que a tabela não cobre (nenhuma, na versão atual da ontologia).
    """
    propriedade = ontologia.value(restricao, OWL.onProperty)
    direcao, base = _passo(ontologia, propriedade)
    nome_da_propriedade = ('inversa de ' if direcao == 'inversa' else '') + _nome_curto(base)
    caminho = _caminho(ontologia, propriedade)

    def inteiro(predicado):
        valor = ontologia.value(restricao, predicado)
        return None if valor is None else int(valor)

    classe = ontologia.value(restricao, OWL.onClass) or ontologia.value(restricao, OWL.someValuesFrom)
    exata = inteiro(OWL.cardinality) if inteiro(OWL.cardinality) is not None else inteiro(OWL.qualifiedCardinality)
    minimo = inteiro(OWL.minCardinality)
    maximo = inteiro(OWL.maxCardinality)
    if maximo is None:
        maximo = inteiro(OWL.maxQualifiedCardinality)
    if exata is not None:
        minimo = maximo = exata
    if ontologia.value(restricao, OWL.someValuesFrom) is not None:
        minimo = 1
    if minimo is None and maximo is None:
        return None
    return {'caminho': caminho, 'nome': nome_da_propriedade, 'minimo': minimo, 'maximo': maximo, 'classe': classe}


def _adicionar_regra(formas: Graph, forma, regra: dict) -> None:
    """Escreve uma regra (sh:property) dentro de uma forma."""
    regra_rdf = BNode()
    formas.add((forma, SH.property, regra_rdf))
    passos = []
    for tipo, propriedade in regra['caminho']:
        if tipo == 'inversa':
            passo = BNode()
            formas.add((passo, SH.inversePath, propriedade))
            passos.append(passo)
        else:
            passos.append(propriedade)
    if len(passos) == 1:
        formas.add((regra_rdf, SH.path, passos[0]))
    else:
        sequencia = BNode()
        Collection(formas, sequencia, passos)
        formas.add((regra_rdf, SH.path, sequencia))
    formas.add((regra_rdf, SH.name, Literal(regra['nome'])))
    if regra.get('minimo') is not None:
        formas.add((regra_rdf, SH.minCount, _numero(regra['minimo'])))
    if regra.get('maximo') is not None:
        formas.add((regra_rdf, SH.maxCount, _numero(regra['maximo'])))
    if regra.get('classe') is not None:
        formas.add((regra_rdf, SH['class'], regra['classe']))
    if regra.get('tipo_de_dado') is not None:
        formas.add((regra_rdf, SH.datatype, regra['tipo_de_dado']))


def gerar_formas(ontologia: Graph, nome_base: str) -> Graph:
    """As formas SHACL que a ontologia da base pede (os três tipos do começo do arquivo)."""
    forma_de = Namespace(f'{URL_BASE_DADOS}/formas/{nome_base}#')
    formas = Graph()
    formas.bind('sh', SH)
    formas.bind('forma', forma_de)

    # 1. Cardinalidade: as restrições de cada classe.
    for classe, restricao in sorted(ontologia.subject_objects(RDFS.subClassOf)):
        if not _da_ontologia(classe) or (restricao, RDF.type, OWL.Restriction) not in ontologia:
            continue
        regra = _regra_da_restricao(ontologia, restricao)
        if regra is None:
            continue
        forma = forma_de[_nome_curto(classe)]
        formas.add((forma, RDF.type, SH.NodeShape))
        formas.add((forma, SH.targetClass, classe))
        _adicionar_regra(formas, forma, regra)

    # 2 e 3. Domínio e imagem de cada propriedade.
    propriedades = set(ontologia.subjects(RDF.type, OWL.ObjectProperty)) | \
        set(ontologia.subjects(RDF.type, OWL.DatatypeProperty))
    for propriedade in sorted(p for p in propriedades if _da_ontologia(p)):
        forma = forma_de['uso-de-' + _nome_curto(propriedade)]
        dominio = ontologia.value(propriedade, RDFS.domain)
        imagem = ontologia.value(propriedade, RDFS.range)
        if dominio is None and imagem is None:
            continue
        formas.add((forma, RDF.type, SH.NodeShape))
        formas.add((forma, SH.targetSubjectsOf, propriedade))
        if dominio is not None:
            formas.add((forma, SH['class'], dominio))
        if imagem is not None:
            regra = {'caminho': [('direta', propriedade)], 'nome': _nome_curto(propriedade)}
            if str(imagem).startswith(str(XSD)):
                regra['tipo_de_dado'] = imagem
            else:
                regra['classe'] = imagem
            _adicionar_regra(formas, forma, regra)
    return formas
