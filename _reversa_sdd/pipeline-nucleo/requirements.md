# pipeline-nucleo

> Gerado pelo reversa-writer em 2026-10-15 (re-extração). Unit da granularity `module`.
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral

É o núcleo comum do pipeline `aurelio-pipeline`. Lê o banco do Aurélio em modo somente-leitura, recusa bancos que não batem com o manifesto de integridade, constrói o mapa de formas flexionadas e renderiza o artigo HTML de cada lema. Também orquestra os alvos KOReader e Readest e traduz o resultado em exit codes. 🟢

## Responsabilidades

- Abrir o banco só para leitura e validar esquema e contagens antes de expor dados. 🟢
- Entregar headwords, lemas frequentes, pares de formas, textos de definições e agregados `Verbete` sem vazar SQL. 🟢
- Construir o mapa lema → formas com descartes classificados e invariante de conservação. 🟢
- Renderizar um artigo HTML integral por lema, com homônimos fundidos. 🟢
- Orquestrar os alvos pedidos em `--alvo` e devolver o pior exit code. 🟢

## Regras de Negócio

- RB-10: o banco é aberto exclusivamente por URI `mode=ro`; nenhuma escrita. 🟢
- RB-15: esquema (12 tabelas e colunas requeridas) e contagens conferidos contra `manifesto-integridade.json`; divergência é erro nomeado. 🟢
- RB-02: homônimos de um lema chegam juntos, ordenados por `homonym` (os nulos por último), `sort_key` e `id`, e viram seções numeradas de um artigo único. 🟢
- RB-14: `flexions.flexion` é dividido por `,` e `" ou "`; forma ou fragmento vazio é erro com tabela e id. 🟢
- RB-16: cada forma é classificada nesta ordem: órfã, idêntica, duplicada ou gravada; a soma das classes é igual à entrada. 🟢
- RB-07: o exemplo do editor sai em `<i>`, e a abonação em `<small><i>`. 🟢
- O artigo sempre abre com `<b>lema</b>`; o alvo Readest depende dessa marca. 🟢
- Com os dois alvos, ingestão e índice rodam uma vez, e o exit code é o máximo entre os alvos. 🟢
- A data do `.ifo` do KOReader é a do build; a do Readest é `gerado_em` do manifesto. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Abrir o banco em `mode=ro`, com erros nomeados para ausente, bloqueado e corrompido | Must | Cada condição produz a exceção correspondente, com instrução de recuperação 🟢 |
| RF-02 | Validar esquema e contagens contra o manifesto, listando todas as divergências de uma vez | Must | Banco com coluna faltando e contagem diferente produz um único erro com todas as divergências 🟢 |
| RF-03 | Expor `headwords()`, `lemas_frequentes()`, `flexoes()`, `conjugacoes()`, `textos_definicoes()` e `artigos()` | Must | Contratos de `design.md` honrados; nenhum cursor ou SQL sai do repositório 🟢 |
| RF-04 | Construir o mapa de formas com split RB-14, descartes classificados e relatório | Must | Banco atual: 774.003 gravadas, 748 órfãs, 220.563 duplicadas, 50.428 idênticas 🟢 |
| RF-05 | Renderizar o artigo HTML integral de cada lema | Must | Todas as definições do banco aparecem no texto do artigo 🟢 |
| RF-06 | Opção `--cobertura flexions-somente`, que exclui as conjugações | Could | Mapa sem formas de `conjugations` 🟢 |
| RF-07 | `--alvo koreader\|readest\|ambos`, com padrão `koreader` | Must | Sem a opção, o comportamento é o da feature 002 🟢 |
| RF-08 | Pré-verificar a conferência do Readest antes da ingestão quando o Readest está no alvo | Must | Node ausente faz o build parar antes de ler o banco, com exit 2 🟢 |
| RF-09 | Exit codes: 0 aprovado, 2 erro nomeado, 3 reprovado | Must | Testado por alvo e na combinação 🟢 |
| RF-10 | Advertir no log os artigos acima de 1 MB, sem falhar | Could | Advertência com lema e tamanho 🟢 |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Disponibilidade | Espera de até 5 s por banco bloqueado | `infra/repositorio.py:122` | 🟢 |
| Segurança | Banco somente-leitura por construção | `infra/repositorio.py:122` (`mode=ro`) | 🟢 |
| Observabilidade | Logs chave=valor por etapa, com progresso a cada 100.000 formas | `cli.py`, `dominio/indice_flexoes.py:17` | 🟢 |
| Performance | Build só com o KOReader em cerca de 12 s; com os dois alvos, cerca de 68 s e 1,4 GB de pico | Notas da T019 da 003 e commit d6efb26 | 🟢 |
| Manutenibilidade | Domínio puro sem I/O, testado com dados sintéticos | `dominio/`, `tests/` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado o banco de 2026-07-03 e o manifesto correspondente
Quando o mantenedor executa "uv run aurelio-pipeline"
Então a ingestão registra smoke_tests_ok, o índice grava 774.003 formas e o processo termina com exit 0

Dado um banco regenerado com contagens diferentes do manifesto
Quando o build é executado
Então o processo para com ContagemDivergenteError, exit 2, e a mensagem manda atualizar o manifesto em commit próprio

Dado um banco sem a coluna entries.most_used
Quando o build é executado
Então EsquemaInvalidoError lista "colunas ausentes em entries: most_used"

Dado o alvo "ambos" e o KOReader aprovado, mas o Readest reprovado
Quando o build termina
Então o exit code é 3
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| RF-01, RF-02, RF-03 | Must | Todos os alvos dependem da ingestão |
| RF-04, RF-05 | Must | Formam o conteúdo dos dois artefatos |
| RF-07, RF-08, RF-09 | Must | Contrato com o operador e com o `[regen]` |
| RF-06 | Could | Fallback do spike, raramente usado |
| RF-10 | Could | Caso de borda |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `pipeline/src/aurelio_pipeline/cli.py` | `executar`, `main`, `_data_referencia` | 🟢 |
| `pipeline/src/aurelio_pipeline/erros.py` | `ErroPipeline` e subclasses | 🟢 |
| `pipeline/src/aurelio_pipeline/infra/repositorio.py` | `RepositorioAurelio` | 🟢 |
| `pipeline/src/aurelio_pipeline/dominio/indice_flexoes.py` | `dividir_formas`, `construir_mapa` | 🟢 |
| `pipeline/src/aurelio_pipeline/dominio/renderizacao.py` | `renderizar_artigo` | 🟢 |
| `pipeline/src/aurelio_pipeline/dominio/modelos.py` | `Verbete` e agregados, `RelatorioCobertura`, `ResultadoBuild` | 🟢 |
| `pipeline/manifesto-integridade.json` | contagens e `gerado_em` | 🟢 |
