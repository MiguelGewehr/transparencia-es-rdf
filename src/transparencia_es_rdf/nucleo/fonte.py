"""Fonte de recursos: de onde vem o dinheiro que entra (Receitas) e que sai (Despesas).

Fica no núcleo pelo mesmo motivo da UG: a integração das duas bases depende
de a mesma fonte ter a mesma URI nas duas.
"""

from transparencia_es_rdf.rdf.vocabularios import uri_de_dado


def uri_da_fonte(codigo_detalhamento_fonte: str) -> str:
    """URI da fonte a partir do código detalhado: '500.100200' vira .../id/fonte/500.100200.
    """
    return uri_de_dado('fonte', codigo_detalhamento_fonte)
