"""O mapeamento de Receitas: de qual coluna do CSV vem cada atributo, e as
classes e relações que a ontologia usa para ligar as entidades.

É a tabela que se confere contra o mapeamento da equipe
(ontologia/mapeamentos/base-receitas/Receitas-2025.csv). O nome de cada
atributo é o da própria coluna: a coluna documento vira
ReceitaOrcamentariaRegistrada.documento. As exceções são a conta contábil e
as UGs, cujos atributos se chamam codigo e descricao (os da UG são os de
OrgaoPublico, no núcleo; ver nucleo/unidade_gestora.py).
"""

from transparencia_es_rdf.nucleo import unidade_gestora
from transparencia_es_rdf.rdf.vocabularios import NAMESPACE_RECEITAS, propriedade

# ---------------------------------------------------------------------------
# Classes: o tipo (rdf:type) de cada entidade.
# ---------------------------------------------------------------------------

CLASSE_RECEITA = NAMESPACE_RECEITAS + 'ReceitaOrcamentariaRegistrada'
CLASSE_REGISTRO = NAMESPACE_RECEITAS + 'RegistroDeReceitaOrcamentaria'
CLASSE_CLASSIFICACAO = NAMESPACE_RECEITAS + 'ClassificacaoDoRegistroDeReceitaOrcamentaria'
CLASSE_VALOR = NAMESPACE_RECEITAS + 'ValorAtreladoNaReceita'
CLASSE_NATUREZA = NAMESPACE_RECEITAS + 'NaturezaDaReceita'
CLASSE_FONTE = NAMESPACE_RECEITAS + 'FonteDaReceita'
CLASSE_CONTA = NAMESPACE_RECEITAS + 'ContaContabil'
CLASSE_UG_EMITENTE = NAMESPACE_RECEITAS + 'UnidadeGestoraEmitenteDeReceita'
CLASSE_UG_BENEFICIADA = NAMESPACE_RECEITAS + 'UnidadeGestoraBeneficiadaDeReceita'

# ---------------------------------------------------------------------------
# Relações: as propriedades que ligam uma entidade a outra.
# ---------------------------------------------------------------------------

RELACAO_TEM_RECEITA = propriedade(NAMESPACE_RECEITAS, 'RegistroDeReceitaOrcamentaria', 'temReceitaOrcamentaria')
RELACAO_TEM_UG_EMITENTE = propriedade(NAMESPACE_RECEITAS, 'RegistroDeReceitaOrcamentaria', 'temUnidadeGestoraEmitenteDeReceita')
RELACAO_TEM_UG_BENEFICIADA = propriedade(NAMESPACE_RECEITAS, 'RegistroDeReceitaOrcamentaria', 'temUnidadeGestoraBeneficiadaDeReceita')
RELACAO_TEM_VALOR = propriedade(NAMESPACE_RECEITAS, 'RegistroDeReceitaOrcamentaria', 'valorAtreladoNaReceita')
RELACAO_CLASSIFICA = propriedade(NAMESPACE_RECEITAS, 'ClassificacaoDoRegistroDeReceitaOrcamentaria', 'classifica')
RELACAO_NATUREZA = propriedade(NAMESPACE_RECEITAS, 'ClassificacaoDoRegistroDeReceitaOrcamentaria', 'naturezaClassificadaPor')
RELACAO_FONTE = propriedade(NAMESPACE_RECEITAS, 'ClassificacaoDoRegistroDeReceitaOrcamentaria', 'fonteClassificadaPor')
RELACAO_CONTA = propriedade(NAMESPACE_RECEITAS, 'ClassificacaoDoRegistroDeReceitaOrcamentaria', 'contabilClassificadaPor')

# ---------------------------------------------------------------------------
# Atributos: coluna do CSV -> propriedade do atributo.
# ---------------------------------------------------------------------------

ATRIBUTOS_DA_RECEITA = {
    coluna: propriedade(NAMESPACE_RECEITAS, 'ReceitaOrcamentariaRegistrada', coluna)
    for coluna in ['documento', 'dataEmissao', 'ano']
}

ATRIBUTOS_DO_REGISTRO = {
    coluna: propriedade(NAMESPACE_RECEITAS, 'RegistroDeReceitaOrcamentaria', coluna)
    for coluna in ['codigoIdUso', 'descricaoIdUso', 'tipoLancamento', 'dataContabilizacao', 'tipo']
}

COLUNAS_DOS_VALORES = [
    'valorPrevista', 'valorArrecadada', 'valorRecolhida',
    'valorPrevistaBruta', 'valorPrevistaDeducao', 'valorPrevistaLiquida',
    'valorArrecadadaBruta', 'valorArrecadadaDeducao', 'valorArrecadadaLiquida',
    'valorRecolhidaBruta',
]

ATRIBUTOS_DO_VALOR = {
    coluna: propriedade(NAMESPACE_RECEITAS, 'ValorAtreladoNaReceita', coluna)
    for coluna in COLUNAS_DOS_VALORES
}

ATRIBUTOS_DA_NATUREZA = {
    coluna: propriedade(NAMESPACE_RECEITAS, 'NaturezaDaReceita', coluna)
    for coluna in [
        'codigoNatureza', 'descricaoNatureza',
        'codigoCategoria', 'descricaoCategoria',
        'codigoOrigem', 'descricaoOrigem',
        'codigoEspecie', 'descricaoEspecie',
        'codigoDetalhamento1', 'descricaoDetalhamento1',
        'codigoDetalhamento2', 'descricaoDetalhamento2',
        'codigoDetalhamento3', 'descricaoDetalhamento3',
        'codigoTipo', 'descricaoTipo',
    ]
}

ATRIBUTOS_DA_FONTE = {
    coluna: propriedade(NAMESPACE_RECEITAS, 'FonteDaReceita', coluna)
    for coluna in [
        'codigoFonte', 'descricaoFonte',
        'codigoGrupoFonte', 'descricaoGrupoFonte',
        'codigoDetalhamentoFonte', 'codigoDetalhamentoFonteAux', 'descricaoDetalhamentoFonte',
    ]
}

ATRIBUTOS_DA_CONTA = {
    'contaContabil': propriedade(NAMESPACE_RECEITAS, 'ContaContabil', 'codigo'),
    'descricaoContaContabil': propriedade(NAMESPACE_RECEITAS, 'ContaContabil', 'descricao'),
}

ATRIBUTOS_DA_UG_EMITENTE = {
    'codigoUGEmitente': unidade_gestora.PROPRIEDADE_CODIGO,
    'descricaoUGEmitente': unidade_gestora.PROPRIEDADE_DESCRICAO,
}

ATRIBUTOS_DA_UG_BENEFICIADA = {
    'codigoUG': unidade_gestora.PROPRIEDADE_CODIGO,
    'descricaoUG': unidade_gestora.PROPRIEDADE_DESCRICAO,
}

# As colunas que viram xsd:dateTime; as outras viram texto.
COLUNAS_DE_DATA_E_HORA = {'dataEmissao', 'dataContabilizacao'}
