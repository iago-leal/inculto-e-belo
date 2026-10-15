# Gaps — inculto-e-belo

> Gerado pelo reversa-reviewer em 2026-07-03; refeito na re-extração de 2026-10-15. Lacunas e suposições que permaneceram após a revisão.

## Permanecem (nenhuma crítica)

| # | Item | Severidade | Onde está documentado |
|---|------|-----------|-----------------------|
| G-01 | Critério editorial exato de `entries.most_used` (🟡); agora ordena as páginas combinadas do Readest | Moderado (mudança de sentido altera a ordem sem erro) | `questions.md` Pergunta 1; `domain.md` L-04 |
| G-02 | Exclusividade `examples.definition_id` ⊕ `locution_definition_id` sem CHECK no DDL (🟡) | Cosmético (RB-10 proíbe escrita) | `banco-lexical/design.md` §Riscos |
| G-03 | Ligação textual `orthographic_marks.rule_code` → `orthographic_rules.rule` sem FK (🟡) | Cosmético | `banco-lexical/design.md` §Riscos |
| G-04 | Restauração do backup sem verificação automática; o primeiro build cumpre o papel na prática (🟡) | Cosmético (era moderado) | `governanca-operacional/decisions.md` §5 |
| G-05 | KOReader troca o artefato antes do veredito da paridade (DT-07) | Moderado | `pipeline-koreader/design.md` §Riscos |
| G-06 | Latência no Boox não medida; GO presumido na feature 001 | Moderado | ADR-0005; `pipeline-koreader/design.md` §Riscos |
| G-07 | Divisor `<hr>` no tema escuro do Readest e chegada ao iPhone sem conferência registrada | Cosmético | O-05 da 003; `user-stories/consulta-no-readest.md` |
| G-08 | README da raiz sem o alvo Readest; docstring do pacote só com a 002 | Cosmético (documental) | `governanca-operacional/decisions.md` §5 |
| G-09 | Units e histórias de 2026-07-03 preservadas pelo Redator, com trechos vencidos anotados no lugar | Cosmético | `governanca-operacional/decisions.md`; anotações «[Revisão 2026-10-15]» |

## Resolvidos desde 2026-07-03

| Lacuna original | Resolução | Evidência |
|-----------------|-----------|-----------|
| README lista 8 das 14 tabelas (DT-01) | Resolvida pela feature 001 | `README.md` da raiz |
| `[regen]` sem artefato derivado | Ativo desde a 002, só com o KOReader | `harness.toml:16` |
| Formato e entrega do dicionário | Pipeline com dois alvos e gates (002 e 003) | `pipeline-nucleo/`, `pipeline-koreader/`, `pipeline-readest/` |
| Marca 🔴 vencida em `banco-lexical/design.md` | Reclassificada para 🟢 | `banco-lexical/questions.md` Q-01 a Q-03 |
