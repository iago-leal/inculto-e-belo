# governanca-operacional

> Gerado pelo reversa-writer em 2026-07-03. Unit da extração reversa (granularity `module`).
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral

Camada fina que mantém o ativo de dados vivo e retomável: backup/restauração do `.db` (rclone ↔ Google Drive), exclusão estrutural do banco no git e governança de sessão via shim do Harness.

## Responsabilidades

- Garantir que o `.db` nunca entre no git e sempre tenha backup restaurável.
- Documentar a proveniência e o runbook de restauração (README).
- Delegar a governança de sessão ao core do Harness no upstream.

## Regras de Negócio

- RB-09 — Fonte de verdade é a cópia local; backup único em `gdrive:inculto-e-belo/`. 🟢
- RB-11 — Nada derivado do Aurélio é publicado (restrição de direitos autorais). 🟢
- RB-13 — Todo processo precisa ser retomável por README após meses de pausa. 🟡

## Requisitos Funcionais

| ID    | Requisito                                                                         | Prioridade | Critério de Aceite                                                     |
| ----- | --------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------- |
| RF-01 | Restaurar o banco num clone limpo com um comando (`rclone copy gdrive:... .`)     | Must       | Clone + restauração + `integrity_check` ok em < 10 min 🟢              |
| RF-02 | Reenviar backup após alteração do banco (`rclone copy ... gdrive: -P`)            | Must       | Arquivo no Drive com mtime/tamanho atualizados 🟢                      |
| RF-03 | Bloquear estruturalmente o versionamento de `*.db`/`*.sqlite` (+WAL/SHM)          | Must       | `git status` nunca lista o banco; `.gitignore` cobre as 6 extensões 🟢 |
| RF-04 | Delegar comandos de sessão ao core do Harness com falha clara se o upstream sumir | Should     | `./harness` sem upstream imprime erro e exit 1 🟢                      |

## Requisitos Não Funcionais

| Tipo             | Requisito inferido                                        | Evidência                | Confiança |
| ---------------- | --------------------------------------------------------- | ------------------------ | --------- |
| Disponibilidade  | Recuperação de desastre = Drive + runbook manual          | README §Onde mora o dado | 🟢        |
| Observabilidade  | Shim falha barulhento (stderr + exit 1)                   | `harness` linhas 8–11    | 🟢        |
| Manutenibilidade | Zero código duplicado do Harness (core único no upstream) | ADR-0003                 | 🟢        |

## Critérios de Aceitação

```gherkin
Dado um clone limpo do repositório sem o .db
Quando o mantenedor executa o comando de restauração do README
Então o banco chega íntegro (integrity_check ok) e as contagens-baseline conferem

Dado o upstream ~/dev/harness ausente ou movido
Quando ./harness é executado
Então o shim aborta com mensagem de erro clara e exit code 1
```

## Prioridade (MoSCoW)

| Requisito    | MoSCoW | Justificativa                                                       |
| ------------ | ------ | ------------------------------------------------------------------- |
| RF-01, RF-03 | Must   | Perda do dado ou vazamento público são os dois desastres do projeto |
| RF-02        | Must   | Sem reenvio, o backup diverge silenciosamente                       |
| RF-04        | Should | Governança; o dado não depende dele                                 |

## Rastreabilidade de Código

| Arquivo        | Elemento                   | Cobertura |
| -------------- | -------------------------- | --------- |
| `harness`      | shim completo              | 🟢        |
| `harness.toml` | config                     | 🟢        |
| `.gitignore`   | regras de exclusão         | 🟢        |
| `README.md`    | runbook backup/restauração | 🟢        |
