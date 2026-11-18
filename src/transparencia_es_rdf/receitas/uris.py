"""Identificadores e URIs das entidades de Receitas.

Quando o CSV traz um código (natureza, conta, documento), a URI usa o código.
O registro, a classificação e o valor existem uma vez por linha, e o CSV não
tem uma coluna de identificador da linha: a URI deles usa a posição da linha
no arquivo (a coluna numeroDaLinha, que portal/leitura.py acrescenta). Assim
cada linha tem as suas URIs, mas elas não são estáveis: se o portal mudar a
ordem das linhas, o mesmo número passa a ser de outra linha. As URIs da UG e
da fonte não estão aqui: vêm do núcleo (nucleo/unidade_gestora.py e
nucleo/fonte.py), porque Despesas usa as mesmas.
"""

from transparencia_es_rdf.rdf.vocabularios import uri_de_dado


def uri_da_receita(ano: str, codigo_ug_emitente: str, documento: str) -> str:
    # O número do documento se repete entre UGs, então a receita é o par
    # UG emitente + documento, dentro do ano.
    return uri_de_dado('receitas', ano, 'receita', f'{codigo_ug_emitente}-{documento}')


def uri_do_registro(ano: str, numero_da_linha: str) -> str:
    return uri_de_dado('receitas', ano, 'registro', numero_da_linha)


def uri_da_classificacao(ano: str, numero_da_linha: str) -> str:
    # A classificação é de um registro só, então usa o número da linha dele.
    return uri_de_dado('receitas', ano, 'classificacao', numero_da_linha)


def uri_do_valor(ano: str, numero_da_linha: str) -> str:
    # O valor também é de um registro só.
    return uri_de_dado('receitas', ano, 'valor', numero_da_linha)


def uri_da_natureza(codigo_natureza: str) -> str:
    return uri_de_dado('natureza-receita', codigo_natureza)


def uri_da_conta(conta_contabil: str) -> str:
    return uri_de_dado('conta-contabil', conta_contabil)
