# Flowchart — módulo `banco-lexical`

> Gerado pelo reversa-archaeologist em 2026-07-03. O módulo é dado puro; os fluxos abaixo descrevem (1) a composição de um verbete e (2) o lookup de leitura que o pipeline forward materializará em StarDict.

## 1. Composição de um verbete completo

```mermaid
flowchart TD
    E[entries: lema, homonym, IPA, etimologia] --> WCB[word_class_blocks<br/>ordenados por position]
    WCB --> WC[word_classes<br/>ex.: Adj. → Adjetivo]
    WCB --> D[definitions<br/>ordenadas por position, numeradas]
    D --> R[rubrics<br/>domínio/registro da acepção]
    D --> EX[examples<br/>kind: editor ou citation]
    D --> ND[notes parent_type=definition]
    E --> L[locutions] --> LD[locution_definitions] --> EX2[examples]
    E --> VR[verb_rection<br/>fonte luft: transitividade, preposições]
    E --> NE[notes parent_type=entry]
    E --> OM[orthographic_marks] --> OR[orthographic_rules]
```

## 2. Lookup de uma forma tocada (fluxo-alvo do produto)

```mermaid
flowchart TD
    T[Forma tocada no leitor] --> X{Existe em entries.lemma?}
    X -- sim --> V[Verbete direto<br/>homônimos fundidos por lema]
    X -- não --> F{Existe em flexions.flexion?}
    F -- sim --> FH[entry_head → entries.lemma]
    F -- não --> C{Existe em conjugations.conjugation?}
    C -- sim --> CI[infinitive → entries.lemma]
    C -- não --> Z[Sem resultado<br/>órfãs: 11 cabeças + 11 infinitivos]
    FH --> V
    CI --> V
    V --> A[Artigo montado na ordem<br/>blocos → acepções → exemplos/notas/locuções/regência]
```

⚠️ As ligações `flexions.entry_head ↔ entries.lemma` e `conjugations.infinitive ↔ entries.lemma` são **textuais, sem FK** — a resolução de órfãs é responsabilidade de quem consome.

## 3. Busca textual (FTS5)

```mermaid
flowchart LR
    Q[consulta] --> FE[fts_entries<br/>unicode61 remove_diacritics 2]
    Q --> FD[fts_definitions<br/>porter + unicode61]
    FE --> E2[entries via content_rowid]
    FD --> D2[definitions via content_rowid]
```
