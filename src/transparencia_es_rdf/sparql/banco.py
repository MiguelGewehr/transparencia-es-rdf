"""O banco de triplas em disco, para rodar consultas SPARQL nos arquivos completos.

O banco é do Oxigraph (biblioteca pyoxigraph) e fica numa pasta. Ele guarda as
triplas em disco, e não na memória, então aguenta os arquivos completos, que
não cabem no rdflib.
"""

import gzip
import shutil
from pathlib import Path

from pyoxigraph import RdfFormat, Store


def carregar(arquivos: list[Path], pasta_banco: Path) -> int:
    """Apaga o banco antigo, carrega os N-Triples (.nt ou .nt.gz) e devolve quantas triplas o banco tem.

    O banco começa do zero a cada carga, para não misturar triplas de uma
    conversão antiga com as de uma nova. Uma tripla que aparece em mais de um
    arquivo (o código de uma UG, por exemplo) é guardada uma vez só.
    """
    if pasta_banco.exists():
        shutil.rmtree(pasta_banco)
    banco = Store(str(pasta_banco))
    for arquivo in arquivos:
        if arquivo.suffix == '.gz':
            with gzip.open(arquivo, 'rb') as entrada:
                banco.bulk_load(entrada, RdfFormat.N_TRIPLES)
        else:
            banco.bulk_load(path=arquivo, format=RdfFormat.N_TRIPLES)
    banco.flush()
    banco.optimize()
    return len(banco)


def consultar(pasta_banco: Path, consulta: str) -> tuple[list[str], list[list[str]]]:
    """Roda uma consulta SELECT e devolve os nomes das colunas e as linhas do resultado.

    Cada valor vem como texto: o número, o texto ou a URI. Um valor que a
    consulta deixou sem resposta (de um OPTIONAL, por exemplo) vem vazio.
    """
    banco = Store.read_only(str(pasta_banco))
    resultado = banco.query(consulta)
    colunas = [variavel.value for variavel in resultado.variables]
    linhas = [[valor.value if valor is not None else '' for valor in solucao] for solucao in resultado]
    return colunas, linhas
