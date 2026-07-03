# ERD completo — aurelio_normalized.db

> Gerado pelo reversa-architect em 2026-07-03 a partir do DDL real. 🟢 CONFIRMADO.
> Linhas tracejadas conceituais: ligações **textuais sem FK** (integridade por convenção).

```mermaid
erDiagram
    entries ||--o{ word_class_blocks : "entry_id"
    word_classes ||--o{ word_class_blocks : "word_class_id"
    word_class_blocks ||--o{ definitions : "word_class_block_id"
    rubrics ||--o{ definitions : "rubric_id"
    definitions ||--o{ examples : "definition_id"
    locution_definitions ||--o{ examples : "locution_definition_id"
    entries ||--o{ locutions : "entry_id"
    rubrics ||--o{ locutions : "rubric_id"
    locutions ||--o{ locution_definitions : "locution_id"
    rubrics ||--o{ locution_definitions : "rubric_id"
    entries ||--o{ verb_rection : "entry_id"
    entries ||--o{ orthographic_marks : "entry_id"
    orthographic_rules ||--o{ orthographic_marks : "rule_code (textual)"
    entries ||..o{ flexions : "entry_head = lemma (SEM FK; 11 orfas)"
    entries ||..o{ conjugations : "infinitive = lemma (SEM FK; 11 orfaos)"
    entries ||..o{ notes : "parent_type=entry (polimorfica)"
    definitions ||..o{ notes : "parent_type=definition (polimorfica)"

    entries {
        INTEGER id PK
        TEXT slug "indexada"
        TEXT lemma "indexada; 137.784 unicos"
        INTEGER homonym "4.585 lemas repetidos"
        TEXT word_class_summary
        TEXT ipa
        TEXT etymology_html
        INTEGER head_type "semantica nao documentada"
        INTEGER most_used "flag 0/1"
        TEXT sort_key
    }
    word_class_blocks {
        INTEGER id PK
        INTEGER entry_id FK
        INTEGER word_class_id FK
        INTEGER position
        TEXT intro_text
    }
    definitions {
        INTEGER id PK
        INTEGER word_class_block_id FK
        INTEGER position
        TEXT number
        TEXT content_html
        TEXT content_text
        INTEGER rubric_id FK
    }
    examples {
        INTEGER id PK
        INTEGER definition_id FK "exclusivo com locution_definition_id"
        INTEGER locution_definition_id FK
        INTEGER position
        TEXT kind "editor|citation (CHECK)"
        TEXT content_html
    }
    notes {
        INTEGER id PK
        TEXT parent_type "CHECK 4 valores"
        INTEGER parent_id "polimorfica"
        INTEGER position
        TEXT content_html
    }
    locutions {
        INTEGER id PK
        INTEGER entry_id FK
        INTEGER position
        TEXT expression
        INTEGER rubric_id FK
    }
    locution_definitions {
        INTEGER id PK
        INTEGER locution_id FK
        INTEGER position
        TEXT number
        TEXT content_html
        INTEGER rubric_id FK
    }
    verb_rection {
        INTEGER id PK
        INTEGER entry_id FK
        INTEGER sense
        INTEGER position
        TEXT transitivity
        TEXT prepositions "CSV"
        TEXT observation
        TEXT source "default luft"
        TEXT raw_text
    }
    flexions {
        INTEGER id PK
        TEXT entry_head "ligacao textual"
        TEXT flexion "indexada"
        TEXT flexion_slug "indexada"
        INTEGER type "1-5 nao documentado"
        INTEGER homonym
    }
    conjugations {
        INTEGER id PK
        TEXT infinitive "ligacao textual"
        INTEGER tense "1-13"
        TEXT person "eu..eles ou vazio"
        TEXT conjugation "indexada"
        INTEGER homonym
    }
    rubrics {
        INTEGER id PK
        TEXT abbreviation
        TEXT whole
    }
    word_classes {
        INTEGER id PK
        TEXT abbreviation
        TEXT whole
    }
    orthographic_marks {
        INTEGER entry_id PK "PK composta"
        TEXT previous_spelling PK
        TEXT rule_code
        INTEGER symbol
    }
    orthographic_rules {
        TEXT rule PK
        TEXT explanation
        TEXT examples
    }
```

## Cardinalidades e volumes

| Relação                         | Cardinalidade | Volume médio                                 |
| ------------------------------- | ------------- | -------------------------------------------- |
| entries → word_class_blocks     | 1:N           | 1,17 blocos/verbete (168.361/143.376)        |
| word_class_blocks → definitions | 1:N           | 1,54 acepções/bloco (259.337/168.361)        |
| definitions → examples          | 1:N esparso   | 54.726 exemplos p/ 259.337 acepções          |
| entries → locutions             | 1:N esparso   | 22.168 locuções                              |
| entries ⇢ flexions              | 1:N textual   | 175.259 formas                               |
| entries ⇢ conjugations          | 1:N textual   | 869.119 formas (~12.972 verbos × ~67 formas) |

## FTS5 (fora do ERD relacional)

`fts_entries` (lemma/slug/classe) e `fts_definitions` (content_text) são tabelas virtuais **external content** apontando para `entries` e `definitions` via `content_rowid` — dependem do mesmo arquivo e quebram em cópias parciais.
