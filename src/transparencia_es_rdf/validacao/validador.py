"""Validação dos dados convertidos com as formas SHACL, usando a pySHACL.

A pySHACL carrega o grafo inteiro na memória, como o rdflib, e o arquivo de
Despesas de 2025 dá 45,5 milhões de triplas. Por isso a validação lê o CSV
em lotes de linhas: converte cada lote num grafo na memória, valida o lote e
soma o resultado. Cada lote é convertido com um estado novo, então sai
completo: a UG, a natureza e as outras entidades que muitas linhas repetem
aparecem em todo lote que as usa, com o tipo e os atributos.

Uma entidade que aparece em vários lotes é conferida em cada um deles, e a
mesma violação dela é contada uma vez só. O que a validação em lotes não vê é
um conflito entre lotes: se uma UG tem uma descrição nas linhas de um lote e
outra descrição nas de outro, cada lote só vê uma, e o "valores a mais" não
aparece. Quando o arquivo cabe num lote só (as amostras e os arquivos
menores de Despesas), a validação é completa.
"""

import io
from collections import Counter
from itertools import islice

import pyshacl
from rdflib import Graph
from rdflib.namespace import RDF, SH

# Os tipos de violação que as formas geradas por validacao/formas.py produzem.
NOME_DO_TIPO_DE_VIOLACAO = {
    'MinCountConstraintComponent': 'falta valor',
    'MaxCountConstraintComponent': 'valores a mais',
    'ClassConstraintComponent': 'valor de outra classe',
    'DatatypeConstraintComponent': 'tipo de dado errado',
}


def _lotes(linhas, linhas_por_lote: int):
    """Divide as linhas do CSV em listas de linhas_por_lote linhas (a última pode ser menor)."""
    iterador = iter(linhas)
    while True:
        lote = list(islice(iterador, linhas_por_lote))
        if not lote:
            return
        yield lote


def _converter_lote(conversor, lote: list) -> Graph:
    """Converte as linhas do lote com o conversor da base e lê o resultado num grafo."""
    destino = io.StringIO()
    conversor.converter_linhas(lote, destino)
    grafo = Graph()
    grafo.parse(data=destino.getvalue(), format='nt')
    return grafo


def _nome_curto(termo) -> str:
    return str(termo).split('#')[-1]


def _violacoes(resultado: Graph, formas: Graph):
    """Cada violação do relatório da pySHACL como (recurso, forma, regra, tipo).

    A regra é a sh:property que falhou; a forma é a que contém a regra. Nas
    formas de domínio, que não têm regra (é o próprio recurso que tem de ser
    da classe), regra e forma são a mesma.
    """
    for violacao in resultado.subjects(RDF.type, SH.ValidationResult):
        recurso = resultado.value(violacao, SH.focusNode)
        regra = resultado.value(violacao, SH.sourceShape)
        tipo = _nome_curto(resultado.value(violacao, SH.sourceConstraintComponent))
        forma = formas.value(predicate=SH.property, object=regra) or regra
        yield recurso, forma, regra, tipo


def validar_linhas(linhas, conversor, formas: Graph, ontologia: Graph, linhas_por_lote: int) -> dict:
    """Converte e valida as linhas lote a lote e devolve o resumo das violações.

    O resumo agrupa as violações por forma, regra e tipo, com a quantidade de
    recursos e um exemplo de recurso, porque o relatório completo da pySHACL
    tem uma entrada por violação (no arquivo de Despesas, mais de um milhão).
    A ontologia vai junto (ont_graph) para a pySHACL saber, por exemplo, que um
    RegistroDeRestosAPagar também é um RegistroDeDespesaOrcamentaria.
    """
    quantidade = Counter()
    exemplo = {}
    ja_contadas = set()                  # hash de (recurso, regra, tipo) já contados
    linhas_lidas = triplas_validadas = lotes = 0

    for lote in _lotes(linhas, linhas_por_lote):
        lotes += 1
        linhas_lidas += len(lote)
        grafo = _converter_lote(conversor, lote)
        triplas_validadas += len(grafo)
        _, resultado, _ = pyshacl.validate(grafo, shacl_graph=formas, ont_graph=ontologia,
                                           inference='none', allow_warnings=True)
        for recurso, forma, regra, tipo in _violacoes(resultado, formas):
            identidade = hash((str(recurso), str(regra), tipo))
            if identidade in ja_contadas:
                continue
            ja_contadas.add(identidade)
            nome_da_regra = formas.value(regra, SH.name)
            chave = (_nome_curto(forma), '' if nome_da_regra is None else str(nome_da_regra),
                     NOME_DO_TIPO_DE_VIOLACAO.get(tipo, tipo))
            quantidade[chave] += 1
            exemplo.setdefault(chave, str(recurso))

    violacoes = [
        {'forma': forma, 'regra': regra, 'tipo': tipo, 'quantidade': quantidade[(forma, regra, tipo)],
         'exemplo': exemplo[(forma, regra, tipo)]}
        for forma, regra, tipo in sorted(quantidade)
    ]
    return {'linhas_lidas': linhas_lidas, 'lotes': lotes, 'triplas_validadas': triplas_validadas,
            'violacoes': violacoes}
