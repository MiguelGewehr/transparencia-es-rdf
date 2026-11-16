"""Como é o arquivo de Receitas no portal. Não abre o arquivo: só o descreve.

O pacote no dados.es.gov.br é o portal-da-transparencia-receitas, com um
arquivo Receitas-<ano>.csv por ano desde 16/10/2026.
"""

# ID do recurso (o arquivo CSV) de cada ano no dados.es.gov.br. O portal já
# trocou esses IDs uma vez (em 16/10/2026); se o resource_show der 404,
# procure o novo no package_show do pacote.
ID_RECURSO_POR_ANO = {
    2025: '2dc2d874-0d72-4c01-b8a0-ecb6f392d6e4',
}

# Formato do CSV: ponto e vírgula entre as colunas e UTF-8 com BOM no começo.
SEPARADOR = ';'
CODIFICACAO = 'utf-8-sig'

# As 47 colunas do arquivo, na ordem do arquivo de 2025. O arquivo não tem
# uma coluna de identificador da linha (ver receitas/uris.py).
COLUNAS = [
    'codigoUG', 'descricaoUG', 'contaContabil', 'descricaoContaContabil',
    'codigoNatureza', 'descricaoNatureza', 'codigoCategoria', 'descricaoCategoria',
    'codigoOrigem', 'descricaoOrigem', 'codigoEspecie', 'descricaoEspecie',
    'codigoDetalhamento1', 'descricaoDetalhamento1', 'codigoDetalhamento2', 'descricaoDetalhamento2',
    'codigoDetalhamento3', 'descricaoDetalhamento3', 'codigoTipo', 'descricaoTipo',
    'codigoIdUso', 'descricaoIdUso', 'codigoFonte', 'descricaoFonte',
    'codigoGrupoFonte', 'descricaoGrupoFonte', 'codigoDetalhamentoFonte',
    'codigoDetalhamentoFonteAux', 'descricaoDetalhamentoFonte', 'valorPrevista',
    'valorArrecadada', 'valorRecolhida', 'tipoLancamento', 'dataEmissao', 'dataContabilizacao',
    'documento', 'codigoUGEmitente', 'descricaoUGEmitente', 'tipo',
    'valorPrevistaBruta', 'valorPrevistaDeducao', 'valorPrevistaLiquida',
    'valorArrecadadaBruta', 'valorArrecadadaDeducao', 'valorArrecadadaLiquida',
    'valorRecolhidaBruta', 'ano',
]
