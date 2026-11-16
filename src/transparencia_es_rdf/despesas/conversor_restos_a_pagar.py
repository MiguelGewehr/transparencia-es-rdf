"""Conversão das linhas do arquivo RestosAPagar em triplas.

O que a ontologia (commit e0fff39) diz que uma linha descreve:

    Registro --temDespesaOrcamentaria---------> Despesa
    Registro --temUnidadeGestoraDaDespesa-----> UG
    Registro --valorAtrelado------------------> Valor (os 3 números da linha)
    Registro --mediatesPoderDaFederacao...----> Poder

    Classificação --classifica----------------> Registro
    Classificação --naturezaClassificadaPor---> Natureza (só o elemento)

O arquivo não tem as outras colunas de classificação, e o favorecido fica de
fora porque a ontologia não o liga a este tipo de registro (ver a parte de
RestosAPagar em despesas/mapeamento.py).
"""

from transparencia_es_rdf.despesas import comum, mapeamento, uris
from transparencia_es_rdf.nucleo.unidade_gestora import uri_da_unidade_gestora
from transparencia_es_rdf.rdf.escrita import montar_relatorio

NOME_DO_ARQUIVO = 'restos-a-pagar'


def _converter_linha(estado: dict, linha: dict) -> None:
    """Escreve tudo o que uma linha do CSV descreve."""
    estado['linhas_lidas'] += 1
    linha = comum.preparar_linha(linha, mapeamento.ATRIBUTOS_DO_VALOR_RESTOS_A_PAGAR)

    # 1. As entidades que muitas linhas repetem: nome -> (URI, classe, atributos).
    compartilhadas = {
        'ug': (uri_da_unidade_gestora(linha['CodigoUnidadeGestora']), mapeamento.CLASSE_UG,
               mapeamento.ATRIBUTOS_DA_UG),
        'poder': (uris.uri_do_poder(linha), mapeamento.CLASSE_PODER, mapeamento.ATRIBUTOS_DO_PODER),
        'natureza': (uris.uri_da_natureza_por_elemento(linha), mapeamento.CLASSE_NATUREZA,
                     mapeamento.ATRIBUTOS_DA_NATUREZA_RESTOS_A_PAGAR),
    }
    uris_da_linha = comum.escrever_compartilhadas(estado, linha, compartilhadas)
    uri_valor = comum.escrever_valor(estado, linha, 'valor-restos-a-pagar', mapeamento.CLASSE_VALOR_RESTOS_A_PAGAR,
                                     mapeamento.ATRIBUTOS_DO_VALOR_RESTOS_A_PAGAR)

    # 2. As entidades que existem uma vez por linha: a despesa, o registro e a classificação.
    ligacoes_do_registro = [
        (mapeamento.RELACAO_RESTOS_A_PAGAR_VALOR, uri_valor),
        (mapeamento.RELACAO_RESTOS_A_PAGAR_PODER, uris_da_linha['poder']),
    ]
    uri_registro = comum.escrever_registro(estado, NOME_DO_ARQUIVO, linha, mapeamento.CLASSE_REGISTRO_RESTOS_A_PAGAR,
                                           mapeamento.ATRIBUTOS_DO_REGISTRO_RESTOS_A_PAGAR, uris_da_linha['ug'],
                                           ligacoes_do_registro)
    comum.escrever_classificacao(estado, NOME_DO_ARQUIVO, linha, uri_registro, [
        (mapeamento.RELACAO_NATUREZA, uris_da_linha['natureza']),
    ])


def converter_linhas(linhas, destino) -> dict:
    """Converte todas as linhas e devolve o relatório com as contagens."""
    estado = comum.criar_estado(destino)
    for linha in linhas:
        _converter_linha(estado, linha)
    return montar_relatorio(estado)
