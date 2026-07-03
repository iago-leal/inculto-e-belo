# governanca-operacional, Design Técnico

> Gerado pelo reversa-writer em 2026-07-03. 🟢 salvo indicação.

## Interface

| Símbolo                                                       | Assinatura           | Retorno                                     | Observação                                          |
| ------------------------------------------------------------- | -------------------- | ------------------------------------------- | --------------------------------------------------- |
| `./harness <args...>`                                         | repassa `$@` ao core | exit code do core; ou 1 se upstream ausente | resolve `upstream_path` de `harness.toml` via `sed` |
| `rclone copy gdrive:inculto-e-belo/aurelio_normalized.db .`   | restauração          | arquivo local                               | runbook README                                      |
| `rclone copy aurelio_normalized.db gdrive:inculto-e-belo/ -P` | backup               | progresso no stdout                         | runbook README                                      |

## Fluxo Principal (shim)

1. Resolve o próprio diretório e faz `cd` nele (`harness:3-4`).
2. Extrai `upstream_path` de `harness.toml` por `sed` (`harness:5`).
3. Valida existência de `main.py` e do venv Python do core (`harness:6-8`).
4. `exec` do core com os argumentos originais (`harness:12`).

## Fluxos Alternativos

- **Upstream ausente/movido:** mensagem em stderr + exit 1 (falha barulhenta, sem fallback).
- **Clone limpo sem `.db`:** qualquer consulta falha até o runbook de restauração ser executado; nenhuma automação mascara a ausência.

## Dependências

- `~/dev/harness` (core + venv) — caminho configurado, não hardcoded.
- rclone com remote `gdrive` configurado na máquina do mantenedor.

## Decisões de Design Identificadas

| Decisão                                                               | Evidência                       | Confiança |
| --------------------------------------------------------------------- | ------------------------------- | --------- |
| Shim mínimo com core único no upstream                                | `harness` (15 linhas); ADR-0003 | 🟢        |
| Backup fora do git por tamanho e direitos autorais                    | `.gitignore`; ADR-0002          | 🟢        |
| Seção `[regen]` reservada e comentada (sem artefatos derivados ainda) | `harness.toml`                  | 🟢        |

## Estado Interno

`.harness/estado-da-sessao.md` (narrativa de retomada) e `.harness/decisoes/` (microdecisões, índice vazio hoje) — escritos pelo core, não pelo shim.

## Observabilidade

stderr do shim; commits `chore(sessao)` no git como trilha de auditoria das sessões.

## Riscos e Lacunas

- 🟡 Restauração sem verificação automática de integridade (runbook manual; risco DT-03 do `architecture.md`).
- 🟡 Caminho absoluto do upstream: mover `~/dev/harness` quebra o shim em todos os projetos (mitigado pela falha clara).
