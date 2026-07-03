# governanca-operacional, Tarefas de Implementação

> Gerado pelo reversa-writer em 2026-07-03. Tarefas para reproduzir a unit num ambiente novo ou endurecê-la.

## Pré-requisitos

- [ ] rclone instalado com remote `gdrive` autenticado
- [ ] Upstream do Harness disponível em `~/dev/harness` (ou caminho ajustado em `harness.toml`)

## Tarefas

- [ ] T-01, Reproduzir o runbook de restauração num clone limpo e cronometrar (< 10 min)
  - Origem no legado: `README.md` §Onde mora o dado
  - Critério de pronto: banco restaurado com `integrity_check` ok e baseline conferida
  - Confiança: 🟢

- [ ] T-02, Verificar cobertura do `.gitignore` contra os artefatos reais (db, shm, wal, sqlite)
  - Origem no legado: `.gitignore`
  - Critério de pronto: `git check-ignore` confirma as 6 extensões
  - Confiança: 🟢

- [ ] T-03, (Endurecimento, opcional) Adicionar verificação automática pós-restauração (integrity_check + contagens) ao runbook
  - Origem no legado: DT-03 (`architecture.md` §6)
  - Critério de pronto: um comando único devolve PASS/FAIL após restauração
  - Confiança: 🟡 (melhoria, não comportamento existente)

## Tarefas de Teste

- [ ] TT-01, Happy path: restauração completa num diretório temporário
- [ ] TT-02, Caso de erro: `./harness` com `upstream_path` inválido termina com exit 1 e mensagem clara

## Tarefas de Migração de Dados

n/a.

## Ordem Sugerida

1. T-02 (barato) → T-01 (valida o desastre-recuperação) → T-03 se aprovado pelo mantenedor.

## Lacunas Pendentes (🔴)

Nenhuma.
