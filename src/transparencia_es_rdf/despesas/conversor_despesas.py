"""Conversão das linhas do arquivo Despesas em triplas.

Funciona como o conversor de Receitas: recebe as linhas já lidas
(portal/leitura.py) e um destino já aberto para escrita (rdf/ntriples.py), e
usa as mesmas funções de rdf/escrita.py para não repetir triplas. As partes
que os quatro arquivos de Despesas têm em comum (a despesa, o registro, o
valor e a classificação) são escritas pelas funções de despesas/comum.py.

O que a ontologia (commit e99443d) diz que uma linha descreve (cada seta é
uma propriedade; as marcadas com * só existem se a linha tiver a entidade):

    Registro --temDespesaOrcamentaria---------> Despesa
    Registro --temUnidadeGestoraDaDespesa-----> UG
    Registro --valorAtrelado------------------> Valor (os 4 números da linha)
    Registro --dadosDoFavorecido--------------> Favorecido
    Registro --dadosLicitacao-----------------> Licitação
    Registro --mediatesProcesso...------------> Processo
    Registro --dadosRetencao------------------> Retenção *
    Registro --hasBancoNaDespesa--------------> Banco *
    Registro --hasConcedorDeConvenio----------> Convênio concedido *
    Registro --hasRecebedorDeConvenio---------> Convênio recebido *

    Classificação --classifica----------------> Registro
    Classificação --funcionalClassificadaPor--> Classificador funcional
    Classificação --programaticaClassificadaPor> Classificador programático
    Classificação --naturezaClassificadaPor---> Natureza
    Classificação --fonteClassificadaPor------> Fonte
    Classificação --mediatesEsfera...---------> Esfera

    Classificador institucional --mediatesClassificacao...--> Classificação
    Classificador institucional --mediatesOrgao...----------> Órgão

Cada linha do CSV é um registro e tem a sua despesa, a sua classificação e o
seu classificador institucional, todos com o Id da linha na URI. O resto
(UG, favorecido, fonte, natureza...) muitas linhas repetem, e cada um é
escrito uma vez só.
"""

from transparencia_es_rdf.despesas import comum, mapeamento, uris
from transparencia_es_rdf.nucleo.fonte import uri_da_fonte
from transparencia_es_rdf.nucleo.unidade_gestora import uri_da_unidade_gestora
from transparencia_es_rdf.rdf.escrita import montar_relatorio

NOME_DO_ARQUIVO = 'despesas'


