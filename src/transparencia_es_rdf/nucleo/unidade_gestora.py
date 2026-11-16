"""Unidade gestora (UG): o órgão que emite ou recebe uma receita, ou que emite uma despesa.

Fica no núcleo porque as duas bases têm UGs, e a integração delas depende de
a mesma UG ter a mesma URI nas duas.
"""

from transparencia_es_rdf.rdf.vocabularios import NAMESPACE_NUCLEO, propriedade, uri_de_dado

# O código e a descrição da UG são atributos de OrgaoPublico, a classe do
# núcleo de que os papéis de UG das duas bases são subclasses.
PROPRIEDADE_CODIGO = propriedade(NAMESPACE_NUCLEO, 'OrgaoPublico', 'codigo')
PROPRIEDADE_DESCRICAO = propriedade(NAMESPACE_NUCLEO, 'OrgaoPublico', 'descricao')

# Em Receitas, todo código de UG tem 6 dígitos. Em Despesas, as UGs dos órgãos
# 1 a 9 vêm sem o zero da frente: 10101 em vez de 010101.
DIGITOS_DO_CODIGO = 6


def completar_codigo(codigo: str) -> str:
    """Põe os zeros que faltam na frente do código: '10101' vira '010101'."""
    return codigo.zfill(DIGITOS_DO_CODIGO)


def uri_da_unidade_gestora(codigo: str) -> str:
    """URI da UG a partir do código: '800102' vira .../id/unidade-gestora/800102."""
    return uri_de_dado('unidade-gestora', codigo)
