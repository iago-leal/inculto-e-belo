# pipeline-readest

> Gerado pelo reversa-writer em 2026-10-15 (re-extração). Unit da granularity `module`.
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral

É o alvo da feature 003: gera um dicionário StarDict para o Readest do Mac e do iPhone. Como o Readest mostra um único resultado por consulta, cada palavra pesquisável abre **uma página** que reúne todos os artigos a que ela leva: o do próprio lema, os dos lemas homógrafos e os dos lemas de que ela é forma. O artefato só é entregue depois de duas etapas aprovadas: uma validação independente em Python e uma conferência com o código real de busca do Readest. 🟢

## Responsabilidades

- Agrupar lemas e formas por chave na comparação do Readest, ordenar os artigos de cada página e decidir o destino de cada chave no índice. 🟢
- Gravar o artefato com escritor próprio, na ordem do `cmpAscii`, com trechos compartilhados e `.ifo` determinístico. 🟢
- Validar o artefato simulando a busca do Readest, sem reaproveitar o agrupamento nem o escritor. 🟢
- Conferir o artefato com o `StarDictReader` real do Readest, pelo commit fixado. 🟢
- Promover o artefato aprovado ou guardar o reprovado, sem nunca destruir a última versão aprovada. 🟢

## Regras de Negócio

- RB-02 (fusão no consumidor): a página reúne homônimos e homógrafos só no artefato; o banco não muda. 🟢
- RB-11: `bookname` «Aurélio (uso pessoal, Readest)»; guardar o artefato na nuvem privada do Readest, vinculada à conta do usuário, não é publicação (ADR-0009). 🟢
- RB-12: duas gerações sobre o mesmo banco produzem bytes idênticos; a data do `.ifo` é `gerado_em` do manifesto e a descrição traz a impressão digital do conteúdo. 🟢
- RB-19: cada chave abre exatamente os artigos de todos os lemas a que corresponde, ignorando a caixa como o leitor. 🟢
- RB-20: ordem dos artigos na página: lemas coincidentes com a chave (a grafia exata primeiro), depois os de vocabulário frequente, desempate alfabético sem diacríticos nem caixa e, por fim, pela grafia. 🟢
- RB-21: formas sem letra são descartadas e listadas no relatório; lemas nunca. 🟢
- RB-22: nenhum artefato é entregue sem validação e conferência aprovadas; o reprovado vai para `dist/readest.reprovado/`, e em erro de ambiente nada é promovido nem guardado. 🟢
- RB-23: a conferência usa o código do Readest pelo commit fixado, com SHA-256 dos originais e dos reescritos; o código de terceiros não é versionado. 🟢
- Chave do Readest = `lower()`; ordem = unidades UTF-16 de `lower()`, como o `cmpAscii` (D-03 da 003). 🟢
- Forma de um só lema cuja página é combinada aponta para o trecho do artigo do lema, sem cópia (RN-03 da 003). 🟢
- Cada sequência combinada distinta é gravada uma única vez (D-08 da 003). 🟢

