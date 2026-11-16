"""O mapeamento de Despesas: de qual coluna do CSV vem cada atributo, e as
classes e relações que a ontologia usa para ligar as entidades.

É a tabela que se confere contra o mapeamento da equipe, que tem um arquivo
para cada arquivo do portal (ontologia/mapeamentos/base-despesas/, commit
e0fff39). A primeira parte é a do arquivo Despesas; as outras três, a dos
arquivos RestosAPagar, OrcamentosDespesa e OrcamentosExecucoes, reaproveitam
as classes e os atributos da primeira quando as colunas são as mesmas.

No arquivo Despesas, os dicionários de atributos cobrem 68 das 71 colunas,
cada coluna uma vez só. As outras 3 o mapeamento da equipe deixa sem destino.

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

# Coluna cujo texto vira data e hora (xsd:dateTime), como a ontologia pede. É
# a mesma nos arquivos Despesas e OrcamentosExecucoes; os outros dois não têm data.
COLUNAS_DE_DATA_E_HORA = {'Data'}


# ===========================================================================
# RestosAPagar (13 colunas)
# ===========================================================================
#
# A ontologia liga o registro de restos a pagar ao valor e ao poder. O
# registro também é um RegistroDeDespesaOrcamentaria, então tem a despesa e a
# UG; e a classificação, que classifica qualquer registro, o liga à natureza.
# CpfCnpjNis e Favorecido ficam de fora: o mapeamento da equipe os põe em
# DadosPessoaisAnonimizados, mas a ontologia não tem uma relação que ligue o
# registro de restos a pagar a eles (a dadosDoFavorecido é só de
# RegistroDeDespesa e de RegistroDeOrcamentoDeDespesa).

CLASSE_REGISTRO_RESTOS_A_PAGAR = NAMESPACE_DESPESAS + 'RegistroDeRestosAPagar'
CLASSE_VALOR_RESTOS_A_PAGAR = NAMESPACE_DESPESAS + 'ValorAtreladoNoRegistroRestosAPagar'
CLASSE_PODER = NAMESPACE_DESPESAS + 'PoderDaFederacaoNaDespesa'

RELACAO_RESTOS_A_PAGAR_VALOR = propriedade(NAMESPACE_DESPESAS, 'RegistroDeRestosAPagar', 'valorAtrelado')
RELACAO_RESTOS_A_PAGAR_PODER = propriedade(NAMESPACE_DESPESAS, 'RegistroDeRestosAPagar',
                                           'mediatesPoderDaFederacaoNaDespesa')

# Registro (1 coluna). RegistroDeRestosAPagar declara o seu próprio idRegistro.
ATRIBUTOS_DO_REGISTRO_RESTOS_A_PAGAR = {
    'Id': propriedade(NAMESPACE_DESPESAS, 'RegistroDeRestosAPagar', 'idRegistro'),
}

# Valor (3 colunas). A ordem é a da URI do valor.
ATRIBUTOS_DO_VALOR_RESTOS_A_PAGAR = {
    'ValorNaoProcessado': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoRegistroRestosAPagar', 'valorNaoProcessado'),
    'ValorProcessado': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoRegistroRestosAPagar', 'valorProcessado'),
    'ValorNaoProcessadoLiquidado': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoRegistroRestosAPagar',
                                               'valorNaoProcessadoLiquidado'),
}

# Poder (2 colunas). Os atributos são de PoderDaFederacao, no núcleo.
ATRIBUTOS_DO_PODER = {
    'CodigoPoder': propriedade(NAMESPACE_NUCLEO, 'PoderDaFederacao', 'codigo'),
    'Poder': propriedade(NAMESPACE_NUCLEO, 'PoderDaFederacao', 'descricao'),
}

# Natureza (2 colunas). O código vem com 6 dígitos ('339039'), e não com os 2
# do elemento, como em Despesas ('39'). Ele vai como está para o
# codigoElementoDespesa, como o mapeamento da equipe pede.
ATRIBUTOS_DA_NATUREZA_RESTOS_A_PAGAR = {
    'CodigoElemento': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'codigoElementoDespesa'),
    'Elemento': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorNaturezaDeDespesa', 'descricaoElementoDespesa'),
}

# Ano (1) e UG (2): ATRIBUTOS_DA_DESPESA e ATRIBUTOS_DA_UG, da primeira parte.

COLUNAS_SEM_MAPEAMENTO_RESTOS_A_PAGAR = ['CpfCnpjNis', 'Favorecido']


# ===========================================================================
# OrcamentosDespesa (42 colunas)
# ===========================================================================
#
# O registro do orçamento liga-se ao valor, ao favorecido, à microrregião e
# ao município. A classificação usa os mesmos classificadores de Despesas, e
# o classificador institucional liga a classificação à unidade orçamentária
# (este arquivo não tem a coluna do órgão).

CLASSE_REGISTRO_ORCAMENTO_DESPESA = NAMESPACE_DESPESAS + 'RegistroDeOrcamentoDeDespesa'
CLASSE_VALOR_ORCAMENTO_DESPESA = NAMESPACE_DESPESAS + 'ValorAtreladoNoOrcamentoDeDespesa'
CLASSE_FAVORECIDO_DO_ORCAMENTO = NAMESPACE_NUCLEO + 'DadosPessoaisAnonimizados'
CLASSE_UNIDADE_ORCAMENTARIA = NAMESPACE_DESPESAS + 'UnidadeOrcamentariaNaDespesa'
CLASSE_MICRORREGIAO = NAMESPACE_DESPESAS + 'MicroRegiaoNaDespesa'
CLASSE_MUNICIPIO = NAMESPACE_DESPESAS + 'MunicipioNaDespesa'

RELACAO_ORCAMENTO_VALOR = propriedade(NAMESPACE_DESPESAS, 'RegistroDeOrcamentoDeDespesa', 'valorAtrelado')
RELACAO_ORCAMENTO_FAVORECIDO = propriedade(NAMESPACE_DESPESAS, 'RegistroDeOrcamentoDeDespesa', 'dadosDoFavorecido')
RELACAO_ORCAMENTO_MICRORREGIAO = propriedade(NAMESPACE_DESPESAS, 'RegistroDeOrcamentoDeDespesa',
                                             'mediatesMicroRegiaoNaDespesa')
RELACAO_ORCAMENTO_MUNICIPIO = propriedade(NAMESPACE_DESPESAS, 'RegistroDeOrcamentoDeDespesa',
                                          'mediatesMunicipioNaDespesa')
RELACAO_INSTITUCIONAL_UNIDADE_ORCAMENTARIA = propriedade(NAMESPACE_DESPESAS, 'ClassificadorInstitucionalDeDespesa',
                                                         'mediatesUnidadeOrcamentariaNaDespesa')

# Registro (2 colunas). O mapeamento da equipe põe o Id em
# RegistroDeOrcamentoDeDespesa.idRegistro, que a ontologia não declara; o
# idRegistro é o de RegistroDeDespesaOrcamentaria, como em Despesas.
ATRIBUTOS_DO_REGISTRO_ORCAMENTO_DESPESA = {
    'Id': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesaOrcamentaria', 'idRegistro'),
    'Emenda': propriedade(NAMESPACE_DESPESAS, 'RegistroDeOrcamentoDeDespesa', 'emenda'),
}

# Valor (5 colunas). A ordem é a da URI do valor.
ATRIBUTOS_DO_VALOR_ORCAMENTO_DESPESA = {
    'DotacaoInicial': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoOrcamentoDeDespesa', 'dotacaoInicial'),
    'DotacaoAtualizada': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoOrcamentoDeDespesa', 'dotacaoAtualizada'),
    'DespesaEmpenhada': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoOrcamentoDeDespesa', 'despesaEmpenhada'),
    'DespesaLiquidada': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoOrcamentoDeDespesa', 'despesaLiquidada'),
    'DespesaPaga': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoOrcamentoDeDespesa', 'despesaPaga'),
}

# Favorecido (2 colunas). Aqui o favorecido é só DadosPessoaisAnonimizados,
# sem os atributos de DadosPessoaisAnonimizadosExpandido.
ATRIBUTOS_DO_FAVORECIDO_DO_ORCAMENTO = {
    'CpfCnpjNis': propriedade(NAMESPACE_NUCLEO, 'DadosPessoaisAnonimizados', 'codigo'),
    'Favorecido': propriedade(NAMESPACE_NUCLEO, 'DadosPessoaisAnonimizados', 'nome'),
}

# Classificação por estrutura programática (6 colunas): as de Despesas, com o
# plano orçamentário no lugar do subtítulo.
ATRIBUTOS_DA_PROGRAMATICA_DO_ORCAMENTO = {
    'CodigoPrograma': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa', 'codigoPrograma'),
    'Programa': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa', 'descricaoPrograma'),
    'CodigoAcao': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa', 'codigoAcao'),
    'Acao': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa', 'descricaoAcao'),
    'CodigoPlanoOrcamentario': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa',
                                           'codigoPlanoOrcamentario'),
    'PlanoOrcamentario': propriedade(NAMESPACE_DESPESAS, 'ClassificadorPorEstruturaProgramaticaDeDespesa',
                                     'descricaoPlanoOrcamentario'),
}

# Fonte (2 colunas): só o código e a descrição da fonte, sem o detalhamento.
ATRIBUTOS_DA_FONTE_DO_ORCAMENTO = {
    'CodigoFonte': propriedade(NAMESPACE_DESPESAS, 'FonteDaDespesa', 'codigoFonte'),
    'Fonte': propriedade(NAMESPACE_DESPESAS, 'FonteDaDespesa', 'descricaoFonte'),
}

# Esfera (2 colunas). Aqui a descrição vem preenchida, na coluna NomeEsfera.
ATRIBUTOS_DA_ESFERA_DO_ORCAMENTO = {
    'Esfera': propriedade(NAMESPACE_NUCLEO, 'EsferaOrcamentaria', 'codigo'),
    'NomeEsfera': propriedade(NAMESPACE_NUCLEO, 'EsferaOrcamentaria', 'descricao'),
}

# Unidade orçamentária (2 colunas). UnidadeOrcamentaria especializa
# UnidadeDeOrgaoPublico, que declara o codigo e a descricao.
ATRIBUTOS_DA_UNIDADE_ORCAMENTARIA = {
    'UnidadeOrcamentaria': propriedade(NAMESPACE_NUCLEO, 'UnidadeDeOrgaoPublico', 'codigo'),
    'NomeUnidadeOrcamentaria': propriedade(NAMESPACE_NUCLEO, 'UnidadeDeOrgaoPublico', 'descricao'),
}

# Microrregião e município (2 colunas cada).
ATRIBUTOS_DA_MICRORREGIAO = {
    'Microregiao': propriedade(NAMESPACE_NUCLEO, 'MicroRegiao', 'codigo'),
    'NomeMicroregiao': propriedade(NAMESPACE_NUCLEO, 'MicroRegiao', 'nome'),
}
ATRIBUTOS_DO_MUNICIPIO = {
    'Municipio': propriedade(NAMESPACE_NUCLEO, 'Municipio', 'codigo'),
    'NomeMunicipio': propriedade(NAMESPACE_NUCLEO, 'Municipio', 'nome'),
}

# Ano (1), UG (2), funcional (4) e natureza (10): os dicionários da primeira
# parte, porque as colunas têm os mesmos nomes.


# ===========================================================================
# OrcamentosExecucoes (11 colunas)
# ===========================================================================
#
# O registro da execução do orçamento liga-se só ao valor, além da despesa e
# da UG. O arquivo não tem classificadores, nem a coluna Ano: o ano da despesa
# sai da coluna Data (conversor_orcamentos_execucoes.py).

CLASSE_REGISTRO_ORCAMENTO_EXECUCAO = NAMESPACE_DESPESAS + 'RegistroDeOrcamentoDeExecucao'
CLASSE_VALOR_ORCAMENTO_EXECUCAO = NAMESPACE_DESPESAS + 'ValorAtreladoNoOrcamentoDeExecucaoDeDespesa'

RELACAO_EXECUCAO_VALOR = propriedade(NAMESPACE_DESPESAS, 'RegistroDeOrcamentoDeExecucao', 'valorAtrelado')

# Registro (2 colunas). O mapeamento da equipe escreve RegistroDeOrcamentoDeExecucoes,
# no plural; na ontologia a classe é RegistroDeOrcamentoDeExecucao.
ATRIBUTOS_DO_REGISTRO_ORCAMENTO_EXECUCAO = {
    'Id': propriedade(NAMESPACE_DESPESAS, 'RegistroDeDespesaOrcamentaria', 'idRegistro'),
    'Data': propriedade(NAMESPACE_DESPESAS, 'RegistroDeOrcamentoDeExecucao', 'data'),
}

# Valor (6 colunas). A ordem é a da URI do valor.
ATRIBUTOS_DO_VALOR_ORCAMENTO_EXECUCAO = {
    'ValorEmpenho': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoOrcamentoDeExecucaoDeDespesa', 'valorEmpenho'),
    'ValorLiquidado': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoOrcamentoDeExecucaoDeDespesa', 'valorLiquidado'),
    'ValorPago': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoOrcamentoDeExecucaoDeDespesa', 'valorPago'),
    'ValorRap': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoOrcamentoDeExecucaoDeDespesa', 'valorRap'),
    'ValorOrcadoInicial': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoOrcamentoDeExecucaoDeDespesa',
                                      'valorOrcadoInicial'),
    'ValorOrcado': propriedade(NAMESPACE_DESPESAS, 'ValorAtreladoNoOrcamentoDeExecucaoDeDespesa', 'valorOrcado'),
}

# UG (3 colunas): as duas de Despesas mais a sigla, que o núcleo declara em
# OrgaoPublico, como o código e a descrição.
ATRIBUTOS_DA_UG_COM_SIGLA = {
    'CodigoUnidadeGestora': unidade_gestora.PROPRIEDADE_CODIGO,
    'UnidadeGestora': unidade_gestora.PROPRIEDADE_DESCRICAO,
    'SiglaUnidadeGestora': propriedade(NAMESPACE_NUCLEO, 'OrgaoPublico', 'sigla'),
}
