"""Regravação de um N-Triples em Turtle, que é mais fácil de ler.

Serve para as amostras: a rdflib carrega o grafo inteiro na memória, o que não
é viável para os arquivos completos.
"""

from pathlib import Path

from rdflib import Graph

from transparencia_es_rdf.rdf.vocabularios import NAMESPACE_DESPESAS, NAMESPACE_NUCLEO, NAMESPACE_RECEITAS

# Os prefixos que encurtam os endereços da ontologia no Turtle.
PREFIXOS = {
    'rec': NAMESPACE_RECEITAS,
    'desp': NAMESPACE_DESPESAS,
    'nucleo': NAMESPACE_NUCLEO,
}


def gravar_em_turtle(entrada: Path, saida: Path) -> int:
    """Lê um arquivo N-Triples e grava o mesmo grafo em Turtle. Devolve o número de triplas."""
    grafo = Graph()
    for prefixo, namespace in PREFIXOS.items():
        grafo.bind(prefixo, namespace)
    grafo.parse(entrada, format='nt')
    saida.parent.mkdir(parents=True, exist_ok=True)
    grafo.serialize(destination=saida, format='turtle')
    return len(grafo)
