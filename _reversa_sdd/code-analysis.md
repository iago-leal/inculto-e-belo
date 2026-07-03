# Análise técnica — inculto-e-belo

> Gerado pelo reversa-archaeologist em 2026-07-03
> Módulos: `banco-lexical`, `governanca-operacional`
> Confidência: 🟢 CONFIRMADO (extraído do banco/arquivos), 🟡 INFERIDO, 🔴 LACUNA

## Módulo `banco-lexical`

### 1. Natureza

🟢 Não há código executável: o módulo é o schema e o conteúdo de `aurelio_normalized.db` (SQLite, WAL, FTS5). A "lógica" está congelada na estrutura relacional — a normalização feita no projeto de origem (`JailBrake Aurelio`) — e nos índices e tokenizers escolhidos.

### 2. Modelo hierárquico do verbete

🟢 O caminho de composição de um verbete completo é:

```
entries (1) ──< word_class_blocks (N, por classe gramatical)
                    └──< definitions (N, acepções ordenadas por position)
                              ├── rubric_id → rubrics (marcação de domínio/registro)
                              ├──< examples (kind: 'editor' | 'citation')
                              └──< notes (parent_type='definition')
entries ──< locutions ──< locution_definitions ──< examples / notes
entries ──< verb_rection (regência, fonte 'luft')
entries ──< notes (parent_type='entry')
entries ──< orthographic_marks → orthographic_rules (grafias pré-acordo)
entries >── flexions (por entry_head, texto, não FK)   [175.259]
entries >── conjugations (por infinitive, texto, não FK) [869.119]
```

Ponto estrutural relevante: **`flexions` e `conjugations` ligam-se a `entries` por texto (`entry_head`/`infinitive` ↔ `lemma`), não por chave estrangeira** — daí as 22 formas órfãs conhecidas (11 infinitivos + 11 cabeças sem verbete). 🟢

### 3. Dicionário de dados

Detalhe completo em `data-dictionary.md`. Contagens verificadas nesta análise:

| Tabela            | Linhas  |     | Tabela               | Linhas |
| ----------------- | ------- | --- | -------------------- | ------ |
| entries           | 143.376 |     | locutions            | 22.168 |
| word_class_blocks | 168.361 |     | locution_definitions | 24.034 |
| definitions       | 259.337 |     | verb_rection         | 6.170  |
| examples          | 54.726  |     | rubrics              | 2.655  |
| notes             | 28.903  |     | word_classes         | 302    |
| flexions          | 175.259 |     | orthographic_marks   | 3.280  |
| conjugations      | 869.119 |     | orthographic_rules   | 15     |

### 4. Domínios de valores (enums implícitos)

| Campo                 | Valores observados                                                                                                                                 | Interpretação                                                                                                                                                                                                                                            | Confidência       |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| `examples.kind`       | `editor` (34.091), `citation` (20.635)                                                                                                             | Exemplo do lexicógrafo vs. abonação literária                                                                                                                                                                                                            | 🟢 (CHECK no DDL) |
| `notes.parent_type`   | `definition` (28.388), `entry` (515)                                                                                                               | Nota por acepção ou por verbete; DDL admite `locution`/`locution_definition`, sem ocorrências                                                                                                                                                            | 🟢                |
| `conjugations.tense`  | 1–13; tenses 1–9 e 11 com 77.832 linhas (= 12.972 verbos × 6 pessoas), tense 10 com 64.859 (= × 5 pessoas), tenses 12–13 com ~12.97x (1 por verbo) | Mapa resolvido por amostragem [Revisão 2026-07-03]: 1=pres. ind., 2=pret. imperf., 3=pret. perf., 4=mais-que-perf., 5=fut. pres., 6=fut. pret., 7=pres. subj., 8=imperf. subj., 9=fut. subj., 10=imperativo, 11=inf. pessoal, 12=gerúndio, 13=particípio | 🟢                |
| `conjugations.person` | eu, tu, ele, nós, vós, eles, vazio                                                                                                                 | Pessoa gramatical; vazio nas formas sem pessoa                                                                                                                                                                                                           | 🟢                |
| `flexions.type`       | 1 (111.455), 2 (32.105), 3 (31.572), 4 (114), 5 (13)                                                                                               | 1=plural, 2=feminino, 3=feminino plural, 4=diminutivo, 5=aumentativo — resolvido por amostragem [Revisão 2026-07-03]                                                                                                                                     | 🟢                |
| `entries.head_type`   | 1 (136.381), 2 (1.132), 3 (3.751), 4 (2.112)                                                                                                       | 1=palavra, 2=letra/sigla/símbolo, 3=afixo/elemento de composição, 4=locução/expressão estrangeira [Revisão 2026-07-03]                                                                                                                                   | 🟢                |
| `entries.most_used`   | 0 (140.337), 1 (3.039)                                                                                                                             | 🟡 Flag de alta frequência de uso (vocabulário básico)                                                                                                                                                                                                   | 🟡                |
| `verb_rection.source` | `luft` (100%)                                                                                                                                      | Fonte única: dicionário de regência do Luft                                                                                                                                                                                                              | 🟢                |

