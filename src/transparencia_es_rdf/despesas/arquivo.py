"""Como é o arquivo de Despesas no portal. Não abre o arquivo: só o descreve.

O pacote no dados.es.gov.br é o
portal-da-transparencia-despesas-execucao-orcamentaria-e-financeira.
"""

# ID do recurso (o arquivo CSV) de cada ano no dados.es.gov.br. O de 2025 é o
# que o protótipo usou em 02/09 (seção 9.1 da descrição do TCC) e não foi
# conferido depois. Em 16/10 o portal trocou os recursos de Receitas, e o ID
# de Receitas mudou. Se o resource_show der 404, procure o novo no
# package_show do pacote acima.
ID_RECURSO_POR_ANO = {
    2025: 'b9c229f8-884c-4fa6-85a9-15469172d6a8',
}

# Formato do CSV: o mesmo de Receitas, com ponto e vírgula entre as colunas e
# UTF-8 com BOM no começo do arquivo.
SEPARADOR = ';'
CODIFICACAO = 'utf-8-sig'

# As 71 colunas, na ordem em que aparecem no cabeçalho do arquivo de 2025.
COLUNAS = [
    'Ano', 'Data',
    'ValorEmpenho', 'ValorLiquidado', 'ValorPago', 'ValorRap',
    'CpfCnpjNis', 'TipoFavorecido', 'CargoFuncao', 'Favorecido', 'IdFavorecido',
    'TipoLicitacao', 'HistoricoDocumento', 'Documento', 'DocumentoEmpenho',
    'CodigoProcesso', 'Processo', 'ProcessoAssunto',
    'CodigoFuncionalProgramatica',
    'CodigoCategoriaEconomica', 'CategoriaEconomica',
    'CodigoUnidadeGestora', 'UnidadeGestora',
    'CodigoGrupoDespesa', 'GrupoDespesa',
    'CodigoElementoDespesa', 'ElementoDespesa', 'DescricaoElementoDespesa',
    'CodigoSubtitulo', 'Subtitulo',
    'CodigoFonte', 'Fonte', 'CodigoDetalhamentoFonte', 'DetalhamentoFonte',
    'CodigoOrgao', 'Orgao',
    'CodigoFuncao', 'Funcao', 'CodigoSubFuncao', 'SubFuncao',
    'CodigoPrograma', 'Programa', 'CodigoAcao', 'Acao',
    'CodigoModalidade', 'Modalidade',
    'CodigoSubelementoDespesa', 'SubelementoDespesa',
    'CodigoGestaoEmitente',
    'CodigoPlanoOrcamentario', 'PlanoOrcamentario',
    'NumeroProcesso',
    'CodigoConvenioRecebido', 'CodigoConvenioConcedido',
    'Embasamento',
    'CredorRetencao', 'NomeCredorRetencao', 'TipoRetencao', 'NomeTipoRetencao',
    'NumeroLicitacao', 'AnoLicitacao',
    'BancoOrigem', 'AgenciaOrigem', 'DomicilioBancarioOrigem',
    'IdUso', 'DescricaoIdUso',
    'Emenda',
    'Esfera', 'DescricaoEsfera',
    'Contrato',
    'Id',
]