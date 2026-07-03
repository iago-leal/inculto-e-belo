# Gaps — inculto-e-belo

> Gerado pelo reversa-reviewer em 2026-07-03. Lacunas e suposições que permaneceram após a revisão.

## Permanecem (nenhuma crítica)

| #    | Item                                                                                             | Severidade                                                    | Onde está documentado                                              |
| ---- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------- | ------------------------------------------------------------------ |
| G-01 | Critério editorial exato de `entries.most_used` (🟡)                                             | Cosmético                                                     | `questions.md` Pergunta 1                                          |
| G-02 | Exclusividade `examples.definition_id` ⊕ `locution_definition_id` assumida sem CHECK no DDL (🟡) | Moderado (só se alguém escrever no banco, o que RB-10 proíbe) | `banco-lexical/design.md` §Riscos                                  |
| G-03 | Ligação textual `orthographic_marks.rule_code` → `orthographic_rules.rule` sem FK (🟡)           | Cosmético                                                     | `banco-lexical/design.md` §Riscos                                  |
| G-04 | Restauração de backup sem verificação automática de integridade (🟡 operacional)                 | Moderado                                                      | `governanca-operacional/tasks.md` T-03 (proposta de endurecimento) |

## Resolvidos nesta revisão

| Lacuna original                       | Resolução                                                                          | Evidência             |
| ------------------------------------- | ---------------------------------------------------------------------------------- | --------------------- |
| `flexions.type` 1–5                   | 🟢 plural/feminino/fem. plural/diminutivo/aumentativo                              | amostragem por tipo   |
| `entries.head_type` 1–4               | 🟢 palavra/símbolo/afixo/locução estrangeira                                       | amostragem por tipo   |
| `conjugations.tense` 1–13             | 🟢 mapa completo dos tempos                                                        | paradigma de "cantar" |
| Formas anômalas nas tabelas de formas | 🟢 zero vazias; fenômeno real são separadores `,` e `" ou "` em `flexions` (RB-14) | contagens LIKE        |

## Divergências documentais (fora do alcance do Reversa — regra non-destructive)

- README lista 8 das 14 tabelas de domínio (DT-01). Correção pertence ao mantenedor; sugerida no relatório final.
