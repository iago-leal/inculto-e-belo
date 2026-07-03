# Inventário — inculto-e-belo

> Gerado pelo reversa-scout em 2026-07-03
> Confidência: 🟢 CONFIRMADO (verificado em disco/banco nesta execução)

## 1. Natureza do sistema

🟢 Este projeto **não é uma aplicação com código-fonte**: é um **ativo de dados** — um dicionário da língua portuguesa (Aurélio normalizado) num único arquivo SQLite de ~189 MB — acompanhado de documentação operacional e da infraestrutura de governança de sessão (Harness) e de especificação (Reversa). Não há linguagem de programação de aplicação, build, CI ou testes: o "sistema legado" a documentar é o **schema e o conteúdo do banco**, mais os procedimentos operacionais do README.

## 2. Estrutura de pastas (excluindo `.git`, `.reversa`, `_reversa_sdd`, `.claude`, `.agents`)

```
inculto-e-belo/
├── aurelio_normalized.db        # o ativo: SQLite ~189 MB (fora do git; backup via rclone)
├── aurelio_normalized.db-shm    # arquivos WAL/SHM de runtime do SQLite
├── aurelio_normalized.db-wal
├── README.md                    # o que é, onde mora o dado, como restaurar/reenviar backup
├── CLAUDE.md                    # instruções do Reversa para agentes (gerado pelo installer)
├── AGENTS.md                    # idem, formato Agent Skills
├── harness                      # shim bash → core do Harness no upstream ~/dev/harness
├── harness.toml                 # config do Harness (state file, decisões)
├── .gitignore                   # allowlist: exclui *.db/*.sqlite (+WAL/SHM), .DS_Store, __pycache__
├── .harness/                    # estado de sessão e microdecisões (governança, não aplicação)
│   ├── estado-da-sessao.md
│   ├── microdecisoes.md
│   └── decisoes/_cabecalho.md
└── _reversa_forward/            # ciclo forward em andamento (feature 001-spike-de-flexoes)
    └── 001-spike-de-flexoes/    # requirements, roadmap, actions, investigation, ...
```

Total de arquivos fora das pastas de meta-governança: **19**.

## 3. Tecnologias

| Camada       | Tecnologia                  | Evidência                                                |
| ------------ | --------------------------- | -------------------------------------------------------- |
| Dados        | SQLite 3 (WAL mode; FTS5)   | `aurelio_normalized.db` + `-shm`/`-wal`; tabelas `fts_*` |
| Scripts      | Bash (1 arquivo, 15 linhas) | `harness` (shim que delega ao upstream)                  |
| Documentação | Markdown                    | `README.md`, `.harness/*.md`, `_reversa_forward/**`      |

Não há: `package.json`, `requirements.txt`, `pyproject.toml`, `Dockerfile`, CI/CD, arquivos `.env`, testes.

## 4. Pontos de entrada

| Entrada                                 | Tipo        | Descrição                                                                  |
| --------------------------------------- | ----------- | -------------------------------------------------------------------------- |
| `sqlite3 aurelio_normalized.db`         | CLI         | Único ponto de acesso ao dado (consultas ad-hoc; ver README §"Como abrir") |
| `./harness <cmd>`                       | CLI         | Governança de sessão (delega ao core em `~/dev/harness`); não toca o dado  |
| `rclone copy gdrive:inculto-e-belo/...` | Operacional | Restauração/backup do `.db` (README §"Onde mora o dado")                   |

## 5. Banco de dados (superfície; detalhe com o Data Master)

🟢 24 tabelas (14 de domínio + 10 internas FTS5/sequência), 18 índices, 0 views, 0 triggers.

### Tabelas de domínio com contagens verificadas

| Tabela                                      | Linhas            | Conteúdo                                                                         |
| ------------------------------------------- | ----------------- | -------------------------------------------------------------------------------- |
| `entries`                                   | 143.376           | verbetes (lema, slug, homônimo, classe, IPA, ortoépia, etimologia)               |
| `definitions`                               | 259.337           | acepções                                                                         |
| `conjugations`                              | 869.119           | conjugações verbais (infinitivo, tempo, pessoa, forma)                           |
| `flexions`                                  | 175.259           | flexões nominais (cabeça, forma, tipo, homônimo)                                 |
| `examples`                                  | 54.726            | exemplos de uso                                                                  |
| `notes`                                     | 28.903            | notas                                                                            |
| `locutions`                                 | 22.168            | locuções                                                                         |
| `locution_definitions`                      | —                 | definições das locuções (não citada no README)                                   |
| `verb_rection`                              | 6.170             | regência verbal                                                                  |
| `rubrics`                                   | —                 | rubricas das acepções (não citada no README)                                     |
| `word_classes` / `word_class_blocks`        | —                 | classes gramaticais e blocos por verbete (não citadas no README)                 |
| `orthographic_marks` / `orthographic_rules` | —                 | marcas e regras ortográficas (não citadas no README)                             |
| `fts_entries` / `fts_definitions`           | 143.376 / 259.337 | busca textual FTS5 (com tabelas internas `_config`, `_data`, `_docsize`, `_idx`) |

⚠️ O README lista apenas 8 tabelas de domínio; o banco tem 14. A divergência vai como observação para o Data Master e para `questions.md` se relevante.

## 6. Cobertura de testes

Nenhum framework de teste, nenhum arquivo `*.test.*`/`*.spec.*`. Coerente com a natureza de ativo de dados; a integridade é conferida por `PRAGMA integrity_check` e contagens contra a origem (README §"Proveniência").

## 7. Proveniência e governança do dado

- 🟢 Importado em 2026-07-03 de `~/dev/meus-projetos/JailBrake Aurelio/extraction/aurelio_normalized.db` via `sqlite3 .backup` (WAL consolidado, `integrity_check` ok).
- 🟢 O `.db` está fora do git (`.gitignore`); fonte de verdade local com backup em `gdrive:inculto-e-belo/` via rclone.
- 🟢 Conteúdo sob direitos autorais (Aurélio): uso estritamente pessoal — restrição registrada no PRD greenfield (`_reversa_sdd/prd.md#6-restricoes`).

## 8. Módulos identificados (para a Fase 2)

| Módulo                   | O que abrange                                                                                                             | Evidência                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `banco-lexical`          | Schema e conteúdo do SQLite: verbetes, acepções, flexões, conjugações, apoio (rubricas, classes, ortografia) e busca FTS5 | `aurelio_normalized.db`                              |
| `governanca-operacional` | Shim `harness` + `harness.toml`, procedimentos de backup/restauração do README, `.gitignore` allowlist                    | `harness`, `harness.toml`, `README.md`, `.gitignore` |
