# Dicionário de dados — aurelio_normalized.db

> Gerado pelo reversa-archaeologist em 2026-07-03, a partir do DDL real (`sqlite_master`).
> Confidência: 🟢 salvo indicação contrária. Comentários de coluna vindos do próprio DDL aparecem entre aspas.

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
| most_used                       | INTEGER    | não         | 🟡 flag de vocabulário frequente (1: 3.039)                                                                                                                                                                                                    |
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
