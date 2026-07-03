# banco-lexical

> Gerado pelo reversa-writer em 2026-07-03. Unit da extração reversa (granularity `module`).
> Foco no QUE a unit oferece. Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral

O léxico completo do Aurélio normalizado num único SQLite (`aurelio_normalized.db`, ~189 MB): 143.376 verbetes com acepções, exemplos, locuções, regência, flexões e conjugações, mais busca FTS5. É a fonte única de todos os consumidores presentes (consultas ad-hoc) e futuros (pipeline StarDict).

## Responsabilidades

- Guardar o léxico com a estrutura editorial preservada (blocos de classe → acepções numeradas → exemplos/notas).
- Oferecer as formas flexionadas e conjugadas prontas, ligadas ao lema por texto.
- Prover busca textual insensível a diacríticos (`fts_entries`, `fts_definitions`).
- Servir de contrato de leitura estável para o pipeline forward (banco somente-leitura).

## Regras de Negócio

- RB-01 — Acepção pertence a bloco de classe gramatical, nunca diretamente ao verbete. 🟢
- RB-02 — Homonímia preservada em linhas distintas (`homonym`); fusão por lema é responsabilidade do consumidor. 🟢
- RB-03 — Conteúdo textual sempre em par `content_html`/`content_text`; tags restritas a `<em>/<u>/<strong>`. 🟢
- RB-04 — Ordem editorial por `position` explícito. 🟢
- RB-05 — Ligações lemma↔formas são textuais, sem FK; 22 órfãs conhecidas são reportadas, nunca corrigidas. 🟢
- RB-10 — Consumidores abrem o banco em modo somente-leitura (`mode=ro`). 🟢 (decisão registrada)
- RB-11 — Conteúdo sob direitos autorais: derivados de uso estritamente pessoal. 🟢

## Requisitos Funcionais

| ID    | Requisito                                                                                                                               | Prioridade | Critério de Aceite                                                                |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------------------------- |
| RF-01 | Fornecer verbete completo por lema: entries + blocos + acepções + rubricas + exemplos + notas + locuções + regência, na ordem editorial | Must       | Consulta por `lemma='belo'` devolve estrutura completa ordenada por `position` 🟢 |
| RF-02 | Resolver forma flexionada/conjugada ao(s) lema(s): `flexions.flexion` e `conjugations.conjugation` indexadas                            | Must       | `SELECT entry_head FROM flexions WHERE flexion='árvores'` responde via índice 🟢  |
| RF-03 | Busca textual sem diacríticos em lemas e acepções                                                                                       | Should     | `fts_entries MATCH 'arvore'` encontra "árvore" 🟢                                 |
| RF-04 | Expor grafias pré-acordo com regra explicativa                                                                                          | Could      | `orthographic_marks` join `orthographic_rules` 🟢                                 |
| RF-05 | Manter contagens-baseline auditáveis (143.376 entries; 1.044.378 formas)                                                                | Must       | Contagens batem com `domain.md` §4 após restauração 🟢                            |

## Requisitos Não Funcionais

| Tipo          | Requisito inferido                                                                                   | Evidência            | Confiança |
| ------------- | ---------------------------------------------------------------------------------------------------- | -------------------- | --------- |
| Integridade   | `PRAGMA integrity_check` = ok é pré-condição de uso após restauração                                 | README §Proveniência | 🟢        |
| Performance   | Lookups por lema/forma via índices dedicados (`idx_entries_lemma`, `idx_flex_form`, `idx_conj_form`) | DDL                  | 🟢        |
| Portabilidade | Arquivo único SQLite consumível por qualquer stack com FTS5                                          | ADR-0001             | 🟢        |
| Durabilidade  | Backup íntegro no Drive; restauração documentada                                                     | ADR-0002             | 🟢        |

## Critérios de Aceitação

```gherkin
Dado o banco restaurado de backup
Quando PRAGMA integrity_check executa e as contagens-baseline são conferidas
Então o resultado é "ok" e os totais batem com domain.md §4

Dado a forma "cantávamos" presente em conjugations
Quando se consulta conjugations.conjugation = 'cantávamos'
Então o infinitive retornado ("cantar") existe em entries.lemma

Dado uma forma órfã (uma das 22 conhecidas)
Quando um consumidor resolve forma → lema
Então a ausência é reportada como órfã, e o banco não é alterado
```

## Prioridade (MoSCoW)

| Requisito           | MoSCoW | Justificativa                                    |
| ------------------- | ------ | ------------------------------------------------ |
| RF-01, RF-02, RF-05 | Must   | Caminho crítico de todos os consumidores         |
| RF-03               | Should | Busca é conveniência; lookup exato é o essencial |
| RF-04               | Could  | Uso gramatical futuro, sem consumidor atual      |

## Rastreabilidade de Código

| Arquivo                        | Elemento                                                     | Cobertura |
| ------------------------------ | ------------------------------------------------------------ | --------- |
| `aurelio_normalized.db`        | 14 tabelas de domínio + 2 FTS5 (DDL em `data-dictionary.md`) | 🟢        |
| `_reversa_sdd/erd-complete.md` | Relacionamentos e cardinalidades                             | 🟢        |
