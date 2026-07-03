# Domínio — inculto-e-belo

> Gerado pelo reversa-detective em 2026-07-03
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. O que o sistema é (uma frase)

🟢 Um léxico completo do Aurélio, normalizado em SQLite, que serve de fonte única para aplicações de gramática normativa — a primeira delas, um dicionário StarDict para leitura no KOReader (ciclo forward em andamento).

## 2. Glossário de domínio

| Termo                    | Definição                                                                                                                              | Onde vive                           |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| **Verbete (entry)**      | Unidade editorial do dicionário: lema + pronúncia + etimologia + blocos de acepções                                                    | `entries`                           |
| **Lema (lemma)**         | Forma canônica de citação da palavra, com diacríticos; chave conceitual de todo o banco                                                | `entries.lemma`                     |
| **Homônimo**             | Verbetes distintos com o mesmo lema (ex.: "manga¹" fruta, "manga²" da camisa), discriminados por `homonym`; 4.585 lemas nessa condição | `entries.homonym`                   |
| **Slug**                 | Forma normalizada sem diacríticos para busca e ligação                                                                                 | `entries.slug`, `flexions.*_slug`   |
| **Bloco de classe**      | Agrupamento das acepções por classe gramatical dentro do verbete (um verbete "s.m. e adj." tem 2 blocos)                               | `word_class_blocks`                 |
| **Acepção (definition)** | Sentido numerado dentro de um bloco, com rubrica opcional                                                                              | `definitions`                       |
| **Rubrica**              | Marca de domínio, registro ou regionalismo da acepção (ex.: "(Prov.) Bras.", "Med.") — 2.655 distintas                                 | `rubrics`                           |
| **Exemplo**              | Abonação de uso: `editor` (do lexicógrafo) ou `citation` (literária)                                                                   | `examples.kind`                     |
| **Locução**              | Expressão fixa subordinada ao verbete (ex.: "à toa" em "toa"), com definições próprias                                                 | `locutions`, `locution_definitions` |
| **Regência verbal**      | Padrões de transitividade e preposição por acepção, fonte Luft                                                                         | `verb_rection`                      |
| **Flexão**               | Forma nominal derivada (feminino, plural etc.) ligada à cabeça por texto                                                               | `flexions`                          |
| **Conjugação**           | Forma verbal (13 tempos × até 6 pessoas, ~12.972 verbos) ligada ao infinitivo por texto                                                | `conjugations`                      |
| **Forma órfã**           | Flexão/conjugação cujo lema-alvo não existe em `entries.lemma` — 22 casos conhecidos (11 + 11)                                         | derivada                            |
| **Marca ortográfica**    | Grafia anterior ao acordo ortográfico, com regra explicativa                                                                           | `orthographic_marks/rules`          |
| **Headword**             | (ciclo forward) Entrada do índice StarDict; = lema com homônimos fundidos                                                              | specs SDD                           |
| **`.syn`**               | (ciclo forward) Índice StarDict de sinônimos usado para mapear forma flexionada → headword                                             | specs SDD                           |

## 3. Regras de negócio

### Do schema (🟢 CONFIRMADO)

1. **RB-01** — Acepção nunca pertence diretamente ao verbete: sempre via bloco de classe gramatical (`definitions.word_class_block_id NOT NULL`).
2. **RB-02** — Homonímia é preservada, não fundida: cada homônimo é uma linha própria de `entries`; a fusão por lema é decisão do consumidor (o pipeline StarDict funde, o banco não).
3. **RB-03** — Todo conteúdo textual existe em par exibição/busca (`content_html` / `content_text`); as tags de exibição limitam-se a `<em>`, `<u>`, `<strong>` (comentário do DDL).
4. **RB-04** — Ordem editorial é dado explícito (`position` em todas as tabelas ordenadas), nunca ordem física de inserção.
5. **RB-05** — Flexões e conjugações ligam-se ao verbete **por texto** (`entry_head`/`infinitive` ↔ `lemma`), sem constraint física; a integridade referencial é responsabilidade do consumidor e tem 22 violações conhecidas (órfãs).
6. **RB-06** — Busca textual ignora diacríticos (tokenizers `remove_diacritics 2`); acepções adicionalmente com stemming Porter.
7. **RB-07** — Exemplo distingue voz do lexicógrafo (`editor`) de abonação literária (`citation`) — distinção editorial que consumidores devem preservar.
8. **RB-08** — Regência tem fonte única declarada (`source='luft'`), separável do corpo Aurélio.

