"""Valores fixos do projeto, que valem para todas as bases."""

from pathlib import Path

# Começo das URIs que a ferramenta cria: as dos dados (/id/...) e as das formas
# SHACL (/formas/...). É provisório, até o projeto ter um domínio definitivo.
URL_BASE_DADOS = 'http://localhost:8000'

# As pastas abaixo são relativas à pasta em que o comando roda, por isso os
# comandos rodam na raiz do repositório.

# Ontologia em OWL, que a validação lê para gerar as formas SHACL.
PASTA_ONTOLOGIA = Path('ontologia/out/ttl')

# Onde os comandos gravam o que geram, cada tipo de arquivo na sua pasta. As
# triplas vão para onde o comando converter mandar; o README sugere saida/rdf/.
PASTA_SAIDA = Path('saida')
PASTA_FORMAS = PASTA_SAIDA / 'formas'
PASTA_VALIDACAO = PASTA_SAIDA / 'validacao'
PASTA_BANCO = PASTA_SAIDA / 'banco'
PASTA_RESULTADOS_DAS_CONSULTAS = PASTA_SAIDA / 'consultas'
