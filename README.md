# transparencia-es-rdf

Converte as bases de Receitas e de Despesas do Portal de Dados Abertos do Espírito Santo ([dados.es.gov.br](https://dados.es.gov.br)) para RDF, com as classes e as propriedades da ontologia do projeto, valida o resultado com SHACL e consulta os dados com SPARQL.

Versão 0.1.0: conversão, validação e consultas SPARQL de Receitas (arquivo de 2025) e dos quatro arquivos de Despesas que a ontologia descreve: Despesas (2025), Restos a Pagar (2024), Orçamentos de Despesa (2025) e Orçamentos de Execuções (2025).

A ferramenta trabalha só com os CSVs já baixados e não consulta a internet. A versão que também gera um cabeçalho de metadados de proveniência, consultando a API do portal, está na branch [`com-metadados`](../../tree/com-metadados).

## Contexto

Esta ferramenta é a parte prática do Trabalho de Conclusão de Curso *Elevando a Maturidade de Dados Abertos: Conversão para RDF das Bases do Portal da Transparência do Espírito Santo*, de Miguel Gewehr de Oliveira, no curso de Ciência da Computação da UFES.

O trabalho faz parte do projeto *Melhoria da Maturidade das Bases de Dados Abertos do Portal da Transparência do Poder Executivo Estadual*, do Núcleo de Estudos em Modelagem Conceitual e Ontologias (NEMO) da UFES, em parceria com a Secretaria de Estado de Controle e Transparência (SECONT). No projeto, a equipe de modelagem descreve cada base do portal numa ontologia, mantida no repositório [secont-ontologias](https://github.com/Renzo-Henrique/secont-ontologias). O portal publica os dados em CSV. Esta ferramenta escreve os mesmos dados em RDF, com os termos dessa ontologia, e liga as duas bases.

## O que a ferramenta faz

| Comando | O que faz | Onde grava |
|---|---|---|
| `converter` | lê um CSV do portal e escreve as triplas em N-Triples, uma por linha | no caminho que você der (sugestão: `saida/rdf/`) |
| `turtle` | regrava um N-Triples pequeno, como uma amostra, em Turtle, para leitura | no caminho que você der |
| `formas` | gera as formas SHACL de uma base a partir da ontologia, para leitura | `saida/formas/` |
| `validar` | converte um CSV em lotes e valida cada lote com as formas SHACL | `saida/validacao/` |
| `carregar` | carrega arquivos N-Triples num banco de triplas em disco | `saida/banco/` |
| `consultar` | roda consultas SPARQL no banco e grava o resultado em CSV | `saida/consultas/` |

As duas bases se ligam pela unidade gestora (UG) e pela fonte de recursos, que recebem a mesma URI em Receitas e em Despesas. Para isso, as URIs são montadas a partir dos mesmos códigos:

- a UG, pelo código de 6 dígitos. Despesas escreve sem o zero da frente o código das UGs dos órgãos 1 a 9 (`10101` em vez de `010101`), e a ferramenta completa o zero;
- a fonte, pelo código detalhado (`codigoDetalhamentoFonteAux` em Receitas e `CodigoDetalhamentoFonte` em Despesas), que tem o mesmo formato nas duas bases.

Nos arquivos de 2025, 190 fontes aparecem nas duas bases. Das 121 UGs de Receitas, 115 aparecem no arquivo Despesas e as 121 aparecem em algum dos quatro arquivos de Despesas. Nas amostras, por exemplo, a fonte `500.100200` aparece em Receitas e em Despesas com a mesma URI.

Os quatro arquivos de Despesas também se ligam entre si: uma entidade com a mesma URI em dois arquivos é a mesma entidade no grafo. A UG se liga nos quatro, e a esfera e os classificadores funcional e por natureza ligam Orçamentos de Despesa a Despesas.

Um trecho da saída da amostra de Receitas, com um registro e a UG que o emitiu, em Turtle:

```turtle
@prefix nucleo: <https://example.org/ontologia-portal-transparencia-es/nucleo#> .
@prefix rec: <https://example.org/ontologia-portal-transparencia-es/base-receitas#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://localhost:8000/id/receitas/2025/registro/1> a rec:RegistroDeReceitaOrcamentaria ;
    rec:RegistroDeReceitaOrcamentaria.codigoIdUso "1" ;
    rec:RegistroDeReceitaOrcamentaria.dataContabilizacao "2025-12-30T02:12:14"^^xsd:dateTime ;
    rec:RegistroDeReceitaOrcamentaria.descricaoIdUso "RECURSOS DO EXERCÍCIO CORRENTE" ;
    rec:RegistroDeReceitaOrcamentaria.temReceitaOrcamentaria <http://localhost:8000/id/receitas/2025/receita/800102-2025GR07548> ;
    rec:RegistroDeReceitaOrcamentaria.temUnidadeGestoraBeneficiadaDeReceita <http://localhost:8000/id/unidade-gestora/800102> ;
    rec:RegistroDeReceitaOrcamentaria.temUnidadeGestoraEmitenteDeReceita <http://localhost:8000/id/unidade-gestora/800102> ;
    rec:RegistroDeReceitaOrcamentaria.tipo "ARRECADADA-LIQUIDA" ;
    rec:RegistroDeReceitaOrcamentaria.tipoLancamento "C" ;
    rec:RegistroDeReceitaOrcamentaria.valorAtreladoNaReceita <http://localhost:8000/id/receitas/2025/valor/1> .

<http://localhost:8000/id/unidade-gestora/800102> a rec:UnidadeGestoraBeneficiadaDeReceita,
        rec:UnidadeGestoraEmitenteDeReceita ;
    nucleo:OrgaoPublico.codigo "800102" ;
    nucleo:OrgaoPublico.descricao "ADMINISTRAÇÃO GERAL A CARGO DA SEFAZ",
        "ENCARGOS GERAIS - SEFAZ" .
```

## Instalação

É preciso ter o Python 3.11 ou mais novo. Na pasta do repositório:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

O `pip` instala as dependências que estão no [`pyproject.toml`](pyproject.toml) (rdflib, pySHACL e pyoxigraph) e cria o comando `transparencia-es-rdf`. Nas próximas vezes, basta ativar o ambiente com `source .venv/bin/activate`.

## Uso

Os comandos rodam na pasta do repositório, com o ambiente ativado. `transparencia-es-rdf --help` lista os comandos, e `transparencia-es-rdf <comando> --help` explica cada um.

### Converter as amostras

As amostras estão no repositório, em [`dados/`](dados): o cabeçalho e as primeiras 1.000 linhas de Receitas 2025, Despesas 2025, Restos a Pagar 2024 e Orçamentos de Despesa 2025, e o arquivo inteiro de Orçamentos de Execuções 2025, que tem 125 linhas.

```
transparencia-es-rdf converter receitas dados/receitas/amostra/amostra-receitas.csv saida/rdf/amostra-receitas.nt
transparencia-es-rdf converter despesas dados/despesas/amostra/amostra-despesas.csv saida/rdf/amostra-despesas.nt
```

Em Despesas, o mesmo comando converte qualquer um dos quatro arquivos: a ferramenta lê o cabeçalho do CSV e descobre qual é. O comando mostra quantas linhas leu, quantas triplas gravou e quantas entidades de cada classe escreveu.

### Ver uma amostra em Turtle

A conversão grava N-Triples, com uma tripla por linha, que é o formato bom para gravar à medida que as linhas são lidas e para conferir o resultado. Para ler, uma amostra pode ser regravada em Turtle, que junta as triplas de cada recurso num bloco e encurta os endereços com prefixos:

```
transparencia-es-rdf turtle saida/rdf/amostra-receitas.nt saida/rdf/amostra-receitas.ttl
```

O Turtle tem as mesmas triplas do N-Triples. Só muda a forma dos números sem casas decimais, que aparecem com `.0`: é o jeito curto do Turtle para escrever um decimal. Por isso, para contar e conferir as triplas, use o `.nt`. O comando carrega o grafo inteiro na memória, com a rdflib: nas amostras leva poucos segundos, mas não serve para os arquivos completos.

### Converter um arquivo completo

Baixe o CSV no portal ([Receitas](https://dados.es.gov.br/dataset/portal-da-transparencia-receitas) e [Despesas](https://dados.es.gov.br/dataset/portal-da-transparencia-despesas-execucao-orcamentaria-e-financeira)) e coloque em `dados/receitas/bruto/` ou `dados/despesas/bruto/`, pastas que não vão para o Git. Com `.gz` no fim do nome da saída, o arquivo sai compactado:

```
transparencia-es-rdf converter receitas dados/receitas/bruto/receitas2025.csv saida/rdf/receitas-2025.nt.gz
transparencia-es-rdf converter despesas dados/despesas/bruto/despesas2025.csv saida/rdf/despesas-2025.nt.gz
transparencia-es-rdf converter despesas dados/despesas/bruto/RestosAPagar-2024.csv saida/rdf/restos-a-pagar-2024.nt.gz
transparencia-es-rdf converter despesas dados/despesas/bruto/orcamentosdespesa-2025.csv saida/rdf/orcamentos-despesa-2025.nt.gz
transparencia-es-rdf converter despesas dados/despesas/bruto/orcamentosexecucoes-2025.csv saida/rdf/orcamentos-execucoes-2025.nt.gz
```

As triplas são gravadas à medida que as linhas são lidas, sem carregar o CSV inteiro na memória. Os arquivos de 2025 de Receitas e de Despesas têm cerca de 1 GB e 1,5 GB, e cada conversão leva poucos minutos num computador pessoal.

| Arquivo | Linhas | Triplas |
|---|---:|---:|
| Receitas 2025 | 1.004.745 | 17.293.607 |
| Despesas 2025 | 1.456.562 | 45.509.544 |
| Restos a Pagar 2024 | 8.770 | 100.715 |
| Orçamentos de Despesa 2025 | 72.523 | 1.708.523 |
| Orçamentos de Execuções 2025 | 125 | 2.368 |

O portal atualiza os arquivos, então um CSV baixado em outra data pode dar outros números.

### Validar com SHACL

A ontologia está em OWL, que adota a hipótese de mundo aberto: se um registro aparece sem um dado que a ontologia diz ser obrigatório, um raciocinador OWL não acusa erro, porque o dado pode só não ter sido informado. A SHACL adota o mundo fechado e acusa. A ferramenta traduz as restrições da ontologia (as cardinalidades, o domínio e a imagem de cada propriedade) em formas SHACL e valida os dados com a [pySHACL](https://github.com/RDFLib/pySHACL).

```
transparencia-es-rdf formas despesas
transparencia-es-rdf validar despesas dados/despesas/amostra/amostra-despesas.csv
transparencia-es-rdf validar despesas dados/despesas/bruto/despesas2025.csv
```

O `formas` grava as formas em `saida/formas/<base>.ttl`, só para leitura: o `validar` gera as formas de novo a cada vez, a partir da ontologia. O `validar` mostra o resumo na tela e grava `saida/validacao/<nome do CSV>.csv`, com uma linha por regra violada: a forma, a regra, o tipo da violação, quantos recursos a violam e um recurso de exemplo.

A pySHACL carrega o grafo na memória, então o `validar` converte o CSV em lotes (10.000 linhas por padrão, ou o número dado em `--linhas-por-lote`) e soma o resultado. Cada lote é convertido com um estado novo e sai completo. O que a validação em lotes não vê é um conflito entre lotes: se uma entidade tem uma descrição nas linhas de um lote e outra nas de outro, o "valores a mais" não aparece. Pela velocidade medida em Orçamentos de Despesa (cerca de 5.500 triplas por segundo), o arquivo de Despesas de 2025 leva mais de duas horas para validar, e o de Receitas, perto de uma hora. São estimativas, e o tempo depende do computador.

As violações mostram onde o arquivo do portal e a ontologia não se encaixam. Quase todas são de dado que falta: parte é falta de dado no portal (descrições vazias, municípios com o texto `null`) e parte é algo que a ontologia pede e o arquivo não traz (a unidade orçamentária no arquivo Despesas, os classificadores em Restos a Pagar).

### Consultar com SPARQL

Com os dados em RDF, uma consulta SPARQL junta arquivos diferentes pela mesma entidade: a UG e a fonte, que têm a mesma URI em Receitas e em Despesas, ou o código da função de governo. O `carregar` põe os N-Triples num banco do [Oxigraph](https://github.com/oxigraph/oxigraph) (biblioteca pyoxigraph), que guarda as triplas em disco e por isso aguenta os arquivos completos. O `consultar` roda as consultas nesse banco.

```
transparencia-es-rdf carregar saida/rdf/receitas-2025.nt.gz saida/rdf/despesas-2025.nt.gz saida/rdf/restos-a-pagar-2024.nt.gz saida/rdf/orcamentos-despesa-2025.nt.gz saida/rdf/orcamentos-execucoes-2025.nt.gz
transparencia-es-rdf consultar consultas/*.rq
```

O `carregar` apaga o banco antigo e começa um novo, para não misturar triplas de uma conversão antiga com as de uma nova. Por isso, carregue todos os arquivos de uma vez, e de novo sempre que converter algum deles. O `consultar` mostra o resultado de cada consulta na tela e grava em `saida/consultas/<nome da consulta>.csv`.

As consultas estão em [`consultas/`](consultas), uma por arquivo `.rq`:

| Consulta | O que mostra | Arquivos que junta |
|---|---|---|
| `1-entidades-em-comum.rq` | quantas UGs e quantas fontes aparecem em cada base e nas duas, e a cobertura: a parte das de Receitas que também aparece em Despesas | Receitas e os quatro arquivos de Despesas que estiverem no banco |
| `2-receita-e-despesa-por-ug.rq` | a receita arrecadada (líquida) e a despesa paga das 10 UGs que mais pagaram | Receitas e Despesas |
| `3-receita-e-despesa-por-fonte.rq` | o mesmo, por fonte de recursos | Receitas e Despesas |
| `4-orcado-e-pago-por-funcao.rq` | a dotação atualizada, o valor pago e a parte paga da dotação de cada função de governo | Orçamentos de Despesa e Despesas |
| `5-execucao-por-ug-nos-dois-arquivos.rq` | se o valor pago de cada UG em Orçamentos de Execuções é igual à soma das linhas da UG em Despesas | Orçamentos de Execuções e Despesas |

Para escrever outra consulta, basta criar outro `.rq` na pasta. O comando aceita consultas `SELECT`.

## Como conferir o resultado

A conversão é determinística: o mesmo CSV gera sempre o mesmo N-Triples, byte a byte. Por isso o número de triplas e o SHA-256 da saída servem de conferência depois de qualquer mudança no código. Para as amostras:

```
wc -l saida/rdf/amostra-receitas.nt saida/rdf/amostra-despesas.nt
shasum -a 256 saida/rdf/amostra-receitas.nt saida/rdf/amostra-despesas.nt
```

Quando a saída muda de propósito, por exemplo com uma versão nova da ontologia, a tabela abaixo é atualizada no mesmo commit.

| Amostra | Linhas do CSV | Triplas | SHA-256 do N-Triples |
|---|---:|---:|---|
| `amostra-receitas.csv` | 1.000 | 30.053 | `5635ed7f293e790cabc5f00aa59da0f39d3728c705253be4ec7d03976adcbbfe` |
| `amostra-despesas.csv` | 1.000 | 45.914 | `595ad5975acf03b8e47844caddacde1d4f4b4a2437275743222e2dd025b6cbea` |
| `amostra-restos-a-pagar.csv` | 1.000 | 15.429 | `470ce2897e165a276f08c82cdc8dc7ebe32a5e71c90f667d463f85c59e50ef8e` |
| `amostra-orcamentos-despesa.csv` | 1.000 | 29.984 | `b1739831eeff5f430d623a5835c7440d824419abbff2f82b99cceff691a1e4ca` |
| `amostra-orcamentos-execucoes.csv` | 125 | 2.375 | `3cd77b4439ba60657bb4d77d115eaf9426b3ffaa50245c5ee414db2b5c6c1eed` |

## Organização do repositório

| Pasta | O que tem |
|---|---|
| [`src/transparencia_es_rdf/`](src/transparencia_es_rdf) | o código |
| [`dados/`](dados) | os CSVs: `amostra/` vai para o Git, `bruto/` (os arquivos completos) não |
| [`ontologia/`](ontologia) | a cópia da ontologia usada (ver [A ontologia](#a-ontologia)) |
| [`consultas/`](consultas) | as consultas SPARQL, uma por arquivo `.rq` |
| `saida/` | o que os comandos geram, em `rdf/`, `formas/`, `validacao/`, `banco/` e `consultas/`; não vai para o Git, porque dá para gerar de novo |

### Como o código está organizado

| Pasta ou arquivo | O que tem |
|---|---|
| [`cli.py`](src/transparencia_es_rdf/cli.py) | o comando `transparencia-es-rdf`: lê o que foi digitado e chama as outras partes na ordem certa |
| [`config.py`](src/transparencia_es_rdf/config.py) | o começo das URIs e as pastas |
| [`portal/`](src/transparencia_es_rdf/portal) | a leitura do CSV, que confere o cabeçalho (`leitura.py`) |
| [`rdf/`](src/transparencia_es_rdf/rdf) | o que vale para qualquer base: os namespaces (`vocabularios.py`), o formato N-Triples (`ntriples.py`), a escrita que não repete triplas (`escrita.py`) e a regravação em Turtle (`turtle.py`) |
| [`nucleo/`](src/transparencia_es_rdf/nucleo) | o que as duas bases compartilham: a UG (`unidade_gestora.py`) e a fonte (`fonte.py`) |
| [`receitas/`](src/transparencia_es_rdf/receitas) | a base de Receitas |
| [`despesas/`](src/transparencia_es_rdf/despesas) | a base de Despesas |
| [`validacao/`](src/transparencia_es_rdf/validacao) | a geração das formas SHACL a partir da ontologia (`formas.py`) e a validação em lotes (`validador.py`) |
| [`sparql/`](src/transparencia_es_rdf/sparql) | o banco de triplas em disco: a carga dos N-Triples e as consultas (`banco.py`) |

A pasta de cada base tem os mesmos arquivos:

- `arquivo.py`: como é o CSV (colunas, separador e codificação);
- `mapeamento.py`: de qual coluna vem cada atributo, e quais classes e relações da ontologia ligam as entidades;
- `uris.py`: como cada entidade ganha a sua URI;
- os conversores, que transformam as linhas em triplas. Receitas tem um só (`conversor.py`). Despesas tem um para cada arquivo (`conversor_despesas.py`, `conversor_restos_a_pagar.py`, `conversor_orcamentos_despesa.py` e `conversor_orcamentos_execucoes.py`), e o que os quatro fazem igual fica em `comum.py`.

O caminho de uma linha: `portal/leitura.py` entrega a linha lida do CSV; o conversor da base monta as URIs com o `uris.py`, pega os atributos e as relações no `mapeamento.py` e grava as triplas com `rdf/escrita.py`. Muitas linhas repetem a mesma UG, a mesma natureza ou a mesma fonte, e a escrita guarda o que já gravou para escrever cada uma dessas entidades uma vez só.

No código, uma função com o nome começando em `_` só é usada dentro do próprio arquivo.

## A ontologia

A pasta [`ontologia/`](ontologia) guarda uma cópia dos arquivos do [secont-ontologias](https://github.com/Renzo-Henrique/secont-ontologias) no commit `e99443d`, de 17 de novembro de 2026:

| Pasta | O que tem |
|---|---|
| `out/ttl/` | a ontologia em OWL: `base-receitas.ttl`, `base-despesas.ttl` e `nucleo.ttl` |
| `src/` | o modelo em Tonto, do qual os `.ttl` são gerados |
| `mapeamentos/` | as tabelas da equipe que dizem a qual atributo vai cada coluna do CSV |
| `out/diagramas/` | os diagramas das classes |

A conversão não lê esses arquivos: os nomes das classes e das propriedades estão escritos no `mapeamento.py` de cada base e nos arquivos do `nucleo/`, do mesmo jeito que nos `.ttl`. Eles registram com qual versão da ontologia as triplas foram geradas. A validação lê os `.ttl` de `out/ttl/` para gerar as formas SHACL.

Para atualizar a ontologia:

1. copie para `ontologia/` os arquivos do commit novo do secont-ontologias;
2. veja com `git diff ontologia/out/ttl` o que mudou e corrija os nomes no `mapeamento.py` (e no `nucleo/`, se for o caso);
3. converta e valide as amostras e compare com o resultado de antes: o SHA-256 mostra se as triplas mudaram, e o resumo do `validar` mostra se apareceram violações novas;
4. confira que a saída só mudou onde era esperado, atualize a tabela de [Como conferir o resultado](#como-conferir-o-resultado) e faça um commit só, com o commit da ontologia na mensagem.

## URIs

As URIs dos dados começam com `http://localhost:8000/id/`. Alguns exemplos, tirados das amostras:

| Entidade | URI |
|---|---|
| unidade gestora | `http://localhost:8000/id/unidade-gestora/800102` |
| fonte de recursos | `http://localhost:8000/id/fonte/500.100200` |
| receita (UG emitente e documento) | `http://localhost:8000/id/receitas/2025/receita/800102-2025GR07548` |
| registro de receita (posição da linha no arquivo) | `http://localhost:8000/id/receitas/2025/registro/1` |
| registro de despesa (arquivo e Id da linha) | `http://localhost:8000/id/despesas/despesas/2025/registro/279277262` |

O registro, a classificação e o valor existem uma vez por linha, e cada linha tem os seus. Em Receitas, a URI deles usa a posição da linha no arquivo, porque o CSV não tem uma coluna de identificador. Em Despesas, usa o Id da linha, com o nome do arquivo no caminho, porque o Id só é único dentro de um arquivo.

Esse começo é provisório: hoje essas URIs não levam a nenhuma página. Os namespaces da ontologia também são provisórios (`https://example.org/ontologia-portal-transparencia-es/...`). Quando o projeto tiver endereços definitivos, mudam o `URL_BASE_DADOS`, em `config.py`, e os três namespaces, em `rdf/vocabularios.py`, que têm de ser iguais aos dos `.ttl`.

## Limitações e próximos passos

- As URIs dos dados e os namespaces da ontologia ainda são provisórios.
- As entidades que existem uma vez por linha não têm URI estável: em Receitas a URI usa a posição da linha, que muda se o portal reordenar o arquivo, e em Despesas usa o Id da linha, que muda de um download para outro.
- O favorecido de Restos a Pagar fica de fora, porque a ontologia não tem uma relação que o ligue a esse tipo de registro.
- A validação em lotes não vê conflitos entre entidades de lotes diferentes.
- As ligações com bases externas ficam para depois.

## Autoria e licença

Desenvolvido por Miguel Gewehr de Oliveira, com orientação de Vítor E. Silva Souza e coorientação de Veruska Zamborlini, no projeto do NEMO com a SECONT. A ontologia é mantida pela equipe de modelagem do projeto, no secont-ontologias.

O repositório está sob a licença Creative Commons Atribuição 4.0 Internacional (CC BY 4.0), em [`LICENSE.txt`](LICENSE.txt). Os dados convertidos seguem a licença que o portal informa para cada pacote no dados.es.gov.br.

Para citar:

> OLIVEIRA, Miguel Gewehr de. **Elevando a Maturidade de Dados Abertos**: Conversão para RDF das Bases do Portal da Transparência do Espírito Santo. Monografia (Bacharelado em Ciência da Computação), Universidade Federal do Espírito Santo, Vitória, 2026. Em andamento.
