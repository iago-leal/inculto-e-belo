# banco-lexical, Design Técnico

> Gerado pelo reversa-writer em 2026-07-03. Foco no COMO a unit é construída. 🟢 salvo indicação.

## Interface

A interface é SQL sobre o arquivo. Consultas canônicas:

| Operação              | SQL (esqueleto)                                                                                                                                       | Retorno                      |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| Verbete por lema      | `SELECT * FROM entries WHERE lemma = ? ORDER BY homonym, sort_key`                                                                                    | 1..N entries (homônimos)     |
| Blocos e acepções     | `SELECT ... FROM word_class_blocks wcb JOIN definitions d ON d.word_class_block_id = wcb.id WHERE wcb.entry_id = ? ORDER BY wcb.position, d.position` | estrutura editorial ordenada |
| Forma nominal → lema  | `SELECT entry_head, homonym FROM flexions WHERE flexion = ?`                                                                                          | 0..N cabeças                 |
| Forma verbal → lema   | `SELECT infinitive FROM conjugations WHERE conjugation = ?`                                                                                           | 0..N infinitivos             |
| Busca sem diacríticos | `SELECT rowid FROM fts_entries WHERE fts_entries MATCH ?`                                                                                             | rowids de entries            |
| Abertura segura       | URI `file:aurelio_normalized.db?mode=ro`                                                                                                              | conexão somente-leitura      |

## Fluxo Principal (montagem de verbete)

1. Resolver lema (direto ou via flexions/conjugations) — índices `idx_entries_lemma`, `idx_flex_form`, `idx_conj_form`.
2. Carregar entries do lema (todos os homônimos, ordem `homonym`, `sort_key`).
3. Por entry: blocos (`word_class_blocks` + `word_classes`), acepções (`definitions` + `rubrics`), exemplos (`examples` por `definition_id`), notas (`notes` polimórfica), locuções (`locutions` → `locution_definitions`), regência (`verb_rection`).
4. Renderizar respeitando `position` em todos os níveis e o par html/text conforme o destino.

## Fluxos Alternativos

- **Forma órfã:** resolução forma→lema não encontra `entries.lemma`; consumidor reporta e segue (RB-05).
- **Forma ambígua:** N cabeças/infinitivos distintos; todos são resultados válidos (desambiguação fica com o leitor).
- **Cópia parcial do arquivo:** tabelas FTS5 external content quebram — o arquivo é indivisível.

## Dependências

- SQLite ≥ 3 com FTS5 habilitado (tokenizers `unicode61 remove_diacritics 2`, `porter`).
- Nenhuma outra.

## Decisões de Design Identificadas

| Decisão                                                                      | Evidência                 | Confiança |
| ---------------------------------------------------------------------------- | ------------------------- | --------- |
| Normalização editorial completa (14 tabelas) em vez de blob HTML por verbete | DDL; ADR-0001             | 🟢        |
| Par `content_html`/`content_text` para separar exibição de busca             | DDL (comentários)         | 🟢        |
| Ligação textual lemma↔formas (herdada da origem), sem FK                     | DDL flexions/conjugations | 🟢        |
| FTS5 external content (economia de espaço, mesma fonte)                      | DDL fts\_\*               | 🟢        |
| WAL mode (arquivos -shm/-wal presentes)                                      | filesystem                | 🟢        |

## Estado Interno

Estático entre regenerações. Única evolução prevista: reimportação completa da origem (nunca update incremental). Versões distinguem-se por contagens-baseline e proveniência no README.

## Observabilidade

Nenhuma embutida (é um arquivo). A auditoria é externa: `PRAGMA integrity_check`, contagens-baseline (`domain.md` §4) e, no pipeline futuro, relatórios JSON de cobertura.

## Riscos e Lacunas

- 🔴 Semântica de `flexions.type` (1–5), `entries.head_type` (1–4) e mapa `conjugations.tense` 1–13 — ver `questions.md` da unit.
- 🟡 Exclusividade `examples.definition_id` ⊕ `locution_definition_id` não imposta por CHECK; assumida pela modelagem.
- 🟡 `orthographic_marks.rule_code` → `orthographic_rules.rule` é ligação textual sem FK.
