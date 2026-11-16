"""
Escrita de triplas em N-Triples: uma tripla por linha do arquivo.

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
    return f'<{endereco}>'

def literal_de_texto(texto: str) -> str:
    escapado = (texto.replace('\\', '\\\\').replace('"', '\\"')
                .replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t'))

    return f'"{escapado}"'

def literal_de_data_e_hora(texto: str) -> str:
    data = datetime.strptime(texto, '%Y-%m-%dT%H:%M:%S')
    return f'"{data.isoformat()}"^^<{XSD_DATETIME}>'

def numero_canonico(numero: Decimal) -> str: 

    if numero == 0:
        return '0'

    return format(numero.normalize(), 'f')

def literal_de_decimal(numero: Decimal) -> str: 
    return f'"{numero_canonico(numero)}"^^<{XSD_DECIMAL}>'

def escrever_tripla(destino, sujeito: str, predicado: str, objeto: str) -> None:
    destino.write(f'<{sujeito}> <{predicado}> {objeto} .\n')

def abrir_saida(caminho: Path): 
    
    caminho.parent.mkdir(parents=True, exist_ok=True)

    if caminho.suffix == '.gz':
        return gzip.open(caminho, 'wt', encoding='utf-8', newline='\n', compresslevel=5)
    
    return open(caminho, 'w', encoding='utf-8', newline='\n')

