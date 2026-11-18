"""URIs das entidades dos quatro arquivos de Despesas.

Cada linha do CSV tem um Id único dentro do seu arquivo (no arquivo Despesas
de 2025, os 1.456.562 Ids são todos diferentes). As entidades que existem uma
vez por linha usam esse Id, com o nome do arquivo no caminho, porque o Id não
é único entre arquivos: em RestosAPagar os Ids começam em 1. O valor também é
um por linha e usa o Id. As que muitas linhas repetem usam os seus códigos,
um em cada pedaço do caminho. As URIs da UG e da fonte não
estão aqui: vêm do núcleo, para serem as mesmas de Receitas.

Uma entidade com a mesma URI em dois arquivos é a mesma entidade no grafo:
é assim que a UG, a esfera e os classificadores funcional e por natureza de
OrcamentosDespesa se ligam aos de Despesas.

As funções que dependem de colunas que podem vir vazias ou com um texto que
quer dizer "nada" (retenção, banco, convênios, município e favorecido do
orçamento) devolvem None quando a linha não tem a entidade.
"""

from transparencia_es_rdf.rdf.vocabularios import uri_de_dado

# Na coluna CodigoConvenioConcedido, "0" quer dizer que a linha não tem
# convênio: é o caso de 1.442.419 das 1.456.562 linhas de 2025. A coluna
# CodigoConvenioRecebido vem sempre vazia. O dicionário de dados do portal não
# diz o que é o "0"; é a nossa leitura do arquivo.
CODIGOS_SEM_CONVENIO = {'', '0'}

# Em OrcamentosDespesa, o texto "null" está no lugar do nome quando a linha não
# tem município (58.243 das 72.523 linhas de 2025, todas com o código 999999)
# ou não tem favorecido (11.366 linhas, todas com o código 0). Também é a
# nossa leitura do arquivo.
TEXTO_SEM_VALOR = 'null'


def uri_por_linha(nome_do_arquivo: str, linha: dict, entidade: str) -> str:
    """URI do registro, da despesa, da classificação, do classificador institucional ou do valor.

    O nome do arquivo é o de despesas/arquivo.py ('despesas', 'restos-a-pagar'...).
    Exemplo: uri_por_linha('despesas', linha, 'registro') devolve
    'http://localhost:8000/id/despesas/despesas/2025/registro/279277262'.
    """
    return uri_de_dado('despesas', nome_do_arquivo, linha['Ano'], entidade, linha['Id'])


def uri_do_favorecido(linha: dict) -> str:
    # O IdFavorecido, e não o CPF: o CPF mascarado se repete entre pessoas
    # diferentes (971 CPFs mascarados de 2025 têm mais de um IdFavorecido).
    return uri_de_dado('favorecido', linha['IdFavorecido'])


def uri_da_licitacao(linha: dict) -> str:
    return uri_de_dado('licitacao', linha['TipoLicitacao'], linha['NumeroLicitacao'], linha['AnoLicitacao'])


def uri_do_processo(linha: dict) -> str:
    return uri_de_dado('processo', linha['CodigoProcesso'])


def uri_do_orgao(linha: dict) -> str:
    return uri_de_dado('orgao', linha['CodigoOrgao'])


def uri_da_funcional(linha: dict) -> str:
    return uri_de_dado('classificador-funcional', linha['CodigoFuncao'], linha['CodigoSubFuncao'])


def uri_da_programatica(linha: dict) -> str:
    # O plano orçamentário fica de fora porque vem vazio em todas as linhas de 2025.
    return uri_de_dado('classificador-programatico', linha['CodigoPrograma'], linha['CodigoAcao'],
                       linha['CodigoSubtitulo'])


def uri_da_programatica_com_plano(linha: dict) -> str:
    # OrcamentosDespesa não tem subtítulo e tem plano orçamentário. O pedaço
    # 'plano-orcamentario' no caminho separa estas URIs das de Despesas, que
    # terminam no subtítulo: .../classificador-programatico/61/2070/plano-orcamentario/1.
    return uri_de_dado('classificador-programatico', linha['CodigoPrograma'], linha['CodigoAcao'],
                       'plano-orcamentario', linha['CodigoPlanoOrcamentario'])


def uri_da_natureza(linha: dict) -> str:
    # Os cinco códigos, porque o mesmo código de subelemento aparece em mais
    # de um elemento.
    return uri_de_dado('natureza-despesa', linha['CodigoCategoriaEconomica'], linha['CodigoGrupoDespesa'],
                       linha['CodigoModalidade'], linha['CodigoElementoDespesa'],
                       linha['CodigoSubelementoDespesa'])


def uri_da_natureza_por_elemento(linha: dict) -> str:
    # RestosAPagar só traz o elemento, num código de 6 dígitos ('339039'), e
    # não traz o subelemento. Com um pedaço só no caminho, a URI não se
    # confunde com as de cinco pedaços de Despesas.
    return uri_de_dado('natureza-despesa', linha['CodigoElemento'])


def uri_da_esfera(linha: dict) -> str:
    return uri_de_dado('esfera-orcamentaria', linha['Esfera'])


def uri_da_retencao(linha: dict) -> str | None:
    # As quatro colunas de retenção vêm todas preenchidas ou todas vazias.
    if linha['CredorRetencao'] == '':
        return None
    return uri_de_dado('retencao', linha['CredorRetencao'], linha['TipoRetencao'])


def uri_do_banco(linha: dict) -> str | None:
    # Na ontologia, a agência e o domicílio bancário são atributos do banco,
    # então cada combinação dos três códigos é um banco diferente.
    if linha['BancoOrigem'] == '':
        return None
    return uri_de_dado('banco', linha['BancoOrigem'], linha['AgenciaOrigem'], linha['DomicilioBancarioOrigem'])


def uri_do_convenio(codigo: str) -> str | None:
    if codigo in CODIGOS_SEM_CONVENIO:
        return None
    return uri_de_dado('convenio', codigo)


def uri_do_poder(linha: dict) -> str:
    return uri_de_dado('poder', linha['CodigoPoder'])


def uri_da_unidade_orcamentaria(linha: dict) -> str:
    return uri_de_dado('unidade-orcamentaria', linha['UnidadeOrcamentaria'])


def uri_da_microrregiao(linha: dict) -> str:
    return uri_de_dado('microrregiao', linha['Microregiao'])


def uri_do_municipio(linha: dict) -> str | None:
    if linha['NomeMunicipio'] == TEXTO_SEM_VALOR:
        return None
    return uri_de_dado('municipio', linha['Municipio'])


def uri_do_favorecido_do_orcamento(linha: dict) -> str | None:
    # OrcamentosDespesa não tem IdFavorecido, e o código 0, além das linhas sem
    # favorecido, aparece com 35 nomes de empresas diferentes (muitas de fora do
    # Brasil). Por isso a URI leva o código e o nome.
    if linha['Favorecido'] == TEXTO_SEM_VALOR:
        return None
    return uri_de_dado('favorecido-do-orcamento', linha['CpfCnpjNis'], linha['Favorecido'])
