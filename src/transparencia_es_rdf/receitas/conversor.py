"""Conversão das linhas do CSV de Receitas em triplas.

Recebe as linhas já lidas (portal/leitura.py) e um destino já aberto para
escrita (rdf/ntriples.py). Não abre arquivo, não baixa e não valida.

O que a ontologia diz que uma linha descreve (cada seta é uma propriedade):

    Registro      --temReceitaOrcamentaria--------> Receita
    Registro      --temUnidadeGestoraEmitente-----> UG emitente
    Registro      --temUnidadeGestoraBeneficiada--> UG beneficiada
    Registro      --valorAtreladoNaReceita--------> Valor (os 10 números da linha)
    Classificação --classifica--------------------> Registro
    Classificação --naturezaClassificadaPor-------> Natureza
    Classificação --fonteClassificadaPor----------> Fonte
    Classificação --contabilClassificadaPor-------> Conta

O registro, a classificação e o valor são um por linha, e a URI deles usa o
número da linha (receitas/uris.py). Já a receita, a UG, a natureza, a fonte e
a conta se repetem em muitas linhas, e cada uma é escrita uma vez só. As
funções que escrevem sem repetir estão em rdf/escrita.py, porque Despesas
usa as mesmas.
"""

from decimal import Decimal

from transparencia_es_rdf.nucleo.fonte import uri_da_fonte
from transparencia_es_rdf.nucleo.unidade_gestora import uri_da_unidade_gestora
from transparencia_es_rdf.portal.leitura import COLUNA_NUMERO_DA_LINHA
from transparencia_es_rdf.rdf.escrita import (atributos_preenchidos, criar_estado_comum, escrever,
                                              escrever_entidade_compartilhada, montar_relatorio)
from transparencia_es_rdf.rdf.ntriples import literal_de_decimal, uri
from transparencia_es_rdf.rdf.vocabularios import RDF_TYPE
from transparencia_es_rdf.receitas import mapeamento, uris


def _escrever_registro_e_classificacao(estado: dict, linha: dict, uris_da_linha: dict) -> str:
    """Escreve o registro da linha e a classificação dele, e devolve a URI do registro."""
    ano = linha['ano']
    numero_da_linha = linha[COLUNA_NUMERO_DA_LINHA]
    uri_registro = uris.uri_do_registro(ano, numero_da_linha)

    # O registro: tipo, atributos e as ligações com a receita e as duas UGs.
    escrever(estado, uri_registro, RDF_TYPE, uri(mapeamento.CLASSE_REGISTRO))
    for propriedade_do_atributo, literal in atributos_preenchidos(estado, mapeamento.ATRIBUTOS_DO_REGISTRO, linha):
        escrever(estado, uri_registro, propriedade_do_atributo, literal)
    escrever(estado, uri_registro, mapeamento.RELACAO_TEM_RECEITA, uri(uris_da_linha['receita']))
    escrever(estado, uri_registro, mapeamento.RELACAO_TEM_UG_EMITENTE, uri(uris_da_linha['ug_emitente']))
    escrever(estado, uri_registro, mapeamento.RELACAO_TEM_UG_BENEFICIADA, uri(uris_da_linha['ug_beneficiada']))

    # A classificação: liga o registro à natureza, à fonte e à conta.
    uri_classificacao = uris.uri_da_classificacao(ano, numero_da_linha)
    escrever(estado, uri_classificacao, RDF_TYPE, uri(mapeamento.CLASSE_CLASSIFICACAO))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_CLASSIFICA, uri(uri_registro))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_NATUREZA, uri(uris_da_linha['natureza']))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_FONTE, uri(uris_da_linha['fonte']))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_CONTA, uri(uris_da_linha['conta']))
    return uri_registro


def _escrever_valor_do_registro(estado: dict, linha: dict, uri_registro: str) -> None:
    """Escreve os dez números da linha como o valor do registro e liga o registro a ele."""
    uri_valor = uris.uri_do_valor(linha['ano'], linha[COLUNA_NUMERO_DA_LINHA])
    escrever(estado, uri_valor, RDF_TYPE, uri(mapeamento.CLASSE_VALOR))
    for coluna in mapeamento.COLUNAS_DOS_VALORES:
        escrever(estado, uri_valor, mapeamento.ATRIBUTOS_DO_VALOR[coluna], literal_de_decimal(Decimal(linha[coluna])))
    escrever(estado, uri_registro, mapeamento.RELACAO_TEM_VALOR, uri(uri_valor))


def _converter_linha(estado: dict, linha: dict) -> None:
    """Escreve tudo o que uma linha do CSV descreve."""
    estado['linhas_lidas'] += 1

    # 1. As entidades que muitas linhas repetem, cada uma com a sua URI.
    uris_da_linha = {
        'ug_emitente': uri_da_unidade_gestora(linha['codigoUGEmitente']),
        'ug_beneficiada': uri_da_unidade_gestora(linha['codigoUG']),
        'natureza': uris.uri_da_natureza(linha['codigoNatureza']),
        'fonte': uri_da_fonte(linha['codigoDetalhamentoFonteAux']),
        'conta': uris.uri_da_conta(linha['contaContabil']),
        'receita': uris.uri_da_receita(linha['ano'], linha['codigoUGEmitente'], linha['documento']),
    }
    escrever_entidade_compartilhada(estado, uris_da_linha['ug_emitente'], mapeamento.CLASSE_UG_EMITENTE,
                                    mapeamento.ATRIBUTOS_DA_UG_EMITENTE, linha)
    escrever_entidade_compartilhada(estado, uris_da_linha['ug_beneficiada'], mapeamento.CLASSE_UG_BENEFICIADA,
                                    mapeamento.ATRIBUTOS_DA_UG_BENEFICIADA, linha)
    escrever_entidade_compartilhada(estado, uris_da_linha['natureza'], mapeamento.CLASSE_NATUREZA,
                                    mapeamento.ATRIBUTOS_DA_NATUREZA, linha)
    escrever_entidade_compartilhada(estado, uris_da_linha['fonte'], mapeamento.CLASSE_FONTE,
                                    mapeamento.ATRIBUTOS_DA_FONTE, linha)
    escrever_entidade_compartilhada(estado, uris_da_linha['conta'], mapeamento.CLASSE_CONTA,
                                    mapeamento.ATRIBUTOS_DA_CONTA, linha)
    escrever_entidade_compartilhada(estado, uris_da_linha['receita'], mapeamento.CLASSE_RECEITA,
                                    mapeamento.ATRIBUTOS_DA_RECEITA, linha)

    # 2. O registro e a sua classificação.
    uri_registro = _escrever_registro_e_classificacao(estado, linha, uris_da_linha)

    # 3. O valor da linha, ligado ao registro.
    _escrever_valor_do_registro(estado, linha, uri_registro)


def converter_linhas(linhas, destino) -> dict:
    """Converte todas as linhas e devolve o relatório com as contagens."""
    estado = criar_estado_comum(destino, mapeamento.COLUNAS_DE_DATA_E_HORA)
    for linha in linhas:
        _converter_linha(estado, linha)
    return montar_relatorio(estado)