### Da operação e das decisões registradas (🟢 em documento, 🟡 quando inferida)

9. **RB-09** 🟢 — O `.db` jamais entra no git; backup único via rclone em `gdrive:inculto-e-belo/`; fonte de verdade é a cópia local (README + `.gitignore`).
10. **RB-10** 🟢 — O banco é **somente-leitura** para todo o ciclo forward: órfãs e anomalias são reportadas, nunca corrigidas (decision log das specs SDD; RN-02 da feature 001).
11. **RB-11** 🟢 — Conteúdo sob direitos autorais do Aurélio: qualquer artefato derivado é de uso estritamente pessoal, nunca publicado (PRD §6; commit f431607 já trata o dado como pessoal).
12. **RB-12** 🟢 — Regeneração de artefatos derivados deve ser determinística e auditável (specs SDD: relatórios JSON de cobertura, builds reproduzíveis).
13. **RB-13** 🟡 — O projeto opera sob mantenedor único intermitente: qualquer processo precisa ser retomável por README (padrão em todos os commits e no PRD).

## 4. Invariantes quantitativas (baseline 2026-07-03)

| Invariante                    | Valor                           | Uso                                         |
| ----------------------------- | ------------------------------- | ------------------------------------------- |
| Entries / lemas únicos        | 143.376 / 137.784               | `wordcount` esperado do artefato StarDict   |
| Formas de flexão / conjugação | 175.259 / 869.119 (Σ 1.044.378) | Entrada do `.syn`                           |
| Órfãs conhecidas              | 11 infinitivos + 11 cabeças     | Contrato de descarte do índice de flexões   |
| Acepções / blocos             | 259.337 / 168.361               | Paridade em re-extrações                    |
| Casamento forma→lema          | 99,9%                           | Premissa do produto (lookup de flexionadas) |

## 5. TODOs e intenções não implementadas

- 🟢 Ciclo forward aberto: feature `001-spike-de-flexoes` (gate GO/NO-GO antes do build completo) — `_reversa_forward/`.
- 🟢 Seção `[regen]` do `harness.toml` comentada: ainda não há artefatos derivados a regenerar no encerramento de sessão.
- 🟡 README desatualizado quanto ao schema (8 de 14 tabelas) — candidato a correção fora do escopo Reversa (regra non-destructive).

## 6. Lacunas 🔴 (revisadas em 2026-07-03)

As quatro lacunas da versão inicial foram **resolvidas por amostragem na revisão** (evidência em `data-dictionary.md`):

| #    | Lacuna original                  | Resolução                                                                                                                 |
| ---- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| L-01 | Semântica de `flexions.type`     | 🟢 1=plural, 2=feminino, 3=feminino plural, 4=diminutivo, 5=aumentativo                                                   |
| L-02 | Semântica de `entries.head_type` | 🟢 1=palavra, 2=letra/sigla/símbolo, 3=afixo, 4=locução/expressão estrangeira                                             |
| L-03 | Mapa de `conjugations.tense`     | 🟢 1–13 nomeados (ver `data-dictionary.md` §conjugations)                                                                 |
| L-04 | Critério de `entries.most_used`  | 🟡 vocabulário básico/frequente (amostra coerente: abrir, abraço, absoluto…); critério editorial exato permanece inferido |

### Achado novo da revisão (RB-14)

- **RB-14** 🟢 — `flexions.flexion` pode conter **múltiplas formas numa linha**, separadas por `,` (1.349 linhas) ou `" ou "` (15 linhas); `conjugations` não tem o fenômeno; não há formas vazias em nenhuma das duas tabelas. Consumidores (em especial o `.syn` do pipeline StarDict e o spike da feature 001) devem dividir esses separadores antes de indexar.
