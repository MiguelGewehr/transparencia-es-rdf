from transparencia_es_rdf.rdf.vocabularios import NAMESPACE_NUCLEO, propriedade, uri_de_dado

PROPRIEDADE_CODIGO = propriedade(NAMESPACE_NUCLEO, 'OrgaoPublico', 'codigo')
PROPRIEDADE_DESCRICAO = propriedade(NAMESPACE_NUCLEO, 'OrgaoPublico', 'descricao')

def uri_da_unidade_gestora(codigo: str) -> str:
    return uri_de_dado('unidade-gestora', codigo)

