"""O que os conversores dos quatro arquivos de Despesas fazem do mesmo jeito.

Cada arquivo tem o seu conversor: conversor_despesas.py para o arquivo Despesas e
conversor_restos_a_pagar.py, conversor_orcamentos_despesa.py e
conversor_orcamentos_execucoes.py para os outros três. Todo registro, de
qualquer um dos quatro arquivos, tem uma despesa, uma UG e um valor, e três
deles têm uma classificação. As funções que escrevem essas partes ficam aqui,
para os quatro conversores escreverem do mesmo jeito.
"""

from datetime import datetime
from decimal import Decimal

from transparencia_es_rdf.despesas import mapeamento, uris
from transparencia_es_rdf.nucleo.unidade_gestora import completar_codigo
from transparencia_es_rdf.rdf.escrita import (atributos_preenchidos, criar_estado_comum, escrever,
                                              escrever_entidade_compartilhada)
from transparencia_es_rdf.rdf.ntriples import literal_de_decimal, uri
from transparencia_es_rdf.rdf.vocabularios import RDF_TYPE


def criar_estado(destino) -> dict:
    """O estado comum (rdf/escrita.py), com as colunas de data e hora de Despesas."""
    return criar_estado_comum(destino, mapeamento.COLUNAS_DE_DATA_E_HORA)


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


def preparar_linha(linha: dict, colunas_dos_valores) -> dict:
    """Uma cópia da linha com os textos no formato que o RDF pede.

    - tira os espaços das pontas de todas as colunas (no arquivo Despesas de
      2025, o nome da UG vem com espaço nas pontas em 830.386 linhas);
    - nos valores, a vírgula decimal vira ponto: '308,0000' vira '308.0000';
    - o código da UG ganha os zeros da frente, para ser o mesmo de Receitas.

    A data, quando o arquivo tem, cada conversor converte depois.
    """
    preparada = {coluna: texto.strip() for coluna, texto in linha.items()}
    for coluna in colunas_dos_valores:
        preparada[coluna] = preparada[coluna].replace(',', '.')
    preparada['CodigoUnidadeGestora'] = completar_codigo(preparada['CodigoUnidadeGestora'])
    return preparada


# ---------------------------------------------------------------------------
# Escrita das partes que os quatro arquivos têm
# ---------------------------------------------------------------------------

def escrever_compartilhadas(estado: dict, linha: dict, compartilhadas: dict) -> dict:
    """Escreve as entidades que muitas linhas repetem e devolve as URIs delas.

    compartilhadas é um dicionário nome -> (URI, classe, atributos). As que
    a linha não tem chegam com a URI None: não são escritas e ficam com None
    no dicionário devolvido, para que a ligação também não seja escrita.
    """
    uris_da_linha = {}
    for nome, (uri_entidade, classe, atributos) in compartilhadas.items():
        uris_da_linha[nome] = uri_entidade
        if uri_entidade is not None:
            escrever_entidade_compartilhada(estado, uri_entidade, classe, atributos, linha)
    return uris_da_linha


def escrever_valor(estado: dict, nome_do_arquivo: str, linha: dict, classe: str, atributos_do_valor: dict) -> str:
    """Escreve os números da linha como o valor do registro e devolve a URI do valor.

    O valor é de um registro só, então a URI usa o Id da linha, como a do
    registro. Duas linhas com os mesmos números têm dois valores diferentes.
    """
    uri_valor = uris.uri_por_linha(nome_do_arquivo, linha, 'valor')
    escrever(estado, uri_valor, RDF_TYPE, uri(classe))
    for coluna, propriedade_do_valor in atributos_do_valor.items():
        escrever(estado, uri_valor, propriedade_do_valor, literal_de_decimal(Decimal(linha[coluna])))
    return uri_valor


def _escrever_ligacoes(estado: dict, uri_sujeito: str, ligacoes: list[tuple[str, str | None]]) -> None:
    """Escreve cada par (propriedade, URI da entidade), pulando os que têm URI None."""
    for relacao, uri_entidade in ligacoes:
        if uri_entidade is not None:
            escrever(estado, uri_sujeito, relacao, uri(uri_entidade))


def escrever_registro(estado: dict, nome_do_arquivo: str, linha: dict, classe_do_registro: str,
                      atributos_do_registro: dict, uri_ug: str, outras_ligacoes: list) -> str:
    """Escreve a despesa e o registro da linha, com as ligações do registro, e devolve a URI do registro.

    Todo registro, dos quatro arquivos, tem a despesa e a UG (as duas
    relações são de RegistroDeDespesaOrcamentaria). As outras ligações
    dependem do tipo de registro e vêm em outras_ligacoes.
    """
    uri_despesa = uris.uri_por_linha(nome_do_arquivo, linha, 'despesa')
    escrever(estado, uri_despesa, RDF_TYPE, uri(mapeamento.CLASSE_DESPESA))
    for propriedade_do_atributo, literal in atributos_preenchidos(estado, mapeamento.ATRIBUTOS_DA_DESPESA, linha):
        escrever(estado, uri_despesa, propriedade_do_atributo, literal)

    uri_registro = uris.uri_por_linha(nome_do_arquivo, linha, 'registro')
    escrever(estado, uri_registro, RDF_TYPE, uri(classe_do_registro))
    for propriedade_do_atributo, literal in atributos_preenchidos(estado, atributos_do_registro, linha):
        escrever(estado, uri_registro, propriedade_do_atributo, literal)

    ligacoes = [
        (mapeamento.RELACAO_TEM_DESPESA, uri_despesa),
        (mapeamento.RELACAO_TEM_UG, uri_ug),
    ] + outras_ligacoes
    _escrever_ligacoes(estado, uri_registro, ligacoes)
    return uri_registro


def escrever_classificacao(estado: dict, nome_do_arquivo: str, linha: dict, uri_registro: str,
                           classificadores: list[tuple[str, str]]) -> str:
    """Escreve a classificação que classifica o registro e devolve a URI dela.

    classificadores são os pares (relação, URI do classificador) que o
    arquivo tem: o arquivo Despesas tem os cinco; o RestosAPagar, só a natureza.
    """
    uri_classificacao = uris.uri_por_linha(nome_do_arquivo, linha, 'classificacao')
    escrever(estado, uri_classificacao, RDF_TYPE, uri(mapeamento.CLASSE_CLASSIFICACAO))
    escrever(estado, uri_classificacao, mapeamento.RELACAO_CLASSIFICA, uri(uri_registro))
    _escrever_ligacoes(estado, uri_classificacao, classificadores)
    return uri_classificacao


def escrever_classificador_institucional(estado: dict, nome_do_arquivo: str, linha: dict, uri_classificacao: str,
                                         ligacoes: list[tuple[str, str]]) -> None:
    """Escreve o classificador institucional, que liga a classificação ao órgão e à unidade orçamentária.

    A ontologia liga o classificador às duas entidades, mas cada arquivo só
    tem uma: o arquivo Despesas tem o órgão, e o OrcamentosDespesa, a unidade
    orçamentária. ligacoes traz a que o arquivo tem.
    """
    uri_institucional = uris.uri_por_linha(nome_do_arquivo, linha, 'classificador-institucional')
    escrever(estado, uri_institucional, RDF_TYPE, uri(mapeamento.CLASSE_CLASSIFICADOR_INSTITUCIONAL))
    escrever(estado, uri_institucional, mapeamento.RELACAO_INSTITUCIONAL_CLASSIFICACAO, uri(uri_classificacao))
    _escrever_ligacoes(estado, uri_institucional, ligacoes)
