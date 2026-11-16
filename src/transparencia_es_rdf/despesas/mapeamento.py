"""O mapeamento de Despesas: de qual coluna do CSV vem cada atributo, e as
classes e relações que a ontologia usa para ligar as entidades.

É a tabela que se confere contra o mapeamento da equipe
(ontologia/mapeamentos/base-despesas/Despesas-2025.csv, commit 90c3354). Os
dicionários de atributos cobrem 68 das 71 colunas do arquivo, cada coluna uma
vez só. As outras 3 o mapeamento da equipe deixa sem destino.

Os atributos ficam na classe que os declara na ontologia. Por isso o código e
a descrição da UG e do órgão são de OrgaoPublico, e os dados do favorecido são
de DadosPessoaisAnonimizados e DadosPessoaisAnonimizadosExpandido, todos do
núcleo.
"""

from transparencia_es_rdf.nucleo import unidade_gestora
from transparencia_es_rdf.rdf.vocabularios import NAMESPACE_DESPESAS, NAMESPACE_NUCLEO, propriedade

# ---------------------------------------------------------------------------
# Classes: o tipo (rdf:type) de cada entidade.
# ---------------------------------------------------------------------------

# As que existem uma vez por linha do CSV.
CLASSE_REGISTRO = NAMESPACE_DESPESAS + 'RegistroDeDespesa'
CLASSE_DESPESA = NAMESPACE_DESPESAS + 'DespesaOrcamentariaRegistrada'
CLASSE_CLASSIFICACAO = NAMESPACE_DESPESAS + 'ClassificacaoDoRegistroDeDespesaOrcamentaria'
CLASSE_CLASSIFICADOR_INSTITUCIONAL = NAMESPACE_DESPESAS + 'ClassificadorInstitucionalDeDespesa'

# As que muitas linhas repetem.
CLASSE_VALOR = NAMESPACE_DESPESAS + 'ValorAtreladoNoRegistroDeDespesa'
CLASSE_FAVORECIDO = NAMESPACE_NUCLEO + 'DadosPessoaisAnonimizadosExpandido'
CLASSE_LICITACAO = NAMESPACE_DESPESAS + 'LicitacaoDaDespesa'
CLASSE_RETENCAO = NAMESPACE_DESPESAS + 'RetencaoDaDespesa'
CLASSE_PROCESSO = NAMESPACE_DESPESAS + 'ProcessoOrcamentarioDeDespesa'
CLASSE_UG = NAMESPACE_DESPESAS + 'UnidadeGestoraNaDespesa'
CLASSE_ORGAO = NAMESPACE_DESPESAS + 'OrgaoPublicoOrcamentarioNaDespesa'
CLASSE_FUNCIONAL = NAMESPACE_DESPESAS + 'ClassificadorFuncionalDeDespesa'
CLASSE_PROGRAMATICA = NAMESPACE_DESPESAS + 'ClassificadorPorEstruturaProgramaticaDeDespesa'
CLASSE_NATUREZA = NAMESPACE_DESPESAS + 'ClassificadorPorNaturezaDeDespesa'
CLASSE_FONTE = NAMESPACE_DESPESAS + 'FonteDaDespesa'
CLASSE_ESFERA = NAMESPACE_DESPESAS + 'EsferaOrcamentariaNaDespesa'
CLASSE_BANCO = NAMESPACE_DESPESAS + 'BancoNaDespesa'
CLASSE_CONVENIO_CONCEDIDO = NAMESPACE_DESPESAS + 'ConcedorDeConvenio'
CLASSE_CONVENIO_RECEBIDO = NAMESPACE_DESPESAS + 'RecebedorDeConvenio'

# ---------------------------------------------------------------------------
# Relações: as propriedades que ligam uma entidade a outra.
# ---------------------------------------------------------------------------

# Do registro para a despesa e a UG (declaradas em RegistroDeDespesaOrcamentaria).
RELACAO_TEM_DESPESA = propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesaOrcamentaria', 'temDespesaOrcamentaria')
RELACAO_TEM_UG = propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesaOrcamentaria', 'temUnidadeGestoraDaDespesa')

