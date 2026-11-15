import hashlib
from decimal import Decimal

from transparencia_es_rdf.rdf.ntriples import numero_canonico
from transparencia_es_rdf.rdf.vocabularios import uri_de_dado

COLUNAS_QUE_IDENTIFICAM_O_REGISTRO = [
    'ano', 'documento', 'codigoUGEmitente',
    'codigoUG',                            
    'codigoNatureza', 'codigoDetalhamentoFonteAux', 'contaContabil',   
    'codigoIdUso', 'tipo', 'tipoLancamento',
    'dataEmissao', 'dataContabilizacao',
]

SEPARADOR_DE_CAMPOS = '\x1f'

def identificador_do_registro(linha: dict) -> str:

    texto = SEPARADOR_DE_CAMPOS.join(linha[coluna] for coluna in COLUNAS_QUE_IDENTIFICAM_O_REGISTRO)

    return hashlib.sha256(texto.encode('utf-8')).hexdigest()[:20]

def chave_do_valor(numeros: list[Decimal]) -> str:
    return '_'.join(numero_canonico(numero) for numero in numeros)

def uri_da_receita(ano: str, codigo_ug_emitente: str, documento: str) -> str:
    return uri_de_dado('receitas', ano, 'receita', f'{codigo_ug_emitente}-{documento}')

def uri_do_registro(ano: str, identificador: str) -> str:
    return uri_de_dado('receitas', ano, 'registro', identificador)

def uri_da_classificacao(ano: str, identificador: str):
    return uri_de_dado('receitas', ano, 'classificacao', identificador)

def uri_do_valor(chave: str) -> str:
    return uri_de_dado('valor-receita', chave)


def uri_da_natureza(codigo_natureza: str) -> str:
    return uri_de_dado('natureza-receita', codigo_natureza)


def uri_da_fonte(codigo_detalhamento_fonte_aux: str) -> str:
    return uri_de_dado('fonte', codigo_detalhamento_fonte_aux)


def uri_da_conta(conta_contabil: str) -> str:
    return uri_de_dado('conta-contabil', conta_contabil)