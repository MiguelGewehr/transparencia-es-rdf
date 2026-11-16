"""Identificadores e URIs das entidades de Receitas.

Quando o CSV traz um código (natureza, conta, documento), a URI usa o código.
Quando não traz (registro, classificação, valor), a URI usa um identificador
calculado a partir da linha, de modo que linhas iguais dão a mesma URI. As
URIs da UG e da fonte não estão aqui: vêm do núcleo (nucleo/unidade_gestora.py
e nucleo/fonte.py), porque Despesas usa as mesmas.
"""

import hashlib
from decimal import Decimal

from transparencia_es_rdf.rdf.ntriples import numero_canonico
from transparencia_es_rdf.rdf.vocabularios import uri_de_dado

# Um registro reúne as linhas do CSV que são iguais nestas 12 colunas. No
# arquivo de 2025, estas 12 colunas e "todas as colunas menos os 10 valores"
# dão os mesmos 664.482 registros.
COLUNAS_QUE_IDENTIFICAM_O_REGISTRO = [
    'ano', 'documento', 'codigoUGEmitente',                            # a receita
    'codigoUG',                                                        # a UG beneficiada
    'codigoNatureza', 'codigoDetalhamentoFonteAux', 'contaContabil',   # a classificação
    'codigoIdUso', 'tipo', 'tipoLancamento',
    'dataEmissao', 'dataContabilizacao',
]

# Caractere posto entre os campos antes de calcular o resumo. Não aparece nos
# dados, e evita que "ab" + "c" e "a" + "bc" deem o mesmo texto.
SEPARADOR_DE_CAMPOS = '\x1f'


def identificador_do_registro(linha: dict) -> str:
    """Os 20 primeiros caracteres do SHA-256 das 12 colunas do registro.

    Com 20 caracteres (80 bits), a chance de dois registros diferentes terem o
    mesmo identificador é desprezível para algumas centenas de milhares.
    """
    texto = SEPARADOR_DE_CAMPOS.join(linha[coluna] for coluna in COLUNAS_QUE_IDENTIFICAM_O_REGISTRO)
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()[:20]


def chave_do_valor(numeros: list[Decimal]) -> str:
    """Os dez números da linha, na forma canônica, separados por "_".

    Exemplo: '0_0_0_0_0_0_0_0_64546.03_0'. Dois registros com os mesmos dez
    números apontam para o mesmo valor.
    """
    return '_'.join(numero_canonico(numero) for numero in numeros)


def uri_da_receita(ano: str, codigo_ug_emitente: str, documento: str) -> str:
    # O número do documento se repete entre UGs, então a receita é o par
    # UG emitente + documento, dentro do ano.
    return uri_de_dado('receitas', ano, 'receita', f'{codigo_ug_emitente}-{documento}')


def uri_do_registro(ano: str, identificador: str) -> str:
    return uri_de_dado('receitas', ano, 'registro', identificador)


def uri_da_classificacao(ano: str, identificador: str) -> str:
    # A classificação é de um registro só, então usa o identificador dele.
    return uri_de_dado('receitas', ano, 'classificacao', identificador)


def uri_do_valor(chave: str) -> str:
    return uri_de_dado('valor-receita', chave)


def uri_da_natureza(codigo_natureza: str) -> str:
    return uri_de_dado('natureza-receita', codigo_natureza)


def uri_da_conta(conta_contabil: str) -> str:
    return uri_de_dado('conta-contabil', conta_contabil)