> A numeração RB segue `domain.md`; consulte-o para o texto integral e a evidência.

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Toda chave pesquisável abre exatamente os artigos esperados, na ordem | Must | `pagina-artigos` com 887.546 de 887.546 🟢 |
| RF-02 | Índices em ordem estrita do Readest e sem chave nos dois | Must | `ordem-idx`, `ordem-syn` e `unicidade-cruzada` aprovados 🟢 |
| RF-03 | Artigo idêntico ao do KOReader | Must | Mesmo `renderizar_artigo`; `amostra-conteudo` 500 de 500 🟢 |
| RF-04 | Escrita determinística | Must | Duas escritas, bytes idênticos (teste `test_duas_escritas_produzem_bytes_identicos`) 🟢 |
| RF-05 | Validação independente com nove checks e relatório com até 50 detalhes por check | Must | `validacao-readest.json` com contagem integral 🟢 |
| RF-06 | Conferência com o código real do Readest | Must | `conferencia-readest.json` com chaves e trechos íntegros 🟢 |
| RF-07 | Pré-verificação do ambiente da conferência antes do build | Must | Node abaixo de 22.18 ou npm ausente: exit 2 antes da ingestão 🟢 |
| RF-08 | Promoção condicionada | Must | Aprovado vai para `dist/readest/`; reprovado para `dist/readest.reprovado/`, com a versão anterior intacta 🟢 |
| RF-09 | Importação manual no Readest do Mac, com sync pela conta | Must | Feita em 2026-10-15 (T021 da 003), hash idêntico ao do artefato 🟢 |
| RF-10 | Página combinada com divisor `<hr>` entre artigos | Should | Teste `test_pagina_combinada_une_artigos_com_divisor` 🟢 |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | Build com os dois alvos em cerca de 68 s e 1,4 GB de pico; conferência em cerca de 42 s | Notas da T019 da 003 | 🟢 |
| Reprodutibilidade | gzip com `mtime=0`; `.ifo` sem data de build | `infra/escrita_readest.py:40` | 🟢 |
| Supply chain | Código de terceiros por commit fixo e SHA-256; `npm ci` com lockfile | `conferencia_readest/fonte-readest.json`, `package-lock.json` | 🟢 |
| Disponibilidade | Rede só na primeira obtenção; depois, cache local | `infra/conferencia_readest.py:136` | 🟢 |
| Licença | Código AGPL-3.0 do Readest fora do git | `.gitignore` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado o banco de 2026-07-03, Node 22.18 ou superior e o cache da conferência válido
Quando o mantenedor executa "uv run aurelio-pipeline --alvo readest"
Então dist/readest/aurelio-readest/ contém os quatro arquivos, com 160.302 entradas no .idx e 727.244 no .syn
E dist/readest/relatorios/ contém os três relatórios com veredito "aprovado"
E o processo termina com exit 0

Dado um artefato em que uma forma aponta para a página errada
Quando a validação roda
Então o check pagina-artigos reprova com o nome da chave
E o preparo vai para dist/readest.reprovado/, a versão aprovada anterior segue em dist/readest/ e o exit é 3

Dado um ambiente sem Node.js
Quando o build com o alvo Readest começa
Então AmbienteConferenciaError interrompe antes da ingestão, com exit 2 e a instrução "brew install node"

Dado que a conferência excede 600 s
Quando o tempo se esgota
Então o veredito é "reprovado", com a causa registrada no relatório
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| RF-01 a RF-09 | Must | Sem eles, a consulta no Readest erra ou o artefato pode ser entregue sem prova |
| RF-10 | Should | Legibilidade da página combinada; não afeta a busca |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `pipeline/src/aurelio_pipeline/dominio/agrupamento_readest.py` | `chave_readest`, `ordem_readest`, `tem_letra`, `agrupar` | 🟢 |
| `pipeline/src/aurelio_pipeline/infra/escrita_readest.py` | `EscritorReadest`, `promover`, `reprovar`, `descartar` | 🟢 |
| `pipeline/src/aurelio_pipeline/validacao/paridade_readest.py` | `paginas_esperadas`, `executar_validacao_readest` | 🟢 |
| `pipeline/src/aurelio_pipeline/infra/conferencia_readest.py` | `ConferenciaReadest`, `versao_suficiente` | 🟢 |
| `pipeline/conferencia_readest/conferir.ts` | roteiro da conferência | 🟢 |
| `pipeline/conferencia_readest/fonte-readest.json` | versão fixada, hashes e reescritas | 🟢 |
| `pipeline/src/aurelio_pipeline/dominio/modelos.py` | `PaginaReadest`, `PlanoPaginas`, `RelatorioAgrupamento`, `ResultadoEscritaReadest` | 🟢 |
| `pipeline/src/aurelio_pipeline/cli.py` | `_alvo_readest` | 🟢 |
