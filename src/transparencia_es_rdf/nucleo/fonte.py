"""Fonte de recursos: de onde vem o dinheiro que entra (Receitas) e que sai (Despesas).

Fica no núcleo pelo mesmo motivo da UG: a integração das duas bases depende
de a mesma fonte ter a mesma URI nas duas. Na ontologia do commit 90c3354,
FonteDaReceita e FonteDaDespesa são papéis de FonteOrcamentaria, do núcleo.
Os atributos continuam em cada base, porque cada papel tem os seus.
"""

from transparencia_es_rdf.rdf.vocabularios import uri_de_dado


def uri_da_fonte(codigo_detalhamento_fonte: str) -> str:
    """URI da fonte a partir do código detalhado: '500.100200' vira .../id/fonte/500.100200.

    Em Receitas, o código vem da coluna codigoDetalhamentoFonteAux; em
    Despesas, da coluna CodigoDetalhamentoFonte. Os dois têm o mesmo formato.
    """
    return uri_de_dado('fonte', codigo_detalhamento_fonte)