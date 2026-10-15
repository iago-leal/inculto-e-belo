# Inventário — inculto-e-belo

> Gerado pelo reversa-scout em 2026-10-15 (re-extração; a extração anterior é de 2026-07-03)
> Confidência: 🟢 CONFIRMADO (verificado em disco, no banco em modo somente-leitura e pela suíte de testes nesta execução)

## 1. Natureza do sistema

🟢 O projeto continua centrado num **ativo de dados**: o dicionário Aurélio normalizado num único arquivo SQLite de 198 MB (189 MiB), fora do git. Desde a extração anterior, porém, ganhou **código de aplicação** em Python: um pipeline de linha de comando que lê o banco em modo somente-leitura e produz dois artefatos StarDict derivados, de uso estritamente pessoal. O primeiro serve ao KOReader e o segundo ao Readest; cada um passa por um gate de validação antes de ser entregue. O pipeline nasceu das features 002 (build de produção, KOReader) e 003 (alvo Readest), precedidas por um spike descartável (feature 001) que validou a premissa do índice de flexões. A conferência do alvo Readest executa o código de busca do próprio Readest em Node.js, por subprocesso.

## 2. Estrutura de pastas

Exclui `.git`, `.reversa`, `_reversa_sdd`, `_reversa_forward`, `.claude`, `.agents`, `dist`, `node_modules`, `.cache`, `.venv`, `__pycache__` e caches de ferramentas (`.ruff_cache`, `.coverage`).

```
inculto-e-belo/
├── aurelio_normalized.db(-shm,-wal)  # o ativo: SQLite de 189 MiB, fora do git; backup via rclone
├── README.md                         # o que é (14 tabelas), onde mora o dado, como abrir, pipeline, proveniência
├── CLAUDE.md, AGENTS.md              # instruções do Reversa para agentes
├── harness, harness.toml             # shim do Harness + config (inclui [regen] do pipeline)
├── .gitignore                        # bancos, dist/, ambientes locais, cache da conferência
├── .harness/                         # estado de sessão e decisões (governança)
├── pipeline/                         # código de produção (features 002 e 003)
│   ├── pyproject.toml, uv.lock       # pacote aurelio-pipeline 1.0.0, dependências pinadas
│   ├── README.md                     # runbook: reprodução, KOReader, Readest, troubleshooting
│   ├── manifesto-integridade.json    # contagens esperadas por tabela (gate da ingestão)
│   ├── src/aurelio_pipeline/
│   │   ├── cli.py                    # entry point `aurelio-pipeline` (--alvo, --cobertura)
│   │   ├── erros.py                  # exceções nomeadas → exit code 2
│   │   ├── dominio/                  # domínio puro: modelos, índice de flexões, renderização, agrupamento Readest
│   │   ├── infra/                    # repositório SQLite, escritores StarDict (KOReader e Readest), conferência
│   │   └── validacao/                # leitor StarDict próprio, paridade KOReader, validação Readest
│   ├── conferencia_readest/          # conferir.ts + fonte-readest.json (commit fixado) + package(-lock).json
│   └── tests/                        # 8 módulos de teste + conftest (dados sintéticos)
└── spike/001-flexoes/                # spike descartável e reprodutível (feature 001)
    ├── gerar_spike.py, pyproject.toml, uv.lock, README.md
```

Arquivos versionados fora das pastas de meta-governança: **47** (eram 19).

## 3. Tecnologias

| Camada | Tecnologia | Evidência |
|--------|------------|-----------|
| Dados | SQLite 3 (WAL; FTS5) | `aurelio_normalized.db`; tabelas `fts_*` |
| Aplicação | Python ≥ 3.12 (27 arquivos `.py`, ~2.400 linhas de código-fonte e ~1.600 de testes) | `pipeline/pyproject.toml`, `spike/001-flexoes/pyproject.toml` |
| Conversão | PyGlossary 5.4.1 (alvo KOReader e spike) e escritor StarDict próprio (alvo Readest) | `pyproject.toml`; `infra/escrita_readest.py` |
| Compressão | python-idzip 0.3.9 (`.dict.dz` em blocos) | `pyproject.toml` |
| Conferência | Node.js ≥ 22.18 com TypeScript apagável nativo; `fflate` 0.8.3 | `conferencia_readest/fonte-readest.json`, `package.json` |
| Gerenciadores | uv (Python) e npm (Node) | `uv.lock`, `package-lock.json` |
| Scripts | Bash (shim `harness`) | `harness` |
| Documentação | Markdown (8 arquivos versionados fora de meta) | READMEs, `.harness/` |

