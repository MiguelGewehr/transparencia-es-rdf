"""Conversão das linhas do arquivo OrcamentosDespesa em triplas.

O que a ontologia (commit e99443d) diz que uma linha descreve (as setas
marcadas com * só existem se a linha tiver a entidade):

    Registro --temDespesaOrcamentaria---------> Despesa
    Registro --temUnidadeGestoraDaDespesa-----> UG
    Registro --valorAtrelado------------------> Valor (os 5 números da linha)
    Registro --dadosDoFavorecido--------------> Favorecido *
    Registro --mediatesMicroRegiao...---------> Microrregião
    Registro --mediatesMunicipio...-----------> Município *

    Classificação --classifica----------------> Registro
    Classificação --funcionalClassificadaPor--> Classificador funcional
    Classificação --programaticaClassificadaPor> Classificador programático (com o plano orçamentário)
    Classificação --naturezaClassificadaPor---> Natureza
    Classificação --fonteClassificadaPor------> Fonte (sem o detalhamento)
    Classificação --mediatesEsfera...---------> Esfera

    Classificador institucional --mediatesClassificacao...--------> Classificação
    Classificador institucional --mediatesUnidadeOrcamentaria...--> Unidade orçamentária

A UG, a esfera e os classificadores funcional e por natureza têm as mesmas
URIs que no arquivo Despesas, então são as mesmas entidades no grafo.
"""

from transparencia_es_rdf.despesas import comum, mapeamento, uris
from transparencia_es_rdf.nucleo.fonte import uri_da_fonte
from transparencia_es_rdf.nucleo.unidade_gestora import uri_da_unidade_gestora
from transparencia_es_rdf.rdf.escrita import montar_relatorio

NOME_DO_ARQUIVO = 'orcamentos-despesa'


def _converter_linha(estado: dict, linha: dict) -> None:
    """Escreve tudo o que uma linha do CSV descreve."""
    estado['linhas_lidas'] += 1
    linha = comum.preparar_linha(linha, mapeamento.ATRIBUTOS_DO_VALOR_ORCAMENTO_DESPESA)

    # 1. As entidades que muitas linhas repetem: nome -> (URI, classe, atributos).
    compartilhadas = {
        'ug': (uri_da_unidade_gestora(linha['CodigoUnidadeGestora']), mapeamento.CLASSE_UG,
               mapeamento.ATRIBUTOS_DA_UG),
        'favorecido': (uris.uri_do_favorecido_do_orcamento(linha), mapeamento.CLASSE_FAVORECIDO_DO_ORCAMENTO,
                       mapeamento.ATRIBUTOS_DO_FAVORECIDO_DO_ORCAMENTO),
        'microrregiao': (uris.uri_da_microrregiao(linha), mapeamento.CLASSE_MICRORREGIAO,
                         mapeamento.ATRIBUTOS_DA_MICRORREGIAO),
        'municipio': (uris.uri_do_municipio(linha), mapeamento.CLASSE_MUNICIPIO, mapeamento.ATRIBUTOS_DO_MUNICIPIO),
        'funcional': (uris.uri_da_funcional(linha), mapeamento.CLASSE_FUNCIONAL,
                      mapeamento.ATRIBUTOS_DA_FUNCIONAL),
        'programatica': (uris.uri_da_programatica_com_plano(linha), mapeamento.CLASSE_PROGRAMATICA,
                         mapeamento.ATRIBUTOS_DA_PROGRAMATICA_DO_ORCAMENTO),
        'natureza': (uris.uri_da_natureza(linha), mapeamento.CLASSE_NATUREZA, mapeamento.ATRIBUTOS_DA_NATUREZA),
        'fonte': (uri_da_fonte(linha['CodigoFonte']), mapeamento.CLASSE_FONTE,
                  mapeamento.ATRIBUTOS_DA_FONTE_DO_ORCAMENTO),
        'esfera': (uris.uri_da_esfera(linha), mapeamento.CLASSE_ESFERA, mapeamento.ATRIBUTOS_DA_ESFERA_DO_ORCAMENTO),
        'unidade_orcamentaria': (uris.uri_da_unidade_orcamentaria(linha), mapeamento.CLASSE_UNIDADE_ORCAMENTARIA,
                                 mapeamento.ATRIBUTOS_DA_UNIDADE_ORCAMENTARIA),
    }
    uris_da_linha = comum.escrever_compartilhadas(estado, linha, compartilhadas)
    uri_valor = comum.escrever_valor(estado, linha, 'valor-orcamento-despesa',
                                     mapeamento.CLASSE_VALOR_ORCAMENTO_DESPESA,
                                     mapeamento.ATRIBUTOS_DO_VALOR_ORCAMENTO_DESPESA)

    # 2. As entidades que existem uma vez por linha: a despesa e o registro...
    ligacoes_do_registro = [
        (mapeamento.RELACAO_ORCAMENTO_VALOR, uri_valor),
        (mapeamento.RELACAO_ORCAMENTO_FAVORECIDO, uris_da_linha['favorecido']),
        (mapeamento.RELACAO_ORCAMENTO_MICRORREGIAO, uris_da_linha['microrregiao']),
        (mapeamento.RELACAO_ORCAMENTO_MUNICIPIO, uris_da_linha['municipio']),
    ]
    uri_registro = comum.escrever_registro(estado, NOME_DO_ARQUIVO, linha,
                                           mapeamento.CLASSE_REGISTRO_ORCAMENTO_DESPESA,
                                           mapeamento.ATRIBUTOS_DO_REGISTRO_ORCAMENTO_DESPESA, uris_da_linha['ug'],
                                           ligacoes_do_registro)

    # ... a classificação, com os cinco classificadores...
    uri_classificacao = comum.escrever_classificacao(estado, NOME_DO_ARQUIVO, linha, uri_registro, [
        (mapeamento.RELACAO_FUNCIONAL, uris_da_linha['funcional']),
        (mapeamento.RELACAO_PROGRAMATICA, uris_da_linha['programatica']),
        (mapeamento.RELACAO_NATUREZA, uris_da_linha['natureza']),
        (mapeamento.RELACAO_FONTE, uris_da_linha['fonte']),
        (mapeamento.RELACAO_ESFERA, uris_da_linha['esfera']),
    ])

    # ... e o classificador institucional, que aqui liga a classificação à
    # unidade orçamentária (este arquivo não tem a coluna do órgão).
    comum.escrever_classificador_institucional(estado, NOME_DO_ARQUIVO, linha, uri_classificacao, [
        (mapeamento.RELACAO_INSTITUCIONAL_UNIDADE_ORCAMENTARIA, uris_da_linha['unidade_orcamentaria']),
    ])


def converter_linhas(linhas, destino) -> dict:
    """Converte todas as linhas e devolve o relatório com as contagens."""
    estado = comum.criar_estado(destino)
    for linha in linhas:
        _converter_linha(estado, linha)
    return montar_relatorio(estado)
