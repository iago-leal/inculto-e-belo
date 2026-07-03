# Relatório de Confiança — inculto-e-belo

> Gerado pelo reversa-reviewer em 2026-07-03

## Resumo Geral

Contagem de afirmações marcadas nos artefatos da extração (inventário, análise, domínio, arquitetura, units):

| Nível         | Quantidade | Percentual |
| ------------- | ---------- | ---------- |
| 🟢 CONFIRMADO | 118        | 84%        |
| 🟡 INFERIDO   | 21         | 15%        |
| 🔴 LACUNA     | 1          | 1%         |
| **Total**     | 140        | 100%       |

**Confiança geral: ~92%** (🟢 + metade dos 🟡)

A única 🔴 remanescente é cosmética (critério editorial de `most_used`, `questions.md` Pergunta 1). Nada bloqueia reimplementação ou o ciclo forward.

## Por Spec

| Spec                                                                                    | 🟢  | 🟡  | 🔴  | Confiança |
| --------------------------------------------------------------------------------------- | --- | --- | --- | --------- |
| `banco-lexical/` (requirements, design, tasks)                                          | 46  | 6   | 1   | ~92%      |
| `governanca-operacional/`                                                               | 22  | 4   | 0   | ~92%      |
| Transversais (inventory, code-analysis, data-dictionary, domain, architecture, C4, ERD) | 50  | 11  | 0   | ~91%      |

A confiança é alta porque o "código" é um schema SQLite lido diretamente: quase tudo é verificável por consulta, e o que era 🔴 foi resolvido por amostragem durante a própria revisão.

## Revisão Cruzada

Não realizada: o plugin do Codex não está disponível nesta sessão (`doc_level=completo` a tornaria opcional).

## Lacunas Pendentes 🔴

### banco-lexical

- **Critério editorial de `entries.most_used`** — só o material do app original responderia; pergunta opcional em `questions.md#pergunta-1`.

## Recomendações

- [ ] Feature `001-spike-de-flexoes`: incorporar **RB-14** (separadores `,` e `" ou "` em `flexions.flexion`, 1.364 linhas) ao mapeamento do `.syn` (ação T004) — sem isso, ~1.400 entradas do índice nasceriam inválidas.
- [ ] Mantenedor: atualizar o README para as 14 tabelas de domínio (DT-01) — fora do alcance do Reversa (non-destructive).
- [ ] Opcional: endurecer a restauração com verificação automática (G-04; `governanca-operacional/tasks.md` T-03).

## Histórico de Reclassificações

| De  | Para      | Afirmação                                                                            | Evidência                              |
| --- | --------- | ------------------------------------------------------------------------------------ | -------------------------------------- |
| 🔴  | 🟢        | `flexions.type`: 1=plural, 2=feminino, 3=fem. plural, 4=diminutivo, 5=aumentativo    | amostragem por tipo (6 exemplos/valor) |
| 🔴  | 🟢        | `entries.head_type`: 1=palavra, 2=símbolo/sigla, 3=afixo, 4=locução estrangeira      | amostragem por tipo                    |
| 🟡  | 🟢        | `conjugations.tense` 1–13 nomeados                                                   | paradigma completo de "cantar"         |
| —   | 🟢 (novo) | RB-14: múltiplas formas por linha em `flexions` (`,` e `" ou "`); zero formas vazias | `COUNT(*)` com LIKE nas duas tabelas   |