Ambiente medido nesta execução: Python 3.14.7, uv 0.11.7, Node v26.10.0, npm 11.19.1.

## 4. Pontos de entrada

| Entrada | Tipo | Descrição |
|---------|------|-----------|
| `uv run aurelio-pipeline [--alvo koreader\|readest\|ambos] [--cobertura total\|flexions-somente]` | CLI | `pipeline/src/aurelio_pipeline/cli.py:main`; exit 0 aprovado, 2 erro nomeado, 3 reprovado |
| `./harness regen` | CLI | `[regen]` do `harness.toml`: `cd pipeline && uv run aurelio-pipeline` (só o alvo KOReader) |
| `node conferir.ts <artefato> <basename> <expectativa>` | Subprocesso | Chamado pelo pipeline na conferência do Readest; não é entrada do operador |
| `uv run python gerar_spike.py [--piloto]` | CLI | Spike 001, descartável e reprodutível |
| `sqlite3 aurelio_normalized.db` | CLI | Consulta ad hoc ao ativo |
| `rclone copy gdrive:inculto-e-belo/...` | Operacional | Restauração e backup do `.db` |

Sem CI/CD, Dockerfile, `.env` ou serviço de rede próprio.

## 5. Banco de dados (superfície)

🟢 Inalterado desde 2026-07-03 (mtime do arquivo e contagens do `manifesto-integridade.json` conferidos): 25 tabelas no `sqlite_master` (14 de domínio, 10 internas do FTS5 e `sqlite_sequence`), 18 índices, nenhuma view e nenhum trigger. Novidade de uso: `entries.most_used` passou a ser lida pelo pipeline (3.039 verbetes marcados).

| Tabela | Linhas |
|--------|--------|
| `entries` | 143.376 |
| `word_class_blocks` / `word_classes` | 168.361 / 302 |
| `definitions` | 259.337 |
| `rubrics` | 2.655 |
| `examples` / `notes` | 54.726 / 28.903 |
| `locutions` / `locution_definitions` | 22.168 / 24.034 |
| `verb_rection` | 6.170 |
| `flexions` / `conjugations` | 175.259 / 869.119 |

## 6. Cobertura de testes

🟢 pytest 8.4.1 e coverage 7.9.1. São 8 módulos de teste em `pipeline/tests/`, com dados sintéticos gerados no `conftest.py`, nunca com conteúdo do Aurélio. A suíte tem **145 testes, todos aprovados em 0,8 s** nesta execução. O marcador `integracao` roda o código real do Readest e é pulado sem Node ou sem cache. A cobertura medida na feature 003 vai de 96% a 100% em `dominio/` e de 91% a 98% em `validacao/`. O spike não tem testes, por ser descartável.

## 7. Proveniência e governança do dado

- 🟢 Importado em 2026-07-03 de `~/dev/meus-projetos/JailBrake Aurelio/extraction/aurelio_normalized.db` por `sqlite3 .backup`.
- 🟢 `.db`, `dist/`, ambientes locais e cache do código do Readest ficam fora do git (`.gitignore`).
- 🟢 Conteúdo sob direitos autorais: artefatos derivados de uso estritamente pessoal. Guardar o artefato do Readest na nuvem privada da conta do usuário não constitui publicação (RN-08 da feature 003).

## 8. Módulos identificados (para a Fase 2)

| Módulo | O que abrange | Evidência |
|--------|---------------|-----------|
| `banco-lexical` | Schema e conteúdo do SQLite | `aurelio_normalized.db` |
| `governanca-operacional` | Shim e config do Harness (com `[regen]`), backup e restauração, `.gitignore`, READMEs como runbook | `harness`, `harness.toml`, `README.md`, `.gitignore`, `pipeline/README.md` |
| `pipeline-nucleo` | CLI e orquestração, erros, modelos, ingestão com manifesto, índice de flexões e renderização de artigos, comuns aos dois alvos | `cli.py`, `erros.py`, `dominio/{modelos,indice_flexoes,renderizacao}.py`, `infra/repositorio.py`, `manifesto-integridade.json` |
| `pipeline-koreader` | Escrita StarDict via PyGlossary e validação de paridade com leitor próprio | `infra/escrita_stardict.py`, `validacao/{leitor_stardict,paridade}.py` |
| `pipeline-readest` | Agrupamento em página única, escritor StarDict próprio, validação independente e conferência com o código do Readest | `dominio/agrupamento_readest.py`, `infra/{escrita_readest,conferencia_readest}.py`, `validacao/paridade_readest.py`, `conferencia_readest/` |
| `spike-001-flexoes` | Gerador descartável que validou o `.syn` em escala real no KOReader | `spike/001-flexoes/` |