### 5. Invariantes e regras embutidas no schema

1. 🟢 Acepções pertencem a **blocos de classe**, não diretamente ao verbete (`definitions.word_class_block_id NOT NULL`); um verbete com duas classes tem ≥ 2 blocos ordenados por `position`.
2. 🟢 Homonímia é modelada por linhas separadas em `entries` com o mesmo `lemma` e campo `homonym` discriminador: 4.585 lemas têm mais de um entry (143.376 entries ↔ 137.784 lemas únicos).
3. 🟢 Todo conteúdo textual existe em par `content_html` / `content_text` (HTML com `<em>/<u>/<strong>` para exibição; texto puro para busca).
4. 🟢 Ordenação editorial é sempre por `position` explícito — nenhuma dependência de ordem de inserção.
5. 🟢 Busca textual: `fts_entries` (tokenizer `unicode61 remove_diacritics 2` sobre lemma/slug/classe) e `fts_definitions` (`porter unicode61 remove_diacritics 2` sobre o texto das acepções), ambas como external content (`content=`) — exigem o mesmo arquivo `.db` como fonte.
6. 🟢 `orthographic_marks` registra grafias anteriores ao acordo ortográfico por verbete, com `rule_code` → `orthographic_rules` (15 regras com explicação e exemplos).

### 6. Fluxo de consulta típico (em texto; diagrama em `flowcharts/banco-lexical.md`)

Lookup de leitura: forma tocada → busca exata em `entries.lemma` → se ausente, busca em `flexions.flexion` / `conjugations.conjugation` → resolve `entry_head`/`infinitive` → verbete → monta artigo na ordem `word_class_blocks.position` → `definitions.position`, anexando rubrica, exemplos, notas, locuções e regência. É exatamente o caminho que o pipeline forward vai materializar em StarDict (`.idx` = lemas; `.syn` = formas).

### 7. Metadados e configuração

Nenhum feature flag ou parâmetro de ambiente: o módulo é dado puro. As únicas "configurações" são os tokenizers FTS5 (embutidos no DDL) e o modo WAL do arquivo.

## Módulo `governanca-operacional`

### 1. Componentes

| Arquivo                     | Papel                                                                                                           | Análise                                                                        |
| --------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `harness` (bash, 15 linhas) | Shim que resolve `upstream_path` de `harness.toml` via `sed` e faz `exec` do core Python do Harness no upstream | 🟢 Falha barulhenta se o upstream não existir; nenhuma lógica de negócio local |
| `harness.toml`              | Config: harness ativo (`claude`), caminho do upstream, arquivos de estado/decisões                              | 🟢 Seção `[regen]` comentada — sem artefatos derivados ainda                   |
| `.gitignore`                | Exclui `*.db`/`*.sqlite` (+WAL/SHM), `.DS_Store`, `__pycache__`, cache do harness                               | 🟢 Regra crítica: o ativo de 189 MB nunca entra no git                         |
| `README.md`                 | Runbook: restaurar (`rclone copy gdrive:...`), reenviar backup, abrir o banco, proveniência                     | 🟢 Desatualizado no schema: lista 8 das 14 tabelas de domínio                  |

### 2. Regras operacionais embutidas

1. 🟢 Fonte de verdade é a cópia local; backup único em `gdrive:inculto-e-belo/` via rclone (procedimentos bidirecionais no README).
2. 🟢 Proveniência registrada: importado por `sqlite3 .backup` da extração do `JailBrake Aurelio` em 2026-07-03, com `integrity_check` ok e contagens validadas.
3. 🟡 Não há verificação automática de integridade pós-restauração — o runbook é manual.

## Resumo para o Reversa

- Módulos analisados: 2 de 2 (`banco-lexical`, `governanca-operacional`)
- Algoritmos: nenhum código executável de domínio; a inteligência está no schema (hierarquia de composição do verbete, pares HTML/texto, FTS5 com remoção de diacríticos, ligação textual lemma↔formas)
- Entidades: 14 tabelas de domínio documentadas em `data-dictionary.md`
- Lacunas 🔴: semântica de `flexions.type` e `entries.head_type`; mapa numérico de `conjugations.tense`
