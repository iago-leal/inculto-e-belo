# pipeline-nucleo, Tarefas de Implementação

> Gerado pelo reversa-writer em 2026-10-15.

## Pré-requisitos
- [ ] Python ≥ 3.12 e uv; pacote com console script `aurelio-pipeline` (`pipeline/pyproject.toml`)
- [ ] Banco `aurelio_normalized.db` na raiz do repositório e `pipeline/manifesto-integridade.json`
- [ ] Nenhuma variável de ambiente: tudo por argumentos de linha de comando

## Tarefas

- [ ] T-01, Hierarquia de erros nomeados derivada de `ErroPipeline` (ingestão, índice, geração, artefato, conferência)
  - Origem no legado: `pipeline/src/aurelio_pipeline/erros.py:1`
  - Critério de pronto: cada erro de `design.md` existe e termina em exit 2
  - Confiança: 🟢
- [ ] T-02, Modelos imutáveis do agregado (`Verbete`, `BlocoClasse`, `Definicao`, `Exemplo`, `Nota`, `Locucao`, `Regencia`) e `RelatorioCobertura.to_dict`
  - Origem no legado: `pipeline/src/aurelio_pipeline/dominio/modelos.py:7`
  - Critério de pronto: dataclasses `frozen=True`; relatório serializável em JSON
  - Confiança: 🟢
- [ ] T-03, Abertura somente-leitura e erros de abertura
  - Origem no legado: `pipeline/src/aurelio_pipeline/infra/repositorio.py:113`
  - Critério de pronto: URI `mode=ro`; ausente, bloqueado e corrompido distinguidos
  - Confiança: 🟢
- [ ] T-04, `validar()` com `COLUNAS_REQUERIDAS` e manifesto
  - Origem no legado: `pipeline/src/aurelio_pipeline/infra/repositorio.py:36`, `:154`
  - Critério de pronto: divergências agregadas numa mensagem; contagens iguais às do manifesto
  - Confiança: 🟢
- [ ] T-05, Consultas e agregados (`headwords`, `lemas_frequentes`, `flexoes`, `conjugacoes`, `textos_definicoes`, `artigos`) com `ORDEM_FUSAO`
  - Origem no legado: `pipeline/src/aurelio_pipeline/infra/repositorio.py:100`, `:217`–`:391`
  - Critério de pronto: homônimos agrupados por lema e na ordem de fusão
  - Confiança: 🟢
- [ ] T-06, `dividir_formas` e `construir_mapa` com invariante
  - Origem no legado: `pipeline/src/aurelio_pipeline/dominio/indice_flexoes.py:15`–`:89`
  - Critério de pronto: números do banco atual reproduzidos (774.003 gravadas e descartes 748, 220.563 e 50.428)
  - Confiança: 🟢
- [ ] T-07, `renderizar_artigo` com o vocabulário de tags e a ordem de seções de `design.md`
  - Origem no legado: `pipeline/src/aurelio_pipeline/dominio/renderizacao.py:58`, `:112`
  - Critério de pronto: abre com `<b>lema</b>`; numera seções só com mais de um homônimo; advertência acima de 1 MB
  - Confiança: 🟢
- [ ] T-08, CLI e orquestração dos alvos, com pré-verificação e exit code agregado
  - Origem no legado: `pipeline/src/aurelio_pipeline/cli.py:193`–`:304`
  - Critério de pronto: `--alvo` com três valores, padrão `koreader`; `--cobertura`; exit 0, 2 e 3
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Repositório sobre SQLite sintético com mini-schema real: validação, ordem de fusão e erros (`pipeline/tests/test_repositorio.py`, `conftest.py`)
- [ ] TT-02, Índice: split, fragmento vazio, classes de descarte e invariante (`pipeline/tests/test_indice_flexoes.py`)
- [ ] TT-03, Renderização: homônimos numerados, exemplos por tipo, escape (`pipeline/tests/test_renderizacao.py`)
- [ ] TT-04, Nenhum dado do Aurélio nos testes, só dados sintéticos

## Ordem Sugerida
1. T-01 e T-02 (contratos), depois T-03 a T-05 (ingestão).
2. T-06 e T-07 são independentes entre si e dependem só de T-02.
3. T-08 por último, porque integra os alvos de `pipeline-koreader` e `pipeline-readest`.

## Lacunas Pendentes (🔴)
Nenhuma.
