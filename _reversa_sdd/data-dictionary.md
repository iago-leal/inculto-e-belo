# Dicionário de dados — inculto-e-belo

> Gerado pelo reversa-archaeologist em 2026-07-03, a partir do DDL real (`sqlite_master`); revisto na re-extração de 2026-10-15.
> Confidência: 🟢 salvo indicação contrária. Comentários de coluna vindos do próprio DDL aparecem entre aspas.
> Parte 1: o banco `aurelio_normalized.db`, inalterado desde 2026-07-03. Parte 2: as estruturas de dados do pipeline e os formatos dos artefatos e relatórios, novos nesta re-extração.

# Parte 1 — `aurelio_normalized.db`

## entries — 143.376 linhas (137.784 lemas únicos)

| Coluna                          | Tipo       | Obrigatória | Descrição                                                                                                                                                                                                                                      |
| ------------------------------- | ---------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id                              | INTEGER PK | sim         |                                                                                                                                                                                                                                                |
| slug                            | TEXT       | sim         | Forma normalizada p/ busca (sem diacríticos); indexada                                                                                                                                                                                         |
| slug_reverse                    | TEXT       | não         | Slug invertido (busca por sufixo) 🟡                                                                                                                                                                                                           |
| lemma                           | TEXT       | sim         | Lema canônico com diacríticos; indexado; chave textual das ligações com flexions/conjugations                                                                                                                                                  |
| lemma_stylized                  | TEXT       | não         | Lema com marcação tipográfica                                                                                                                                                                                                                  |
| homonym                         | INTEGER    | não         | Discriminador de homônimos (4.585 lemas repetidos)                                                                                                                                                                                             |
| word_class_summary              | TEXT       | não         | "cópia de entries.word_class do original"                                                                                                                                                                                                      |
| ipa                             | TEXT       | não         | Pronúncia, "do `<FNCT>`"                                                                                                                                                                                                                       |
| orthoepy                        | TEXT       | não         | Ortoépia, "do entries.orthoepy original"                                                                                                                                                                                                       |
| etymology_html / etymology_text | TEXT       | não         | Etimologia "do `<ETM>`" (com/sem tags)                                                                                                                                                                                                         |
| head_type                       | INTEGER    | não         | 🟢 1=palavra comum (136.381); 2=letra/sigla/símbolo (1.132: "A", "Å", "A4"); 3=afixo/elemento de composição (3.751: "a-", "-a-"); 4=locução/expressão latina-estrangeira (2.112: "ab absurdo") — resolvido por amostragem [Revisão 2026-07-03] |
| most_used                       | INTEGER    | não         | 🟡 flag de vocabulário frequente (1: 3.039). Desde a feature 003 é coluna requerida pelo pipeline e ordena os artigos não coincidentes nas páginas combinadas do Readest                                                                          |
| sort_key                        | TEXT       | não         | Chave de ordenação editorial                                                                                                                                                                                                                   |

## word_class_blocks — 168.361 linhas

| Coluna        | Tipo                    | Obrigatória | Descrição                          |
| ------------- | ----------------------- | ----------- | ---------------------------------- |
| id            | INTEGER PK AI           | sim         |                                    |
| entry_id      | INTEGER FK→entries      | sim         | Indexada                           |
| word_class_id | INTEGER FK→word_classes | não         | NULL em bloco sem classe declarada |
| position      | INTEGER                 | sim         | Ordem dos blocos no verbete        |
| intro_text    | TEXT                    | não         | "`<DEF_nonum>`, ex.: 'Indica:'"    |

## definitions — 259.337 linhas

| Coluna                      | Tipo                         | Obrigatória | Descrição                                         |
| --------------------------- | ---------------------------- | ----------- | ------------------------------------------------- |
| id                          | INTEGER PK AI                | sim         |                                                   |
| word_class_block_id         | INTEGER FK→word_class_blocks | sim         | Acepção pertence a bloco, nunca direto ao verbete |
| position                    | INTEGER                      | sim         | Ordem dentro do bloco                             |
| number                      | TEXT                         | não         | "valor de DEF@n ('1', '2', '1a'…)"                |
| content_html / content_text | TEXT                         | sim         | Par exibição/busca ("HTML com `<em><u><strong>`") |
| rubric_id                   | INTEGER FK→rubrics           | não         | Domínio/registro da acepção                       |

## examples — 54.726 linhas