# Do registro para os seus dados (declaradas em RegistroDeDespesa).
RELACAO_TEM_VALOR = propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'valorAtrelado')
RELACAO_FAVORECIDO = propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'dadosDoFavorecido')
RELACAO_LICITACAO = propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'dadosLicitacao')
RELACAO_RETENCAO = propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'dadosRetencao')
RELACAO_PROCESSO = propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'mediatesProcessoOrcamentarioDeDespesa')
RELACAO_BANCO = propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'hasBancoNaDespesa')
RELACAO_CONVENIO_CONCEDIDO = propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'hasConcedorDeConvenio')
RELACAO_CONVENIO_RECEBIDO = propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'hasRecebedorDeConvenio')

# Da classificação para o registro e para os classificadores.
RELACAO_CLASSIFICA = propriedade(NAMESPACE_DESPESAS, 'ClassificacaoDoRegistroDeDespesaOrcamentaria', 'classifica')
RELACAO_FUNCIONAL = propriedade(NAMESPACE_DESPESAS, 'ClassificacaoDoRegistroDeDespesaOrcamentaria', 'funcionalClassificadaPor')
RELACAO_PROGRAMATICA = propriedade(NAMESPACE_DESPESAS, 'ClassificacaoDoRegistroDeDespesaOrcamentaria', 'programaticaClassificadaPor')
RELACAO_NATUREZA = propriedade(NAMESPACE_DESPESAS, 'ClassificacaoDoRegistroDeDespesaOrcamentaria', 'naturezaClassificadaPor')
RELACAO_FONTE = propriedade(NAMESPACE_DESPESAS, 'ClassificacaoDoRegistroDeDespesaOrcamentaria', 'fonteClassificadaPor')
RELACAO_ESFERA = propriedade(NAMESPACE_DESPESAS, 'ClassificacaoDoRegistroDeDespesaOrcamentaria', 'mediatesEsferaOrcamentariaNaDespesa')

# Do classificador institucional para a classificação e para o órgão.
RELACAO_INSTITUCIONAL_CLASSIFICACAO = propriedade(NAMESPACE_DESPESAS, 'ClassificadorInstitucionalDeDespesa',
                                                  'mediatesClassificacaoDoRegistroDeDespesaOrcamentaria')
RELACAO_INSTITUCIONAL_ORGAO = propriedade(NAMESPACE_DESPESAS, 'ClassificadorInstitucionalDeDespesa',
                                          'mediatesOrgaoPublicoOrcamentarioNaDespesa')

# ---------------------------------------------------------------------------
# Atributos: coluna do CSV -> propriedade que recebe o texto da coluna.
# ---------------------------------------------------------------------------

# Registro: uma linha do CSV (11 colunas). O idRegistro é declarado em
# RegistroDeDespesaOrcamentaria; os outros, em RegistroDeDespesa.
ATRIBUTOS_DO_REGISTRO = {
    'Id': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesaOrcamentaria', 'idRegistro'),
    'Data': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'data'),
    'Documento': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'documento'),
    'DocumentoEmpenho': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'documentoEmpenho'),
    'HistoricoDocumento': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'historicoDocumento'),
    'Embasamento': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'embasamento'),
    'Emenda': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'emenda'),
    'IdUso': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'idUso'),
    'DescricaoIdUso': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'descricaoIdUso'),
    'Contrato': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'contratoDaDespesa'),
    'CodigoGestaoEmitente': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesa', 'codigoGestaoEmitente'),
}

# Despesa: só o ano (1 coluna).
ATRIBUTOS_DA_DESPESA = {
    'Ano': propriedade(NAMESPACE_DESPESAS, 'DespesaOrcamentariaRegistrada', 'ano'),
}

# Valor: os quatro números da linha (4 colunas). A ordem importa: é com ela
# que se monta a URI do valor em despesas/uris.py.
COLUNAS_DOS_VALORES = ['ValorEmpenho', 'ValorLiquidado', 'ValorPago', 'ValorRap']
ATRIBUTOS_DO_VALOR = {
    'ValorEmpenho': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoRegistroDeDespesa', 'valorEmpenho'),
    'ValorLiquidado': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoRegistroDeDespesa', 'valorLiquidado'),
    'ValorPago': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoRegistroDeDespesa', 'valorPago'),
    'ValorRap': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoRegistroDeDespesa', 'valorRap'),
}

