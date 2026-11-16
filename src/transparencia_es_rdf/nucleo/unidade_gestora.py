"""Unidade gestora (UG): o órgão que emite ou recebe uma receita, ou que emite uma despesa.

Fica no núcleo porque as duas bases têm UGs, e a integração delas depende de
a mesma UG ter a mesma URI nas duas. Na ontologia, codigo e descricao são
atributos de OrgaoPublico, do pacote nucleo, e os papéis de UG de cada base
herdam esses dois atributos.
"""

from transparencia_es_rdf.rdf.vocabularios import NAMESPACE_NUCLEO, propriedade, uri_de_dado

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