| Coluna                      | Tipo                            | Obrigatória | Descrição                                   |
| --------------------------- | ------------------------------- | ----------- | ------------------------------------------- |
| id                          | INTEGER PK AI                   | sim         |                                             |
| definition_id               | INTEGER FK→definitions          | não\*       | \*exatamente um dos dois pais preenchido 🟡 |
| locution_definition_id      | INTEGER FK→locution_definitions | não\*       |                                             |
| position                    | INTEGER                         | sim         |                                             |
| kind                        | TEXT CHECK                      | sim         | `editor` (34.091) ou `citation` (20.635)    |
| content_html / content_text | TEXT                            | sim         |                                             |

## notes — 28.903 linhas

| Coluna                      | Tipo          | Obrigatória | Descrição                                                                                       |
| --------------------------- | ------------- | ----------- | ----------------------------------------------------------------------------------------------- |
| id                          | INTEGER PK AI | sim         |                                                                                                 |
| parent_type                 | TEXT CHECK    | sim         | `entry` (515), `definition` (28.388); `locution`/`locution_definition` admitidos sem ocorrência |
| parent_id                   | INTEGER       | sim         | FK polimórfica (sem constraint física)                                                          |
| position                    | INTEGER       | sim         |                                                                                                 |
| content_html / content_text | TEXT          | sim         |                                                                                                 |

## locutions — 22.168 linhas · locution_definitions — 24.034 linhas

`locutions`: id PK, entry_id FK→entries (indexada), position, expression (TEXT NOT NULL), rubric_id FK→rubrics.
`locution_definitions`: id PK, locution_id FK→locutions (indexada), position, number, content_html/content_text, rubric_id.

## verb_rection — 6.170 linhas

| Coluna       | Tipo                | Obrigatória | Descrição                            |
| ------------ | ------------------- | ----------- | ------------------------------------ |
| id           | INTEGER PK AI       | sim         |                                      |
| entry_id     | INTEGER FK→entries  | sim         | Indexada                             |
| sense        | INTEGER             | não         | "número da acepção (1,2,3…) ou NULL" |
| position     | INTEGER             | sim         | "ordem dentro da acepção"            |
| transitivity | TEXT                | não         | "NULL quando for só observação"      |
| prepositions | TEXT                | não         | "CSV: 'a,contra' ou NULL"            |
| observation  | TEXT                | não         | "NULL para linhas de transitividade" |
| source       | TEXT DEFAULT 'luft' | sim         | 100% `luft`                          |
| raw_text     | TEXT                | não         | Texto original da fonte              |

## flexions — 175.259 linhas

| Coluna          | Tipo       | Obrigatória | Descrição                                                                                                                                                                                                                                                           |
| --------------- | ---------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id              | INTEGER PK | sim         |                                                                                                                                                                                                                                                                     |
| entry_head      | TEXT       | sim         | Lema-cabeça (ligação **textual** com entries.lemma; 11 cabeças órfãs); indexada                                                                                                                                                                                     |
| entry_head_slug | TEXT       | não         |                                                                                                                                                                                                                                                                     |
| flexion         | TEXT       | sim         | Forma flexionada; indexada. ⚠️ Pode conter **múltiplas formas** separadas por `,` (1.349 linhas, ex.: "abatis-timbaís,abatis-timbaí") ou `" ou "` (15 linhas, ex.: "abelhas-carpinteiras ou abelhas-carpinteira") — consumidores devem dividir [Revisão 2026-07-03] |
| flexion_slug    | TEXT       | não         | Indexada                                                                                                                                                                                                                                                            |
| type            | INTEGER    | não         | 🟢 resolvido por amostragem [Revisão 2026-07-03]: 1=plural (111.455), 2=feminino (32.105), 3=feminino plural (31.572), 4=diminutivo (114), 5=aumentativo (13)                                                                                                       |
| homonym         | INTEGER    | não         | Discriminador quando a cabeça é homônima                                                                                                                                                                                                                            |

## conjugations — 869.119 linhas

| Coluna      | Tipo       | Obrigatória | Descrição                                                                                                                                                                                                                                                                                                            |
| ----------- | ---------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id          | INTEGER PK | sim         |                                                                                                                                                                                                                                                                                                                      |
| infinitive  | TEXT       | sim         | Ligação textual com entries.lemma (11 órfãos); indexada com tense                                                                                                                                                                                                                                                    |
| tense       | INTEGER    | sim         | 🟢 mapa resolvido por amostragem ("cantar") [Revisão 2026-07-03]: 1=pres. ind., 2=pret. imperfeito, 3=pret. perfeito, 4=pret. mais-que-perfeito, 5=fut. presente, 6=fut. pretérito, 7=pres. subj., 8=pret. imperf. subj., 9=fut. subj., 10=imperativo (5 pessoas), 11=infinitivo pessoal, 12=gerúndio, 13=particípio |
| person      | TEXT       | não         | eu, tu, ele, nós, vós, eles, vazio                                                                                                                                                                                                                                                                                   |
| conjugation | TEXT       | sim         | Forma conjugada; indexada                                                                                                                                                                                                                                                                                            |
| homonym     | INTEGER    | não         |                                                                                                                                                                                                                                                                                                                      |

