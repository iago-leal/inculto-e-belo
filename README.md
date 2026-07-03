# inculto-e-belo

Dicionário da língua portuguesa em SQLite, base para trabalho de gramática
normativa. O nome vem do verso de Bilac (_"Última flor do Lácio, inculta e bela"_).

Repositório: <https://github.com/iago-leal/inculto-e-belo>

## O que é

Um único arquivo SQLite — `aurelio_normalized.db` (~189 MB) — com o léxico do
Aurélio normalizado a partir do app Android (projeto `JailBrake Aurelio`).

| Tabela                 | Linhas  | Conteúdo                                                        |
| ---------------------- | ------- | --------------------------------------------------------------- |
| `entries`              | 143.376 | verbetes (lema, homônimo, classe, etimologia, IPA)              |
| `word_class_blocks`    | 168.361 | blocos de classe gramatical por verbete (agrupam acepções)      |
| `definitions`          | 259.337 | acepções (pertencem a blocos, não direto ao verbete)            |
| `conjugations`         | 869.119 | conjugações verbais (13 tempos; liga ao lema por texto)         |
| `flexions`             | 175.259 | flexões nominais (pode haver várias formas por linha, `,`/`ou`) |
| `examples`             | 54.726  | exemplos de uso (`editor` ou `citation`)                        |
| `notes`                | 28.903  | notas (polimórficas: verbete ou acepção)                        |
| `locutions`            | 22.168  | locuções                                                        |
| `locution_definitions` | 24.034  | definições das locuções                                         |
| `verb_rection`         | 6.170   | regência verbal (fonte Luft)                                    |
| `rubrics`              | 2.655   | rubricas de domínio/registro das acepções                       |
| `word_classes`         | 302     | classes gramaticais (abreviação → nome por extenso)             |
| `orthographic_marks`   | 3.280   | grafias anteriores ao acordo ortográfico, por verbete           |
| `orthographic_rules`   | 15      | regras ortográficas explicativas                                |

Há ainda tabelas FTS5 (`fts_entries`, `fts_definitions`) para busca textual sem
diacríticos. Dicionário de dados completo (DDL comentado, enums resolvidos,
relações sem FK): `_reversa_sdd/data-dictionary.md`.

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
