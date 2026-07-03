# Code/Spec Matrix — inculto-e-belo

> Gerado pelo reversa-writer em 2026-07-03. Cobertura: arquivo do legado → unit que o especifica.

| Arquivo do legado                                                                                   | Unit correspondente                                                      | Cobertura |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | --------- |
| `aurelio_normalized.db` (14 tabelas + FTS5)                                                         | `banco-lexical/`                                                         | 🟢        |
| `aurelio_normalized.db-shm` / `-wal`                                                                | `banco-lexical/` (runtime WAL, sem spec própria)                         | 🟢        |
| `harness`                                                                                           | `governanca-operacional/`                                                | 🟢        |
| `harness.toml`                                                                                      | `governanca-operacional/`                                                | 🟢        |
| `.gitignore`                                                                                        | `governanca-operacional/`                                                | 🟢        |
| `README.md`                                                                                         | `governanca-operacional/` (runbook) + `banco-lexical/` (proveniência)    | 🟢        |
| `.harness/estado-da-sessao.md`, `.harness/microdecisoes.md`, `.harness/decisoes/`                   | `governanca-operacional/` (estado do core, documentado como dependência) | 🟡        |
| `CLAUDE.md`, `AGENTS.md`                                                                            | n/a — meta do próprio Reversa                                            | n/a       |
| `_reversa_forward/001-spike-de-flexoes/*`                                                           | n/a — artefatos do ciclo forward (não são legado)                        | n/a       |
| `_reversa_sdd/prd.md`, `_reversa_sdd/sdd/*.md`, `ideation.md`, `personas.md`, `newproject-brief.md` | n/a — specs greenfield pré-existentes (fonte, não alvo, desta extração)  | n/a       |

## Cobertura estimada

**100% dos arquivos do legado real** (ativo + operação) estão mapeados a uma das 2 units. Os `n/a` são artefatos de processo (Reversa/forward), deliberadamente fora do escopo de spec.

## Observações

- A pasta `_reversa_sdd/sdd/` (specs greenfield por componente do pipeline futuro) convive com as pastas de unit desta extração (`banco-lexical/`, `governanca-operacional/`) sem conflito: as primeiras descrevem o que será construído; as segundas, o que existe.
