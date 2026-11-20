"""Conversão das linhas do arquivo OrcamentosExecucoes em triplas.

O que a ontologia (commit 5937382) diz que uma linha descreve:

    Registro --temDespesaOrcamentaria---------> Despesa
    Registro --temUnidadeGestoraDaDespesa-----> UG (com a sigla)
    Registro --valorAtrelado------------------> Valor (os 6 números da linha)

O arquivo não tem classificadores. Também não tem a coluna Ano, que a
despesa pede (DespesaOrcamentariaRegistrada.ano): o ano sai da coluna Data.
No arquivo de 2025, as 125 linhas têm a mesma data, 01/01/2025.
"""

from transparencia_es_rdf.despesas import comum, mapeamento
from transparencia_es_rdf.nucleo.unidade_gestora import uri_da_unidade_gestora
from transparencia_es_rdf.rdf.escrita import montar_relatorio

NOME_DO_ARQUIVO = 'orcamentos-execucoes'


def _converter_linha(estado: dict, linha: dict) -> None:
    """Escreve tudo o que uma linha do CSV descreve."""
    estado['linhas_lidas'] += 1
    linha = comum.preparar_linha(linha, mapeamento.ATRIBUTOS_DO_VALOR_ORCAMENTO_EXECUCAO)
    linha['Data'] = comum.data_no_formato_iso(linha['Data'])
    linha['Ano'] = linha['Data'][:4]                  # '2025-01-01T00:00:00' -> '2025'

    # 1. As entidades que muitas linhas repetem: só a UG.
    uris_da_linha = comum.escrever_compartilhadas(estado, linha, {
        'ug': (uri_da_unidade_gestora(linha['CodigoUnidadeGestora']), mapeamento.CLASSE_UG,
               mapeamento.ATRIBUTOS_DA_UG_COM_SIGLA),
    })
    uri_valor = comum.escrever_valor(estado, NOME_DO_ARQUIVO, linha,
                                     mapeamento.CLASSE_VALOR_ORCAMENTO_EXECUCAO,
                                     mapeamento.ATRIBUTOS_DO_VALOR_ORCAMENTO_EXECUCAO)

    # 2. As entidades que existem uma vez por linha: a despesa e o registro.
    ligacoes_do_registro = [(mapeamento.RELACAO_EXECUCAO_VALOR, uri_valor)]
    comum.escrever_registro(estado, NOME_DO_ARQUIVO, linha, mapeamento.CLASSE_REGISTRO_ORCAMENTO_EXECUCAO,
                            mapeamento.ATRIBUTOS_DO_REGISTRO_ORCAMENTO_EXECUCAO, uris_da_linha['ug'],
                            ligacoes_do_registro)


def converter_linhas(linhas, destino) -> dict:
    """Converte todas as linhas e devolve o relatório com as contagens."""
    estado = comum.criar_estado(destino)
    for linha in linhas:
        _converter_linha(estado, linha)
    return montar_relatorio(estado)
