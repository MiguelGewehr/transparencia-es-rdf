"""Escrita de triplas em N-Triples: uma tripla por linha do arquivo.

Cada linha tem a forma

    <sujeito> <predicado> objeto .

em que o objeto é uma URI entre < > ou um literal entre aspas. Este arquivo só
formata e escreve: não sabe o que é receita ou despesa.
"""

import gzip
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from transparencia_es_rdf.rdf.vocabularios import XSD_DATETIME, XSD_DECIMAL


def uri(endereco: str) -> str:
    """Uma URI no formato do N-Triples: o endereço entre < >."""
    return f'<{endereco}>'


def literal_de_texto(texto: str) -> str:
    """Um texto entre aspas, com a barra, as aspas e as quebras de linha escapadas."""
    escapado = (texto.replace('\\', '\\\\').replace('"', '\\"')
                .replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t'))
    return f'"{escapado}"'


def literal_de_data_e_hora(texto: str) -> str:
    """'2025-08-26T00:00:00' vira um xsd:dateTime.

    O strptime confere o formato: se a data vier de outro jeito, a conversão
    para com um erro em vez de gravar uma data inválida.
    """
    data = datetime.strptime(texto, '%Y-%m-%dT%H:%M:%S')
    return f'"{data.isoformat()}"^^<{XSD_DATETIME}>'


def numero_canonico(numero: Decimal) -> str:
    """O número sem zeros sobrando: '308.0000' vira '308' e '0.00' vira '0'.

    Assim o mesmo valor escrito de jeitos diferentes no CSV vira o mesmo texto,
    no literal e nas URIs dos valores.
    """
    if numero == 0:
        return '0'
    return format(numero.normalize(), 'f')


def literal_de_decimal(numero: Decimal) -> str:
    """Um número como xsd:decimal, na forma canônica."""
    return f'"{numero_canonico(numero)}"^^<{XSD_DECIMAL}>'


def escrever_tripla(destino, sujeito: str, predicado: str, objeto: str) -> None:
    """Escreve uma linha do N-Triples. O objeto já vem formatado (uri() ou literal_de_...)."""
    destino.write(f'<{sujeito}> <{predicado}> {objeto} .\n')


def abrir_saida(caminho: Path):
    """Abre o arquivo de saída para escrita, criando a pasta se precisar.

    Se o nome terminar em .gz, o arquivo sai compactado. O newline='\\n' faz
    a quebra de linha ser a mesma em qualquer sistema, para o SHA-256 da
    saída não depender do computador.
    """
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if caminho.suffix == '.gz':
        return gzip.open(caminho, 'wt', encoding='utf-8', newline='\n', compresslevel=5)
    return open(caminho, 'w', encoding='utf-8', newline='\n')
