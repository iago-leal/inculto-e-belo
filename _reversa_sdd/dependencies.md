# Dependências — inculto-e-belo

> Gerado pelo reversa-scout em 2026-10-15 (re-extração)
> Confidência: 🟢 CONFIRMADO

## 1. Dependências declaradas

### Pipeline de produção (`pipeline/pyproject.toml`, travadas em `pipeline/uv.lock`)

| Pacote | Versão | Uso | Criticidade |
|--------|--------|-----|-------------|
| `pyglossary` | `==5.4.1` | Escrita StarDict do alvo KOReader (adaptador `infra/escrita_stardict.py`) | Alta para o KOReader; nenhuma para o Readest |
| `python-idzip` | `==0.3.9` | Compressão `.dict.dz` em blocos (dictzip) | Alta nos dois alvos |
| `pytest` (dev) | `==8.4.1` | Testes | Média |
| `coverage` (dev) | `==7.9.1` | Cobertura | Baixa |
| `hatchling` (build) | sem pino | Backend de build do pacote | Baixa |

Transitivas no `uv.lock`: `colorama` 0.4.6 (só Windows), `iniconfig` 2.3.0, `packaging` 26.2, `pluggy` 1.6.0, `pygments` 2.20.0.

### Conferência do Readest (`pipeline/conferencia_readest/package.json`, travada em `package-lock.json`)

| Pacote | Versão | Uso |
|--------|--------|-----|
| `fflate` | `0.8.3` | Descompressão usada pelo `dictZip.ts` do Readest e pela descompressão integral de referência |

Código de terceiros obtido em tempo de execução, não versionado: `stardictReader.ts` e `dictZip.ts` do repositório `readest/readest`, tag `v0.12.16`, commit `3cc39ad7a558e6612e1a8135058fbd6f3c90b3e3`. Os SHA-256 dos originais e dos reescritos estão fixados em `fonte-readest.json`. O código é AGPL-3.0 e fica só no cache local (`.cache/`, fora do git).

### Spike (`spike/001-flexoes/pyproject.toml`, `uv.lock`)

`pyglossary==5.4.1` e `python-idzip==0.3.9`, as mesmas do pipeline; `package = false`.

## 2. Ferramentas de sistema

| Ferramenta | Uso | Versão exigida | Criticidade |
|------------|-----|----------------|-------------|
| SQLite 3 com FTS5 | Ler o ativo | Qualquer 3.x | Alta |
| Python | Pipeline e spike | ≥ 3.12 | Alta |
| uv | Ambiente e execução | Compatível com `uv.lock` v1 | Alta |
| Node.js | Conferência do Readest (TypeScript apagável nativo, `openAsBlob`) | ≥ 22.18 (`node_minimo`) | Alta para o alvo Readest; nenhuma para o KOReader |
| npm | `npm ci` na primeira preparação da conferência | Acompanha o Node | Média |
| rclone | Backup e restauração do `.db` | Remote `gdrive` configurado | Alta para recuperação de desastre |
| git, Bash | Versionamento; shim `harness` | — | Média / baixa |

## 3. Dependências externas de infraestrutura

| Recurso | Papel | Risco |
|---------|-------|-------|
| Google Drive (`gdrive:inculto-e-belo/`) | Único backup do ativo | Perda do remote e da cópia local significa perda total |
| `~/dev/harness` (upstream do Harness) | Core executado pelo shim | Mudança de caminho quebra o shim com erro claro |
| GitHub (`raw.githubusercontent.com`) | Primeira obtenção do código do Readest | Sem rede na primeira vez, o alvo Readest para com exit 2; depois o cache dispensa a rede |
| Registro npm | `npm ci` na primeira preparação | Idem |
| Readest (nuvem da conta do usuário) | Sincronização do dicionário importado | Conta privada; não constitui publicação (RN-08 da 003) |

## 4. Sinais de dívida de dependência

- 🟢 Todas as dependências diretas são pinadas e travadas em lockfile.
- 🟡 O Node evolui depressa: o Node 26 já exigiu três reescritas mecânicas no código do Readest, e uma versão futura pode recusar outra construção. A mitigação existente é o hash dos arquivos reescritos.
- 🟡 O `hatchling` não é pinado, mas só atua no build do pacote; `uv run` usa o lock.
- 🟡 O `ruff` aparece em caches locais (`.ruff_cache/`), mas não está declarado como dependência; é ferramenta de uso avulso.
