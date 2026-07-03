# inculto-e-belo

Dicionário da língua portuguesa em SQLite, base para trabalho de gramática
normativa. O nome vem do verso de Bilac (*"Última flor do Lácio, inculta e bela"*).

Repositório: <https://github.com/iago-leal/inculto-e-belo>

## O que é

Um único arquivo SQLite — `aurelio_normalized.db` (~189 MB) — com o léxico do
Aurélio normalizado a partir do app Android (projeto `JailBrake Aurelio`).

| Tabela         | Linhas  | Conteúdo                                  |
| -------------- | ------- | ----------------------------------------- |
| `entries`      | 143.376 | verbetes (lema, classe, etimologia, IPA)  |
| `definitions`  | 259.337 | acepções                                  |
| `conjugations` | 869.119 | conjugações verbais                       |
| `flexions`     | 175.259 | flexões                                   |
| `examples`     |  54.726 | exemplos de uso                           |
| `notes`        |  28.903 | notas                                     |
| `locutions`    |  22.168 | locuções                                  |
| `verb_rection` |   6.170 | regência verbal                           |

Há ainda tabelas FTS5 (`fts_entries`, `fts_definitions`) para busca textual.

## Onde mora o dado

O `.db` **não** é versionado no git (grande demais para o GitHub; ver `.gitignore`).
A fonte de verdade é a cópia local; o backup fica no Google Drive via rclone:

    gdrive:inculto-e-belo/aurelio_normalized.db

**Restaurar** a base num clone limpo:

    rclone copy gdrive:inculto-e-belo/aurelio_normalized.db .

**Reenviar** o backup após alterar a base:

    rclone copy aurelio_normalized.db gdrive:inculto-e-belo/ -P

## Como abrir

    sqlite3 aurelio_normalized.db
    sqlite> SELECT lemma, word_class_summary FROM entries WHERE lemma = 'belo';

## Proveniência

Importado em 2026-07-03 de
`~/dev/meus-projetos/JailBrake Aurelio/extraction/aurelio_normalized.db`
via `sqlite3 .backup` (cópia consistente, WAL já consolidado).
Integridade conferida (`PRAGMA integrity_check` → `ok`) e contagens validadas
contra a origem.
