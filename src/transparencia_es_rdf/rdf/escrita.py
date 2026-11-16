from collections import Counter

from transparencia_es_rdf.rdf.ntriples import (escrever_tripla, literal_de_data_e_hora, literal_de_texto, uri)
from transparencia_es_rdf.rdf.vocabularios import RDF_TYPE


def criar_estado_comum(destino, colunas_de_data_e_hora: set[str]) -> dict:
    """O que toda conversão precisa lembrar de uma linha para a outra."""
    return {
        'destino': destino,
        'colunas_de_data_e_hora': colunas_de_data_e_hora,
        'entidades_vistas': set(),
        'triplas_compartilhadas_escritas': set(),
        'linhas_lidas': 0,
        'triplas_escritas': 0,
        'entidades_por_classe': Counter(),
    }


def escrever(estado: dict, sujeito: str, predicado: str, objeto: str) -> None:
    """Escreve uma tripla e atualiza as contagens do relatório."""
    escrever_tripla(estado['destino'], sujeito, predicado, objeto)
    estado['triplas_escritas'] += 1
    if predicado == RDF_TYPE:
        classe = objeto[1:-1]                             
        estado['entidades_por_classe'][classe] += 1


def escrever_uma_vez(estado: dict, sujeito: str, predicado: str, objeto: str) -> None:
    """Como escrever(), mas pula a tripla se ela já foi escrita antes."""
    tripla = (sujeito, predicado, objeto)
    if tripla in estado['triplas_compartilhadas_escritas']:
        return
    estado['triplas_compartilhadas_escritas'].add(tripla)
    escrever(estado, sujeito, predicado, objeto)


def atributos_preenchidos(estado: dict, atributos: dict, linha: dict) -> list[tuple[str, str]]:
    """Os pares (propriedade, literal) das colunas que têm texto.

    Uma célula vazia não vira tripla: uma tripla com texto vazio afirmaria
    que a descrição é um texto vazio, o que é diferente de não ter descrição.
    Os espaços das pontas são tirados. As colunas de data e hora da base
    viram xsd:dateTime; as outras, texto.
    """
    pares = []
    for coluna, propriedade_do_atributo in atributos.items():
        texto = linha[coluna].strip()
        if texto == '':
            continue
        if coluna in estado['colunas_de_data_e_hora']:
            literal = literal_de_data_e_hora(texto)
        else:
            literal = literal_de_texto(texto)
        pares.append((propriedade_do_atributo, literal))
    return pares


def escrever_entidade_compartilhada(estado: dict, uri_entidade: str, classe: str,
                                    atributos: dict, linha: dict) -> None:
    """Escreve o tipo e os atributos de uma entidade que muitas linhas repetem.

    É o caso das UGs e das fontes, nas duas bases, e de tudo o que o CSV
    identifica por um código. Dois conjuntos evitam repetição:
    - entidades_vistas: se a entidade já apareceu com estes mesmos textos, não
      há nada novo nesta linha, e a função sai logo (isso poupa tempo nos
      arquivos de mais de 1 milhão de linhas);
    - triplas_compartilhadas_escritas: se a entidade volta com um texto
      diferente (15 receitas têm duas datas de emissão em 2025), só a tripla
      nova é escrita.
    """
    textos = tuple(linha[coluna].strip() for coluna in atributos)
    assinatura = (uri_entidade, classe, textos)
    if assinatura in estado['entidades_vistas']:
        return
    estado['entidades_vistas'].add(assinatura)

    escrever_uma_vez(estado, uri_entidade, RDF_TYPE, uri(classe))
    for propriedade_do_atributo, literal in atributos_preenchidos(estado, atributos, linha):
        escrever_uma_vez(estado, uri_entidade, propriedade_do_atributo, literal)


def relatorio_comum(estado: dict) -> dict:
    """As contagens que o cli.py mostra no fim, com o nome curto de cada classe.

    O nome curto é o que vem depois do "#" na URI da classe:
    .../base-receitas#ContaContabil vira ContaContabil.
    """
    entidades_por_classe = {}
    for classe, quantidade in estado['entidades_por_classe'].items():
        entidades_por_classe[classe.split('#')[-1]] = quantidade
    return {
        'linhas_lidas': estado['linhas_lidas'],
        'triplas_escritas': estado['triplas_escritas'],
        'entidades_por_classe': dict(sorted(entidades_por_classe.items())),
    }