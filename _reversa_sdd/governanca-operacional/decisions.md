# governanca-operacional, Delta da re-extração de 2026-10-15

> Gerado pelo reversa-writer em 2026-10-15. Arquivo novo: `requirements.md`, `design.md` e `tasks.md` desta unit são de 2026-07-03 e foram **preservados** pela diretiva non-destructive do Redator. Este arquivo registra o que mudou desde então; em conflito, ele prevalece sobre aqueles três.
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## 1. O que mudou desde 2026-07-03

| # | Mudança | Origem | Evidência | Confiança |
|---|---------|--------|-----------|-----------|
| G-01 | `[regen]` do Harness ativo, só com o alvo KOReader | Feature 002; D-19 da 003 | `harness.toml:16` (`command = "cd pipeline && uv run aurelio-pipeline"`) | 🟢 |
| G-02 | Manifesto de integridade versionado; banco mudado exige atualizá-lo em commit próprio | Feature 002 | `pipeline/manifesto-integridade.json`; `pipeline/README.md` «Quando o banco mudar» | 🟢 |
| G-03 | `.gitignore` ampliado para artefatos e ambientes do spike, do pipeline e da conferência | Features 001, 002 e 003 | `.gitignore` (blocos comentados por feature) | 🟢 |
| G-04 | Código de terceiros (Readest, AGPL-3.0) e `node_modules/` só em cache local | Feature 003 | `.gitignore`; `pipeline/conferencia_readest/fonte-readest.json` | 🟢 |
| G-05 | Runbooks novos: `pipeline/README.md` e `spike/001-flexoes/README.md` | Features 001 a 003 | Arquivos citados | 🟢 |
| G-06 | README da raiz lista as 14 tabelas e remete ao pipeline (DT-01 resolvida) | Feature 001 | `README.md:54` | 🟢 |
| G-07 | RB-11 com a ressalva da nuvem privada do Readest | Decisão do usuário em 2026-10-15 (RN-08 da 003) | ADR-0009 | 🟢 |

## 2. Regras de negócio que esta unit passa a guardar

- RB-09, RB-11 e RB-13, como antes, com RB-11 na redação nova de `domain.md`. 🟢
- RB-15: banco mudado exige commit próprio do manifesto; até lá, o build falha com exit 2. 🟢
- RB-17: o encerramento de sessão regenera só o KOReader, para não depender de Node nem de rede. 🟢

## 3. Requisitos funcionais acrescentados

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-05 | Regenerar o artefato do KOReader no encerramento de sessão | Should | `[regen]` roda o pipeline com o alvo padrão em cerca de 12 s; falha barulhenta sem o `.db` 🟢 |
| RF-06 | Atualizar o manifesto deliberadamente quando o banco mudar | Must | Commit próprio do `manifesto-integridade.json`; sem ele, `ContagemDivergenteError` 🟢 |
| RF-07 | Manter fora do git todo artefato derivado do Aurélio e todo código de terceiros baixado | Must | `git check-ignore` cobre `dist/`, `spike/*/dist/`, `.cache/` e `node_modules/` da conferência 🟢 |
| RF-08 | Runbook retomável para cada processo novo | Should | Reprodução, números esperados, exit codes e troubleshooting em `pipeline/README.md` 🟢 |

## 4. Exclusões do `.gitignore` (estado atual)

| Bloco | Padrões |
|-------|---------|
| Bancos | `*.db`, `*.db-shm`, `*.db-wal`, `*.sqlite`, `*.sqlite-shm`, `*.sqlite-wal` |
| Sistema e editor | `.DS_Store`, `*.swp`, `.harness/sync-cache.json` |
| Python | `__pycache__/`, `*.pyc` |
| Spike (001) | `spike/*/dist/`, `spike/*/.venv/`, `spike/*/medicao-geracao.txt`, `spike/*/geracao-stdout.txt` |
| Build (002) | `dist/`, `pipeline/.venv/`, `pipeline/.coverage` |
| Conferência (003) | `pipeline/conferencia_readest/.cache/`, `pipeline/conferencia_readest/node_modules/` |

## 5. Pendências observadas

- 🟡 O README da raiz não menciona o alvo Readest; quem chega pela raiz só descobre o alvo novo ao abrir `pipeline/README.md`.
- 🟡 Continua sem verificação automática de integridade depois de restaurar o `.db`; na prática, o primeiro build cumpre esse papel, porque confere esquema e contagens.
- 🟡 O docstring de `pipeline/src/aurelio_pipeline/__init__.py` descreve só as camadas da feature 002.