def _converter_linha(estado: dict, linha: dict) -> None:
    """Escreve tudo o que uma linha do CSV descreve."""
    estado['linhas_lidas'] += 1
    linha = comum.preparar_linha(linha, mapeamento.COLUNAS_DOS_VALORES)
    linha['Data'] = comum.data_no_formato_iso(linha['Data'])

    # 1. As entidades que muitas linhas repetem: nome -> (URI, classe, atributos).
    compartilhadas = {
        'ug': (uri_da_unidade_gestora(linha['CodigoUnidadeGestora']), mapeamento.CLASSE_UG,
               mapeamento.ATRIBUTOS_DA_UG),
        'orgao': (uris.uri_do_orgao(linha), mapeamento.CLASSE_ORGAO, mapeamento.ATRIBUTOS_DO_ORGAO),
        'favorecido': (uris.uri_do_favorecido(linha), mapeamento.CLASSE_FAVORECIDO,
                       mapeamento.ATRIBUTOS_DO_FAVORECIDO),
        'licitacao': (uris.uri_da_licitacao(linha), mapeamento.CLASSE_LICITACAO,
                      mapeamento.ATRIBUTOS_DA_LICITACAO),
        'processo': (uris.uri_do_processo(linha), mapeamento.CLASSE_PROCESSO, mapeamento.ATRIBUTOS_DO_PROCESSO),
        'funcional': (uris.uri_da_funcional(linha), mapeamento.CLASSE_FUNCIONAL,
                      mapeamento.ATRIBUTOS_DA_FUNCIONAL),
        'programatica': (uris.uri_da_programatica(linha), mapeamento.CLASSE_PROGRAMATICA,
                         mapeamento.ATRIBUTOS_DA_PROGRAMATICA),
        'natureza': (uris.uri_da_natureza(linha), mapeamento.CLASSE_NATUREZA, mapeamento.ATRIBUTOS_DA_NATUREZA),
        'fonte': (uri_da_fonte(linha['CodigoDetalhamentoFonte']), mapeamento.CLASSE_FONTE,
                  mapeamento.ATRIBUTOS_DA_FONTE),
        'esfera': (uris.uri_da_esfera(linha), mapeamento.CLASSE_ESFERA, mapeamento.ATRIBUTOS_DA_ESFERA),
        'retencao': (uris.uri_da_retencao(linha), mapeamento.CLASSE_RETENCAO, mapeamento.ATRIBUTOS_DA_RETENCAO),
        'banco': (uris.uri_do_banco(linha), mapeamento.CLASSE_BANCO, mapeamento.ATRIBUTOS_DO_BANCO),
        'convenio_concedido': (uris.uri_do_convenio(linha['CodigoConvenioConcedido']),
                               mapeamento.CLASSE_CONVENIO_CONCEDIDO, mapeamento.ATRIBUTOS_DO_CONVENIO_CONCEDIDO),
        'convenio_recebido': (uris.uri_do_convenio(linha['CodigoConvenioRecebido']),
                              mapeamento.CLASSE_CONVENIO_RECEBIDO, mapeamento.ATRIBUTOS_DO_CONVENIO_RECEBIDO),
    }
    uris_da_linha = comum.escrever_compartilhadas(estado, linha, compartilhadas)
    uri_valor = comum.escrever_valor(estado, linha, 'valor-despesa', mapeamento.CLASSE_VALOR,
                                     mapeamento.ATRIBUTOS_DO_VALOR)

    # 2. As entidades que existem uma vez por linha: a despesa e o registro,
    # com as ligações do registro (as que a linha não tem ficaram com None em
    # uris_da_linha e não são escritas)...
    ligacoes_do_registro = [
        (mapeamento.RELACAO_TEM_VALOR, uri_valor),
        (mapeamento.RELACAO_FAVORECIDO, uris_da_linha['favorecido']),
        (mapeamento.RELACAO_LICITACAO, uris_da_linha['licitacao']),
        (mapeamento.RELACAO_PROCESSO, uris_da_linha['processo']),
        (mapeamento.RELACAO_RETENCAO, uris_da_linha['retencao']),
        (mapeamento.RELACAO_BANCO, uris_da_linha['banco']),
        (mapeamento.RELACAO_CONVENIO_CONCEDIDO, uris_da_linha['convenio_concedido']),
        (mapeamento.RELACAO_CONVENIO_RECEBIDO, uris_da_linha['convenio_recebido']),
    ]
    uri_registro = comum.escrever_registro(estado, NOME_DO_ARQUIVO, linha, mapeamento.CLASSE_REGISTRO,
                                           mapeamento.ATRIBUTOS_DO_REGISTRO, uris_da_linha['ug'],
                                           ligacoes_do_registro)

    # ... a classificação, com os cinco classificadores...
    uri_classificacao = comum.escrever_classificacao(estado, NOME_DO_ARQUIVO, linha, uri_registro, [
        (mapeamento.RELACAO_FUNCIONAL, uris_da_linha['funcional']),
        (mapeamento.RELACAO_PROGRAMATICA, uris_da_linha['programatica']),
        (mapeamento.RELACAO_NATUREZA, uris_da_linha['natureza']),
        (mapeamento.RELACAO_FONTE, uris_da_linha['fonte']),
        (mapeamento.RELACAO_ESFERA, uris_da_linha['esfera']),
    ])

    # ... e o classificador institucional, que liga a classificação ao órgão.
    # A ontologia também o liga a uma unidade orçamentária, mas este arquivo
    # não tem essa coluna.
    comum.escrever_classificador_institucional(estado, NOME_DO_ARQUIVO, linha, uri_classificacao, [
        (mapeamento.RELACAO_INSTITUCIONAL_ORGAO, uris_da_linha['orgao']),
    ])


def converter_linhas(linhas, destino) -> dict:
    """Converte todas as linhas e devolve o relatório com as contagens."""
    estado = comum.criar_estado(destino)
    for linha in linhas:
        _converter_linha(estado, linha)
    return montar_relatorio(estado)