# Favorecido: quem recebeu o dinheiro (5 colunas). O codigo é o CPF, o CNPJ ou
# o NIS, com o CPF mascarado pelo portal (###.134.977-##).
ATRIBUTOS_DO_FAVORECIDO = {
    'CpfCnpjNis': propriedade(NAMESPACE_NUCLEO, 'DadosPessoaisAnonimizados', 'codigo'),
    'Favorecido': propriedade(NAMESPACE_NUCLEO, 'DadosPessoaisAnonimizados', 'nome'),
    'TipoFavorecido': propriedade(NAMESPACE_NUCLEO, 'DadosPessoaisAnonimizadosExpandido', 'tipoFavorecido'),
    'CargoFuncao': propriedade(NAMESPACE_NUCLEO, 'DadosPessoaisAnonimizadosExpandido', 'cargoFuncao'),
    'IdFavorecido': propriedade(NAMESPACE_NUCLEO, 'DadosPessoaisAnonimizadosExpandido', 'idFavorecido'),
}

# Licitação (3 colunas).
ATRIBUTOS_DA_LICITACAO = {
    'TipoLicitacao': propriedade(NAMESPACE_DESPESAS, 'LicitacaoDaDespesa', 'tipoLicitacao'),
    'NumeroLicitacao': propriedade(NAMESPACE_DESPESAS, 'LicitacaoDaDespesa', 'numeroLicitacao'),
    'AnoLicitacao': propriedade(NAMESPACE_DESPESAS, 'LicitacaoDaDespesa', 'anoLicitacao'),
}

# Retenção (4 colunas). RetencaoDaDespesa especializa DadosPessoaisAnonimizados:
# o credor da retenção é o codigo e o nome.
ATRIBUTOS_DA_RETENCAO = {
    'CredorRetencao': propriedade(NAMESPACE_NUCLEO, 'DadosPessoaisAnonimizados', 'codigo'),
    'NomeCredorRetencao': propriedade(NAMESPACE_NUCLEO, 'DadosPessoaisAnonimizados', 'nome'),
    'TipoRetencao': propriedade(NAMESPACE_DESPESAS, 'RetencaoDaDespesa', 'tipoRetencao'),
    'NomeTipoRetencao': propriedade(NAMESPACE_DESPESAS, 'RetencaoDaDespesa', 'nomeTipoRetencao'),
}

# Processo orçamentário (3 colunas).
ATRIBUTOS_DO_PROCESSO = {
    'CodigoProcesso': propriedade(NAMESPACE_DESPESAS, 'ProcessoOrcamentarioDeDespesa', 'codigo'),
    'Processo': propriedade(NAMESPACE_DESPESAS, 'ProcessoOrcamentarioDeDespesa', 'descricao'),
    'ProcessoAssunto': propriedade(NAMESPACE_DESPESAS, 'ProcessoOrcamentarioDeDespesa', 'assunto'),
}

# Unidade gestora (2 colunas). As propriedades vêm do núcleo, como em Receitas.
ATRIBUTOS_DA_UG = {
    'CodigoUnidadeGestora': unidade_gestora.PROPRIEDADE_CODIGO,
    'UnidadeGestora': unidade_gestora.PROPRIEDADE_DESCRICAO,
}

# Órgão orçamentário (2 colunas). Também é um papel de OrgaoPublico, então usa
# as mesmas duas propriedades da UG.
ATRIBUTOS_DO_ORGAO = {
    'CodigoOrgao': propriedade(NAMESPACE_NUCLEO, 'OrgaoPublico', 'codigo'),
    'Orgao': propriedade(NAMESPACE_NUCLEO, 'OrgaoPublico', 'descricao'),
}

# Classificação funcional (4 colunas).
ATRIBUTOS_DA_FUNCIONAL = {
    'CodigoFuncao': propriedade(NAMESPACE_DESPESAS, 'ClassificadorFuncionalDeDespesa', 'codigoFuncao'),
    'Funcao': propriedade(NAMESPACE_DESPESAS, 'ClassificadorFuncionalDeDespesa', 'descricaoFuncao'),
    'CodigoSubFuncao': propriedade(NAMESPACE_DESPESAS, 'ClassificadorFuncionalDeDespesa', 'codigoSubFuncao'),
    'SubFuncao': propriedade(NAMESPACE_DESPESAS, 'ClassificadorFuncionalDeDespesa', 'descricaoSubFuncao'),
}

