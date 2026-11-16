# transparencia-es-rdf

Coverte as bases de Receitas e Despesas do Portal de Dados Abertos do Espírito Santo ([dados.es.gov.br](https://dados.es.gov.br)) para RDF.

Versão 0.1.0: cabecalho de metadados, Receitas e Despesas, com os arquivos de 2025. Em Despesas, os quatro arquivos que a ontologia descreve: Despesas, Restos a Pagar (o de 2024), Orçamentos de Despesa e Orçamentos de Execuções

## Contexto

Essa ferramenta é parte do Trabalho de Conclução de Conclusão de Curso *Elevando a Maturidade de Dados Abertos: Conversão para RDF das Bases do Portal da Transparência do Espírito Santo*, de Miguel Gewehr de Oliveira, no curso de Ciência da Computação da UFES.

O trabalho faz parte do projeto *Melhoria da Maturidade das Bases de Dados Abertos do Portal da Transparência do Poder Executivo Estadual*, do Núcleo de Estudos em Modelagem Conceitual e Ontologias (NEMO) da UFES, em parceria com a Secretaria de Estado de Controle e Transparência (SECONT). No projeto, a equipe de modelagem descreve cada base do portal numa ontologia, mantida no repositório [secont-ontologias](https://github.com/Renzo-Henrique/secont-ontologias). O portal publica os dados em CSV. Esta ferramenta escreve os mesmos dados em RDF, com os termos dessa ontologia, e liga as duas bases.

## O que a ferramenta gera

Para cada base, dois arquivos na pasta `saida/`:

As duas bases se ligam pela unidade gestora (UG) e pela fonte de recursos, que recebem a mesma URI em Receitas e em Despesas. Para isso, as URIs são montadas a partir dos mesmos códigos:

- a UG, pelo código de 6 dígitos. Despesas escreve sem o zero da frente o código das UGs dos órgãos 1 a 9 (`10101` em vez de `010101`), e a ferramenta completa o zero;
- a fonte, pelo código detalhado (`codigoDetalhamentoFonteAux` em Receitas e `CodigoDetalhamentoFonte` em Despesas), que tem o mesmo formato nas duas bases.

Nos arquivos de 2025, 115 UGs e 190 fontes aparecem nas duas bases. Nas amostras, por exemplo, a fonte `500.100200` aparece em Receitas e em Despesas com a mesma URI.

## Instalação

É preciso ter o Python 3.11 ou mais novo. Na pasta do repositório:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

O `pip` instala as dependências que estão no [`pyproject.toml`](pyproject.toml) (rdflib e requests) e cria o comando `transparencia-es-rdf`. Nas próximas vezes, basta ativar o ambiente com `source .venv/bin/activate`.

## Uso

Os comandos rodam na pasta do repositório, com o ambiente ativado.

## A ontologia

A pasta [`ontologia/`](ontologia) guarda uma cópia dos arquivos do [secont-ontologias](https://github.com/Renzo-Henrique/secont-ontologias) no commit `e0fff39`, de 16 de novembro de 2026:

| Pasta | O que tem |
|---|---|
| `out/ttl/` | a ontologia em OWL: `base-receitas.ttl`, `base-despesas.ttl` e `nucleo.ttl` |
| `src/` | o modelo em Tonto, do qual os `.ttl` são gerados |
| `mapeamentos/` | as tabelas da equipe que dizem a qual atributo vai cada coluna do CSV |
| `out/diagramas/` | os diagramas das classes |

O código não lê esses arquivos. Eles ficam aqui para registrar com qual versão da ontologia as triplas foram geradas. Os nomes das classes e das propriedades estão escritos no `mapeamento.py` de cada base e nos arquivos do `nucleo/`, do mesmo jeito que nos `.ttl`.