## Tabelas de apoio

| Tabela             | Linhas | Estrutura                                                                                     |
| ------------------ | ------ | --------------------------------------------------------------------------------------------- |
| rubrics            | 2.655  | id PK, abbreviation, whole (ex.: "(Prov.) Bras." → "(Prov.) Brasileirismo")                   |
| word_classes       | 302    | id PK, abbreviation, whole (ex.: "Adj." → "Adjetivo")                                         |
| orthographic_marks | 3.280  | PK composta (entry_id, previous_spelling); rule_code → orthographic_rules; grafias pré-acordo |
| orthographic_rules | 15     | rule PK, explanation, examples                                                                |

## Busca textual (FTS5, external content)

| Tabela virtual  | Fonte                 | Colunas                         | Tokenizer                              |
| --------------- | --------------------- | ------------------------------- | -------------------------------------- |
| fts_entries     | content='entries'     | lemma, slug, word_class_summary | `unicode61 remove_diacritics 2`        |
| fts_definitions | content='definitions' | content_text                    | `porter unicode61 remove_diacritics 2` |

⚠️ Por serem external content, dependem das tabelas-fonte no mesmo arquivo; cópia parcial do banco quebra a busca. Tabelas internas (`*_config`, `*_data`, `*_docsize`, `*_idx`) e `sqlite_sequence` são infraestrutura do SQLite.

## Relacionamentos sem constraint física (atenção de integridade)

1. `flexions.entry_head` ↔ `entries.lemma` (textual; 11 órfãs conhecidas)
2. `conjugations.infinitive` ↔ `entries.lemma` (textual; 11 órfãos conhecidos)
3. `notes.parent_id` ↔ pai indicado por `parent_type` (polimórfica)
4. `examples`: exclusividade entre `definition_id` e `locution_definition_id` não imposta por CHECK 🟡

## Colunas consumidas pelo pipeline

🟢 `COLUNAS_REQUERIDAS` em `pipeline/src/aurelio_pipeline/infra/repositorio.py`. A ausência de qualquer uma reprova a ingestão com `EsquemaInvalidoError`, que lista todas as faltantes de uma vez.

| Tabela | Colunas requeridas |
|--------|--------------------|
| entries | id, lemma, lemma_stylized, homonym, word_class_summary, ipa, etymology_html, sort_key, most_used |
| word_class_blocks | id, entry_id, word_class_id, position, intro_text |
| word_classes | id, whole |
| definitions | id, word_class_block_id, position, number, content_html, content_text, rubric_id |
| rubrics | id, abbreviation |
| examples | id, definition_id, locution_definition_id, position, kind, content_html, content_text |
| notes | id, parent_type, parent_id, position, content_html, content_text |
| locutions | id, entry_id, position, expression, rubric_id |
| locution_definitions | id, locution_id, position, number, content_html, content_text, rubric_id |
| verb_rection | id, entry_id, sense, position, transitivity, prepositions, observation |
| flexions | id, entry_head, flexion |
| conjugations | id, infinitive, conjugation |

Não são lidas: `slug`, `slug_reverse`, `orthoepy`, `etymology_text`, `head_type`, `verb_rection.source` e `raw_text`, as colunas `*_slug`, `type` e `homonym` de `flexions` e `conjugations`, `tense` e `person`, as tabelas ortográficas e as tabelas FTS5.

# Parte 2 — pipeline, artefatos e relatórios

## Manifesto de integridade (`pipeline/manifesto-integridade.json`)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| gerado_em | string `AAAA-MM-DD` | Data do banco de referência (`2026-07-03`); vira o `date` do `.ifo` do Readest |
| banco_referencia | string | Nome do arquivo do banco |
| observacao | string | Política: atualização sempre em commit deliberado e próprio |
| contagens | objeto tabela → inteiro | As 12 contagens conferidas a cada build |

## Agregado de leitura (`dominio/modelos.py`, imutável)

