# banco-lexical, Tarefas de Implementação

> Gerado pelo reversa-writer em 2026-07-03. A unit já existe (o ativo está pronto); as tarefas abaixo são as de **reconstrução/reaproveitamento**: o que um agente precisa fazer para consumir ou regenerar a unit com fidelidade.

## Pré-requisitos

- [ ] SQLite 3 com FTS5 disponível no ambiente
- [ ] `aurelio_normalized.db` presente (ou restaurado: `rclone copy gdrive:inculto-e-belo/aurelio_normalized.db .`)
- [ ] `PRAGMA integrity_check` = ok

## Tarefas

- [ ] T-01, Implementar camada de leitura somente-leitura (`file:...?mode=ro`) com as consultas canônicas do `design.md` §Interface
  - Origem no legado: DDL do banco (`data-dictionary.md`)
  - Critério de pronto: verbete completo de `belo` montado na ordem editorial
  - Confiança: 🟢

- [ ] T-02, Implementar resolução forma→lema com tratamento de órfãs e ambíguas
  - Origem no legado: `flexions`/`conjugations` (RB-05)
  - Critério de pronto: as 22 órfãs conhecidas são detectadas e reportadas, não corrigidas
  - Confiança: 🟢

- [ ] T-03, Implementar auditoria de baseline: contagens de `domain.md` §4 conferidas após qualquer restauração/regeneração
  - Origem no legado: README §Proveniência
  - Critério de pronto: script/consulta devolve PASS com os totais atuais
  - Confiança: 🟢

- [ ] T-04, (Se regeneração da origem for necessária) Reexecutar a extração do `JailBrake Aurelio` via `sqlite3 .backup` e revalidar proveniência
  - Origem no legado: README §Proveniência; ADR-0001
  - Critério de pronto: `integrity_check` ok + baseline íntegra + backup reenviado ao Drive
  - Confiança: 🟡 (processo da origem fora deste repo)

## Tarefas de Teste

- [ ] TT-01, Happy path: forma conjugada resolve ao verbete esperado (Gherkin do `requirements.md`)
- [ ] TT-02, Caso de erro: forma órfã reportada sem escrita no banco
- [ ] TT-03, Busca FTS sem diacríticos encontra lema acentuado

## Tarefas de Migração de Dados

n/a — a unit é o dado; migrações são regenerações completas (T-04).

## Ordem Sugerida

1. T-01 (leitura) → T-02 (resolução) → TT-01..03; T-03 independe e pode rodar primeiro.
2. T-04 só em desastre ou atualização da origem.

## Lacunas Pendentes (🔴)

- Semântica de `flexions.type`, `entries.head_type`, mapa de `conjugations.tense` — ver `questions.md`.
