"""URIs das entidades de Despesas.

Cada linha do CSV tem um Id único (no arquivo de 2025, os 1.456.562 Ids são
todos diferentes). As quatro entidades que existem uma vez por linha usam
esse Id. As que muitas linhas repetem usam os seus códigos, um em cada pedaço
do caminho; o valor usa os seus quatro números, como em Receitas. As URIs da
UG e da fonte não estão aqui: vêm do núcleo, para serem as mesmas de Receitas.

As funções que dependem de colunas que podem vir vazias (retenção, banco e
convênios) devolvem None quando a linha não tem a entidade.
"""

from decimal import Decimal

from transparencia_es_rdf.rdf.ntriples import numero_canonico
from transparencia_es_rdf.rdf.vocabularios import uri_de_dado

# Na coluna CodigoConvenioConcedido, "0" quer dizer que a linha não tem
# convênio: é o caso de 1.442.419 das 1.456.562 linhas de 2025. A coluna
# CodigoConvenioRecebido vem sempre vazia. O dicionário de dados do portal não
# diz o que é o "0"; é a nossa leitura do arquivo.
CODIGOS_SEM_CONVENIO = {'', '0'}


def uri_por_linha(linha: dict, entidade: str) -> str:
    """URI do registro, da despesa, da classificação ou do classificador institucional.

    Exemplo: uri_por_linha(linha, 'registro') devolve
    'http://localhost:8000/id/despesas/2025/registro/279277262'.
    """
    return uri_de_dado('despesas', linha['Ano'], entidade, linha['Id'])


def uri_do_valor(numeros: list[Decimal]) -> str:
    """Os quatro números na forma canônica, separados por "_": .../id/valor-despesa/0_0_190.59_0."""
    chave = '_'.join(numero_canonico(numero) for numero in numeros)
    return uri_de_dado('valor-despesa', chave)


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


def uri_da_natureza(linha: dict) -> str:
    # Os cinco códigos, porque o mesmo código de subelemento aparece em mais
    # de um elemento.
    return uri_de_dado('natureza-despesa', linha['CodigoCategoriaEconomica'], linha['CodigoGrupoDespesa'],
                       linha['CodigoModalidade'], linha['CodigoElementoDespesa'],
                       linha['CodigoSubelementoDespesa'])


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