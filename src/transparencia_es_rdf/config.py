"""
Valores fixos do projeto, válidos para todas as bases.
"""

from pathlib import Path

# API do CKAN, o sistema por trás do dados.es.gov.br.
URL_API_CKAN = 'https://dados.es.gov.br/api/action'

# Endereço público do portal.
URL_PORTAL = 'https://dados.es.gov.br'


URL_BASE_DADOS = 'http://localhost:8000'

# Quanto tempo esperar a resposta da API antes de desistir, em segundos.
TIMEOUT_SEGUNDOS = 60

# Versão do grafo gerado (vai em owl:versionInfo e no fim do owl:versionIRI).
VERSAO_GRAFO = '1.0.0'

# Idioma dos textos (título e comentário), no formato de tag de idioma do RDF.
IDIOMA = 'pt-br'

# Autor da conversão (vai em dcterms:creator).
AUTOR = 'Miguel Gewehr de Oliveira'

# Pasta onde os .ttl gerados são gravados. O caminho é relativo à pasta em
# que o comando roda, por isso os comandos rodam na raiz do repositório.
PASTA_SAIDA = Path('saida')