# Classificação por estrutura programática (8 colunas).
ATRIBUTOS_DA_PROGRAMATICA = {
    'CodigoPrograma': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa', 'codigoPrograma'),
    'Programa': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa', 'descricaoPrograma'),
    'CodigoAcao': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa', 'codigoAcao'),
    'Acao': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa', 'descricaoAcao'),
    'CodigoSubtitulo': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa', 'codigoSubtitulo'),
    'Subtitulo': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa', 'descricaoSubtitulo'),
    'CodigoPlanoOrcamentario': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa',
                                           'codigoPlanoOrcamentario'),
    'PlanoOrcamentario': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa',
                                     'descricaoPlanoOrcamentario'),
}

# Classificação por natureza da despesa (10 colunas). Atenção aos nomes: a
# coluna ElementoDespesa vai para descricaoElementoDespesa, e as colunas de
# subelemento, com "e" minúsculo, vão para atributos com "E" maiúsculo.
ATRIBUTOS_DA_NATUREZA = {
    'CodigoCategoriaEconomica': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'codigoCategoriaEconomica'),
    'CategoriaEconomica': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'descricaoCategoriaEconomica'),
    'CodigoGrupoDespesa': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'codigoGrupoDespesa'),
    'GrupoDespesa': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'descricaoGrupoDespesa'),
    'CodigoModalidade': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'codigoModalidade'),
    'Modalidade': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'descricaoModalidade'),
    'CodigoElementoDespesa': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'codigoElementoDespesa'),
    'ElementoDespesa': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'descricaoElementoDespesa'),
    'CodigoSubelementoDespesa': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'codigoSubElementoDespesa'),
    'SubelementoDespesa': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'descricaoSubElementoDespesa'),
}

# Fonte de recursos (4 colunas). Os atributos são de FonteDaDespesa; a URI é a
# mesma da fonte de Receitas (nucleo/fonte.py).
ATRIBUTOS_DA_FONTE = {
    'CodigoFonte': propriedade(NAMESPACE_DESPESAS, 'FonteDaDespesa', 'codigoFonte'),
    'Fonte': propriedade(NAMESPACE_DESPESAS, 'FonteDaDespesa', 'descricaoFonte'),
    'CodigoDetalhamentoFonte': propriedade(NAMESPACE_DESPESAS, 'FonteDaDespesa', 'codigoDetalhamentoFonte'),
    'DetalhamentoFonte': propriedade(NAMESPACE_DESPESAS, 'FonteDaDespesa', 'descricaoDetalhamentoFonte'),
}

# Esfera orçamentária (2 colunas). No arquivo de 2025, a coluna Esfera só tem
# 10 e 20, e a DescricaoEsfera vem sempre vazia.
ATRIBUTOS_DA_ESFERA = {
    'Esfera': propriedade(NAMESPACE_NUCLEO, 'EsferaOrcamentaria', 'codigo'),
    'DescricaoEsfera': propriedade(NAMESPACE_NUCLEO, 'EsferaOrcamentaria', 'descricao'),
}

# Banco de origem do pagamento (3 colunas).
ATRIBUTOS_DO_BANCO = {
    'BancoOrigem': propriedade(NAMESPACE_NUCLEO, 'Banco', 'codigo'),
    'AgenciaOrigem': propriedade(NAMESPACE_NUCLEO, 'Banco', 'codigoAgenciaOrigem'),
    'DomicilioBancarioOrigem': propriedade(NAMESPACE_NUCLEO, 'Banco', 'codigoDomicilioBancarioOrigem'),
}

# Convênios (1 coluna cada). Os dois papéis são do mesmo Convenio do núcleo.
ATRIBUTOS_DO_CONVENIO_CONCEDIDO = {
    'CodigoConvenioConcedido': propriedade(NAMESPACE_NUCLEO, 'Convenio', 'codigo'),
}
ATRIBUTOS_DO_CONVENIO_RECEBIDO = {
    'CodigoConvenioRecebido': propriedade(NAMESPACE_NUCLEO, 'Convenio', 'codigo'),
}

# As 3 colunas que o mapeamento da equipe deixa sem destino. No arquivo de
# 2025, a primeira é sempre "0" e as outras duas vêm sempre vazias.
COLUNAS_SEM_MAPEAMENTO = ['CodigoFuncionalProgramatica', 'DescricaoElementoDespesa', 'NumeroProcesso']

# Coluna cujo texto vira data e hora (xsd:dateTime), como a ontologia pede.
COLUNAS_DE_DATA_E_HORA = {'Data'}