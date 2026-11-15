from collections import Counter
from decimal import Decimal

from transparencia_es_rdf.nucleo.unidade_gestora import uri_da_unidade_gestora
from transparencia_es_rdf.rdf.ntriples import (escrever_tripla, literal_de_data_e_hora, literal_de_decimal, literal_de_texto, uri)
from transparencia_es_rdf.rdf.vocabularios import NAMESPACE_RECEITAS, RDF_TYPE
from transparencia_es_rdf.receitas import mapeamento, uris

def criar_estado(destino) -> dict:

    return {
        'destino' : destino,
        'entidades_vista' : set(),
        'triplas_compartilhadas_escritas': set(),
        'registros_escritos': set(), 
        'valores_escritos': set(),
        'ligacoes_registro_valor': set(),
        'linhas_lidas': 0,
        'linhas_repetidas': 0, 
        'triplas_escritas': 0,
        'entidades_por_classe': Counter(), 
    }

def escrever(estado: dict, sujeito: str, predicado: str, objeto: str) -> None:

    escrever_tripla(estado['destino'], sujeito, predicado, objeto)

    estado['triplas_escritas'] += 1

    if predicado == RDF_TYPE:
        classe = objeto[1:-1]
        estado['entidades_por_classe'][classe] += 1

def escrever_uma_vez(estado: dict, sujeito: str, predicado: str, objeto: str) -> None:

    tripla = (sujeito, predicado, objeto)

    if tripla in estado['triplas_compartilhadas_escritas']:
        return

    estado['triplas_compartilhadas_escritas'].add(tripla)

    escrever(estado, sujeito, predicado, objeto)

def atributos_preenchidos(atributos: dict, linha: dict) -> list[tuple[str, str]]:

    pares = []

    for coluna, propriedade_do_atributo in atributos.items():

        texto = linha[coluna].strip()

        if texto == '':
            continue
        if coluna in mapeamento.COLUNAS_DE_DATA_E_HORA:
            literal = literal_de_data_e_hora(texto)
        else:
            literal = literal_de_texto(texto)

        pares.append((propriedade_do_atributo, literal))

    return pares

def escrever_entidade_compartilhada(estado: dict, uri_entidade: str, classe: str, atributos: dict, linha: dict) -> None:

    textos = tuple(linha[coluna].strip() for coluna in atributos)
   
    assinatura = (uri_entidade, classe, textos)

    if assinatura in estado['entidades_vista']:
        return

    estado['entidades_vista'].add(assinatura)

    escrever_uma_vez(estado, uri_entidade, RDF_TYPE, uri(classe))

    for propriedade_do_atributo, literal in atributos_preenchidos(atributos, linha):
        escrever_uma_vez(estado, uri_entidade, propriedade_do_atributo, literal)

def escrever_registro_e_classificacao(estado: dict, linha: dict, identificador: str, uris_da_linha: dict) -> str:

    ano = linha['ano']

    uri_registro = uris.uri_do_registro(ano, identificador)

    if identificador in estado['registros_escritos']:
        return uri_registro

    estado['registros_escritos'].add(identificador)

    escrever(estado, uri_registro, RDF_TYPE, uri(mapeamento.CLASSE_REGISTRO))

    for propriedade_do_atributo, literal in atributos_preenchidos(mapeamento.ATRIBUTOS_DO_REGISTRO, linha):
        escrever(estado, uri_registro, propriedade_do_atributo, literal)
    
    escrever(estado, uri_registro, mapeamento.RELACAO_FORMALIZADA_POR, uri(uris_da_linha['receita']))
    escrever(estado, uri_registro, mapeamento.RELACAO_TEM_UG_EMITENTE, uri(uris_da_linha['ug_emitente']))
    escrever(estado, uri_registro, mapeamento.RELACAO_TEM_UG_BENEFICIADA, uri(uris_da_linha['ug_beneficiada']))

    uri_classificacao = uris.uri_da_classificacao(ano, identificador)
    
    escrever(estado, uri_classificacao, RDF_TYPE, uri(mapeamento.CLASSE_CLASSIFICACAO))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_CLASSIFICA, uri(uri_registro))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_NATUREZA, uri(uris_da_linha['natureza']))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_FONTE, uri(uris_da_linha['fonte']))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_CONTA, uri(uris_da_linha['conta']))
    
    return uri_registro

def escrever_valor_do_registro(estado: dict, linha: dict, identificador: str, uri_registro: str) -> None:
   
    numeros = [Decimal(linha[coluna]) for coluna in mapeamento.COLUNAS_DOS_VALORES]
    chave = uris.chave_do_valor(numeros)
    uri_valor = uris.uri_do_valor(chave)

    if chave not in estado['valores_escritos']:
        
        estado['valores_escritos'].add(chave)

        escrever(estado, uri_valor, RDF_TYPE, uri(mapeamento.CLASSE_VALOR))

        for coluna, numero in zip(mapeamento.COLUNAS_DOS_VALORES, numeros):
            escrever(estado, uri_valor, mapeamento.ATRIBUTOS_DO_VALOR[coluna], literal_de_decimal(numero))

    ligacao = (identificador, chave)

    if ligacao in estado['ligacoes_registro_valor']:
       
        estado['linhas_repetidas'] += 1
        return
    
    estado['ligacoes_registro_valor'].add(ligacao)
    escrever(estado, uri_registro, mapeamento.RELACAO_TEM_VALOR, uri(uri_valor))

def converter_linha(estado: dict, linha: dict) -> None:
   
    estado['linhas_lidas'] += 1

   
    uris_da_linha = {
        'ug_emitente': uri_da_unidade_gestora(linha['codigoUGEmitente']),
        'ug_beneficiada': uri_da_unidade_gestora(linha['codigoUG']),
        'natureza': uris.uri_da_natureza(linha['codigoNatureza']),
        'fonte': uris.uri_da_fonte(linha['codigoDetalhamentoFonteAux']),
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

    identificador = uris.identificador_do_registro(linha)
    uri_registro = escrever_registro_e_classificacao(estado, linha, identificador, uris_da_linha)

    escrever_valor_do_registro(estado, linha, identificador, uri_registro)

def converter_linhas(linhas, destino) -> dict:

    estado = criar_estado(destino)
    for linha in linhas:
        converter_linha(estado, linha)

    entidades_por_classe = {
        classe.replace(NAMESPACE_RECEITAS, ''): quantidade
        for classe, quantidade in sorted(estado['entidades_por_classe'].items())
    }
    return {
        'linhas_lidas': estado['linhas_lidas'],
        'triplas_escritas': estado['triplas_escritas'],
        'linhas_repetidas': estado['linhas_repetidas'],
        'entidades_por_classe': entidades_por_classe,
    }