| Classe | Campos | Origem no banco |
|--------|--------|-----------------|
| `Verbete` | id, lemma, lemma_stylized, homonym, word_class_summary, ipa, etymology_html, blocos, locucoes, notas, regencias | `entries` e filhos |
| `BlocoClasse` | classe (`word_classes.whole`), intro_text, definicoes | `word_class_blocks` |
| `Definicao` | numero, rubrica (`rubrics.abbreviation`), content_html, content_text, exemplos, notas | `definitions` ou `locution_definitions` |
| `Exemplo` | kind, content_html, content_text | `examples` |
| `Nota` | content_html, content_text | `notes` |
| `Locucao` | expression, rubrica, definicoes, notas | `locutions` |
| `Regencia` | sense, transitivity, prepositions, observation | `verb_rection` |

## Estruturas do alvo Readest (`dominio/modelos.py`)

| Classe | Campos | Descrição |
|--------|--------|-----------|
| `PaginaReadest` | chave (minúsculas), grafia (gravada no índice), lemas (sequência de artigos), destino | Uma chave pesquisável; `combinada` quando há mais de um lema |
| `PlanoPaginas` | paginas, em ordem de índice | `do_idx()` e `do_syn()` separam os destinos |
| `DESTINOS_READEST` | `idx-lema`, `idx-forma-combinada`, `idx-forma-direta`, `syn` | Enum de destino no índice |
| `ResultadoEscritaReadest` | idx, syn, trechos, bytes_corpo, impressao_digital, preparo, artefato, expectativa, duracao_s, arquivos | Saída do escritor |

## Formatos dos artefatos StarDict

| Arquivo | Estrutura | KOReader (`dist/aurelio-stardict/`) | Readest (`dist/readest/aurelio-readest/`) |
|---------|-----------|-------------------------------------|-------------------------------------------|
| `.ifo` | Texto `chave=valor` após a linha mágica | Escrito pelo PyGlossary; `date` é a data do build | Escrito pelo pipeline: `version`, `bookname`, `wordcount`, `synwordcount`, `idxfilesize`, `sametypesequence=h`, `date` do manifesto, `description` com a impressão digital |
| `.idx` | `palavra\0` + offset (u32 BE) + tamanho (u32 BE) | Ordem do PyGlossary; 137.784 entradas | Ordem `cmpAscii` (minúsculas, UTF-16); 160.302 entradas |
| `.syn` | `forma\0` + índice no `.idx` (u32 BE) | 774.003 entradas | 727.244 entradas |
| `.dict.dz` | dictzip (gzip com campo de blocos) | Um artigo por entrada | Páginas com artigos separados por `<hr>`; sequências gravadas uma vez; `mtime=0` |

## Relatórios JSON

| Arquivo | Alvo | Campos |
|---------|------|--------|
| `relatorio-cobertura.json` | KOReader | entrada_linhas, entrada_formas, gravadas, descartes {orfa, duplicada, identica}, orfas, headwords_com_formas |
| `parity-report.json` | KOReader | veredito, gerado_em, seeds {verbetes, flexoes}, contagens, amostras {verbetes_ok, flexoes_ok}, divergencias [{check, detalhe}] |
| `relatorios/relatorio-agrupamento.json` | Readest | chaves, paginas_simples, paginas_combinadas, sequencias_distintas, descartes_sem_letra, formas_descartadas [{forma, lema}], artigos_por_pagina, indice {idx, syn, idx_lemas, idx_formas_combinadas, idx_formas_diretas} |
| `relatorios/validacao-readest.json` | Readest | Mesma forma do `parity-report.json`; seeds {conteudo}; contagens com `falhas_<check>` para os 9 checks |
| `relatorios/conferencia-readest.json` | Readest | readest {tag, commit}, fflate, node, chaves_ok, chaves_falha, trechos_ok, trechos_falha, falhas (até 50), duracao_s, veredito |

## Expectativa da conferência (`expectativa-conferencia.tsv`, só no preparo)

Uma linha por chave do `.idx` e do `.syn`: `grafia\toffset\ttamanho`, com o offset e o tamanho que a busca do Readest deve devolver. É removida na promoção.

## Fonte fixada da conferência (`pipeline/conferencia_readest/fonte-readest.json`)

| Campo | Valor atual | Uso |
|-------|-------------|-----|
| repositorio, tag, commit, base | `readest/readest`, `v0.12.16`, `3cc39ad7…`, `apps/readest-app/src/services/dictionaries/` | Montagem da URL bruta |
| arquivos | SHA-256 de `stardictReader.ts` e `dictZip.ts` originais | Integridade do download |
| reescritas | 3 substituições {arquivo, motivo, de, para} | Compatibilidade com a remoção nativa de tipos do Node |
| arquivos_reescritos | SHA-256 dos dois arquivos depois das reescritas | Validade do cache |
| fflate | `0.8.3` | Versão exigida em `node_modules` |
| node_minimo | `22.18` | Pré-verificação do ambiente |
