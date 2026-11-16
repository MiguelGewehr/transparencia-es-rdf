"""Conversão das linhas do CSV de Despesas em triplas.

Funciona como o conversor de Receitas: recebe as linhas já lidas
(portal/leitura.py) e um destino já aberto para escrita (rdf/ntriples.py), e
usa as mesmas funções de rdf/escrita.py para não repetir triplas.

O que a ontologia (commit e0fff39) diz que uma linha descreve (cada seta é
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

from datetime import datetime
from decimal import Decimal

from transparencia_es_rdf.despesas import mapeamento, uris
from transparencia_es_rdf.nucleo.fonte import uri_da_fonte
from transparencia_es_rdf.nucleo.unidade_gestora import completar_codigo, uri_da_unidade_gestora
from transparencia_es_rdf.rdf.escrita import (atributos_preenchidos, criar_estado_comum, escrever,
                                              escrever_entidade_compartilhada, relatorio_comum)
from transparencia_es_rdf.rdf.ntriples import literal_de_decimal, uri
from transparencia_es_rdf.rdf.vocabularios import RDF_TYPE


def criar_estado(destino) -> dict:
    """O estado comum (rdf/escrita.py) mais o que só Despesas precisa lembrar."""
    estado = criar_estado_comum(destino, mapeamento.COLUNAS_DE_DATA_E_HORA)
    estado['valores_escritos'] = set()               # URIs dos valores já escritos
    return estado


# ---------------------------------------------------------------------------
# Preparação da linha
# ---------------------------------------------------------------------------

def data_no_formato_iso(texto: str) -> str:
    """'26/08/2025 00:00:00' vira '2025-08-26T00:00:00', o formato do xsd:dateTime.

    O strptime lê o texto no formato do portal e para com um ValueError claro
    se a data vier em outro formato; o isoformat escreve no formato do RDF.
    """
    data_e_hora = datetime.strptime(texto, '%d/%m/%Y %H:%M:%S')
    return data_e_hora.isoformat()


def preparar_linha(linha: dict) -> dict:
    """Uma cópia da linha com os textos no formato que o RDF pede.

    - tira os espaços das pontas de todas as colunas (no arquivo de 2025, o
      nome da UG vem com espaço nas pontas em 830.386 linhas);
    - a data vira AAAA-MM-DDThh:mm:ss;
    - nos quatro valores, a vírgula decimal vira ponto: '308,0000' vira '308.0000';
    - o código da UG ganha os zeros da frente, para ser o mesmo de Receitas.
    """
    preparada = {coluna: texto.strip() for coluna, texto in linha.items()}
    preparada['Data'] = data_no_formato_iso(preparada['Data'])
    for coluna in mapeamento.COLUNAS_DOS_VALORES:
        preparada[coluna] = preparada[coluna].replace(',', '.')
    preparada['CodigoUnidadeGestora'] = completar_codigo(preparada['CodigoUnidadeGestora'])
    return preparada


# ---------------------------------------------------------------------------
# As entidades de uma linha
# ---------------------------------------------------------------------------

def escrever_valor(estado: dict, linha: dict) -> str:
    """Escreve o conjunto de quatro números da linha, se ainda não foi escrito, e devolve a URI dele.

    É como o valor de Receitas: a URI é feita dos próprios números, então uma
    URI já vista não tem nada de novo. Guardar só a URI, e não as triplas,
    poupa memória: em 2025 são 514.075 valores diferentes.
    """
    numeros = [Decimal(linha[coluna]) for coluna in mapeamento.COLUNAS_DOS_VALORES]
    uri_valor = uris.uri_do_valor(numeros)
    if uri_valor not in estado['valores_escritos']:
        estado['valores_escritos'].add(uri_valor)
        escrever(estado, uri_valor, RDF_TYPE, uri(mapeamento.CLASSE_VALOR))
        for coluna, numero in zip(mapeamento.COLUNAS_DOS_VALORES, numeros):
            escrever(estado, uri_valor, mapeamento.ATRIBUTOS_DO_VALOR[coluna], literal_de_decimal(numero))
    return uri_valor


def escrever_despesa_e_registro(estado: dict, linha: dict, uris_da_linha: dict) -> str:
    """Escreve a despesa e o registro da linha, com as ligações do registro."""
    uri_despesa = uris.uri_por_linha(linha, 'despesa')
    escrever(estado, uri_despesa, RDF_TYPE, uri(mapeamento.CLASSE_DESPESA))
    for propriedade_do_atributo, literal in atributos_preenchidos(estado, mapeamento.ATRIBUTOS_DA_DESPESA, linha):
        escrever(estado, uri_despesa, propriedade_do_atributo, literal)

    uri_registro = uris.uri_por_linha(linha, 'registro')
    escrever(estado, uri_registro, RDF_TYPE, uri(mapeamento.CLASSE_REGISTRO))
    for propriedade_do_atributo, literal in atributos_preenchidos(estado, mapeamento.ATRIBUTOS_DO_REGISTRO, linha):
        escrever(estado, uri_registro, propriedade_do_atributo, literal)

    # As ligações: (propriedade, URI da entidade). As que a linha não tem
    # ficaram com None em uris_da_linha e não são escritas.
    ligacoes = [
        (mapeamento.RELACAO_TEM_DESPESA, uri_despesa),
        (mapeamento.RELACAO_TEM_UG, uris_da_linha['ug']),
        (mapeamento.RELACAO_TEM_VALOR, uris_da_linha['valor']),
        (mapeamento.RELACAO_FAVORECIDO, uris_da_linha['favorecido']),
        (mapeamento.RELACAO_LICITACAO, uris_da_linha['licitacao']),
        (mapeamento.RELACAO_PROCESSO, uris_da_linha['processo']),
        (mapeamento.RELACAO_RETENCAO, uris_da_linha['retencao']),
        (mapeamento.RELACAO_BANCO, uris_da_linha['banco']),
        (mapeamento.RELACAO_CONVENIO_CONCEDIDO, uris_da_linha['convenio_concedido']),
        (mapeamento.RELACAO_CONVENIO_RECEBIDO, uris_da_linha['convenio_recebido']),
    ]
    for relacao, uri_entidade in ligacoes:
        if uri_entidade is not None:
            escrever(estado, uri_registro, relacao, uri(uri_entidade))
    return uri_registro


def escrever_classificacao(estado: dict, linha: dict, uris_da_linha: dict, uri_registro: str) -> None:
    """Escreve a classificação da linha e o classificador institucional dela."""
    uri_classificacao = uris.uri_por_linha(linha, 'classificacao')
    escrever(estado, uri_classificacao, RDF_TYPE, uri(mapeamento.CLASSE_CLASSIFICACAO))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_CLASSIFICA, uri(uri_registro))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_FUNCIONAL, uri(uris_da_linha['funcional']))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_PROGRAMATICA, uri(uris_da_linha['programatica']))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_NATUREZA, uri(uris_da_linha['natureza']))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_FONTE, uri(uris_da_linha['fonte']))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_ESFERA, uri(uris_da_linha['esfera']))

    # O classificador institucional liga a classificação ao órgão. A ontologia
    # também o liga a uma unidade orçamentária, mas o CSV não tem essa coluna.
    uri_institucional = uris.uri_por_linha(linha, 'classificador-institucional')
    escrever(estado, uri_institucional, RDF_TYPE, uri(mapeamento.CLASSE_CLASSIFICADOR_INSTITUCIONAL))
    escrever(estado, uri_institucional, mapeamento.RELACAO_INSTITUCIONAL_CLASSIFICACAO, uri(uri_classificacao))
    escrever(estado, uri_institucional, mapeamento.RELACAO_INSTITUCIONAL_ORGAO, uri(uris_da_linha['orgao']))


def converter_linha(estado: dict, linha: dict) -> None:
    """Escreve tudo o que uma linha do CSV descreve."""
    estado['linhas_lidas'] += 1
    linha = preparar_linha(linha)

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
    uris_da_linha = {}
    for nome, (uri_entidade, classe, atributos) in compartilhadas.items():
        uris_da_linha[nome] = uri_entidade
        if uri_entidade is not None:
            escrever_entidade_compartilhada(estado, uri_entidade, classe, atributos, linha)
    uris_da_linha['valor'] = escrever_valor(estado, linha)

    # 2. As entidades que existem uma vez por linha.
    uri_registro = escrever_despesa_e_registro(estado, linha, uris_da_linha)
    escrever_classificacao(estado, linha, uris_da_linha, uri_registro)


def converter_linhas(linhas, destino) -> dict:
    """Converte todas as linhas e devolve o relatório com as contagens."""
    estado = criar_estado(destino)
    for linha in linhas:
        converter_linha(estado, linha)
    return relatorio_comum(estado)