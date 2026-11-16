"""Como são os arquivos de Despesas no portal. Não abre os arquivos: só os descreve.

O pacote no dados.es.gov.br é o
portal-da-transparencia-despesas-execucao-orcamentaria-e-financeira. A
ontologia de Despesas descreve quatro arquivos dele, cada um com o seu tipo
de registro:

    Despesas              -> RegistroDeDespesa
    RestosAPagar          -> RegistroDeRestosAPagar
    OrcamentosDespesa     -> RegistroDeOrcamentoDeDespesa
    OrcamentosExecucoes   -> RegistroDeOrcamentoDeExecucao

Os quatro têm o mesmo formato e colunas diferentes, então o cabeçalho basta
para saber de qual arquivo se trata (identificar_arquivo, no fim deste arquivo).
"""

# ID do recurso (o arquivo CSV) de cada ano no dados.es.gov.br. O de 2025 é o
# que o protótipo usou em 02/09 (seção 9.1 da descrição do TCC) e não foi
# conferido depois. Em 16/10 o portal trocou os recursos de Receitas, e o ID
# de Receitas mudou. Se o resource_show der 404, procure o novo no
# package_show do pacote acima.
ID_RECURSO_POR_ANO = {
    2025: 'b9c229f8-884c-4fa6-85a9-15469172d6a8',
}

# Formato do CSV, o mesmo nos quatro arquivos e em Receitas: ponto e vírgula
# entre as colunas e UTF-8 com BOM no começo do arquivo.
SEPARADOR = ';'
CODIFICACAO = 'utf-8-sig'

# As 71 colunas do arquivo Despesas, na ordem em que aparecem no cabeçalho do
# arquivo de 2025.
COLUNAS_DESPESAS = [
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

# As 13 colunas do arquivo RestosAPagar, na ordem do arquivo de 2024. Restos a
# pagar são as despesas empenhadas e não pagas até 31 de dezembro (MCASP,
# seção 4.7, citado na ontologia).
COLUNAS_RESTOS_A_PAGAR = [
    'Ano',
    'CodigoPoder', 'Poder',
    'CodigoUnidadeGestora', 'UnidadeGestora',
    'CodigoElemento', 'Elemento',
    'CpfCnpjNis', 'Favorecido',
    'ValorNaoProcessado', 'ValorProcessado', 'ValorNaoProcessadoLiquidado',
    'Id',
]

# As 42 colunas do arquivo OrcamentosDespesa, na ordem do arquivo de 2025.
COLUNAS_ORCAMENTOS_DESPESA = [
    'CodigoUnidadeGestora', 'UnidadeGestora',
    'CodigoPrograma', 'Programa', 'CodigoAcao', 'Acao',
    'CodigoFuncao', 'Funcao', 'CodigoSubFuncao', 'SubFuncao',
    'CodigoCategoriaEconomica', 'CategoriaEconomica',
    'CodigoGrupoDespesa', 'GrupoDespesa',
    'CodigoModalidade', 'Modalidade',
    'CodigoElementoDespesa', 'ElementoDespesa',
    'CodigoSubelementoDespesa', 'SubelementoDespesa',
    'CodigoFonte', 'Fonte',
    'CpfCnpjNis', 'Favorecido',
    'CodigoPlanoOrcamentario', 'PlanoOrcamentario',
    'DotacaoInicial', 'DotacaoAtualizada', 'DespesaEmpenhada', 'DespesaLiquidada', 'DespesaPaga',
    'Ano',
    'Esfera', 'NomeEsfera',
    'UnidadeOrcamentaria', 'NomeUnidadeOrcamentaria',
    'Microregiao', 'NomeMicroregiao',
    'Municipio', 'NomeMunicipio',
    'Emenda',
    'Id',
]

# As 11 colunas do arquivo OrcamentosExecucoes, na ordem do arquivo de 2025.
# É o único dos quatro sem a coluna Ano.
COLUNAS_ORCAMENTOS_EXECUCOES = [
    'Data',
    'ValorEmpenho', 'ValorLiquidado', 'ValorPago', 'ValorRap', 'ValorOrcadoInicial', 'ValorOrcado',
    'CodigoUnidadeGestora', 'UnidadeGestora', 'SiglaUnidadeGestora',
    'Id',
]

# O nome curto de cada arquivo, que também vai nas URIs das entidades que
# existem uma vez por linha (despesas/uris.py), e as suas colunas.
COLUNAS_POR_ARQUIVO = {
    'despesas': COLUNAS_DESPESAS,
    'restos-a-pagar': COLUNAS_RESTOS_A_PAGAR,
    'orcamentos-despesa': COLUNAS_ORCAMENTOS_DESPESA,
    'orcamentos-execucoes': COLUNAS_ORCAMENTOS_EXECUCOES,
}


def identificar_arquivo(cabecalho: list[str]) -> str:
    """Qual dos quatro arquivos tem este cabeçalho: 'despesas', 'restos-a-pagar'...

    Compara o conjunto das colunas, sem olhar a ordem, do mesmo jeito que a
    leitura confere o cabeçalho (portal/leitura.py). Se nenhum dos quatro
    bater, para com um erro em vez de adivinhar.
    """
    for nome_do_arquivo, colunas in COLUNAS_POR_ARQUIVO.items():
        if set(cabecalho) == set(colunas):
            return nome_do_arquivo
    raise ValueError(f'O cabeçalho não é de nenhum dos quatro arquivos de Despesas: {cabecalho}')
