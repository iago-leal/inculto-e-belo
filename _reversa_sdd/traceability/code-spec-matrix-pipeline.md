# Code/Spec Matrix, código das features 001 a 003

> Gerado pelo reversa-writer em 2026-10-15 (re-extração). Complementa `code-spec-matrix.md` (2026-07-03), que continua válida para o banco e a governança e foi preservada sem alteração. Juntas, as duas matrizes cobrem todo o legado versionado.

## Código de produção

| Arquivo do legado | Linhas | Unit correspondente | Spec greenfield de origem | Cobertura |
|-------------------|--------|---------------------|---------------------------|-----------|
| `pipeline/src/aurelio_pipeline/__init__.py` | 11 | `pipeline-nucleo/` | n/a | 🟡 docstring desatualizado |
| `pipeline/src/aurelio_pipeline/cli.py` | 304 | `pipeline-nucleo/` (orquestração), `pipeline-koreader/` (`_alvo_koreader`), `pipeline-readest/` (`_alvo_readest`) | `sdd/conversao-formato.md` | 🟢 |
| `pipeline/src/aurelio_pipeline/erros.py` | 69 | `pipeline-nucleo/` | todas | 🟢 |
| `pipeline/src/aurelio_pipeline/dominio/modelos.py` | 170 | `pipeline-nucleo/`, `pipeline-readest/` | todas | 🟢 |
| `pipeline/src/aurelio_pipeline/dominio/indice_flexoes.py` | 89 | `pipeline-nucleo/` | `sdd/indice-de-flexoes.md` | 🟢 |
| `pipeline/src/aurelio_pipeline/dominio/renderizacao.py` | 127 | `pipeline-nucleo/` | `sdd/conversao-formato.md` | 🟢 |
| `pipeline/src/aurelio_pipeline/dominio/agrupamento_readest.py` | 133 | `pipeline-readest/` | n/a (feature 003) | 🟢 |
| `pipeline/src/aurelio_pipeline/infra/repositorio.py` | 391 | `pipeline-nucleo/` | `sdd/ingestao-aurelio.md` | 🟢 |
| `pipeline/src/aurelio_pipeline/infra/escrita_stardict.py` | 128 | `pipeline-koreader/` | `sdd/conversao-formato.md` | 🟢 |
| `pipeline/src/aurelio_pipeline/infra/escrita_readest.py` | 245 | `pipeline-readest/` | n/a (feature 003) | 🟢 |
| `pipeline/src/aurelio_pipeline/infra/conferencia_readest.py` | 284 | `pipeline-readest/` | n/a (feature 003) | 🟢 |
| `pipeline/src/aurelio_pipeline/validacao/leitor_stardict.py` | 112 | `pipeline-koreader/` (reaproveitado por `pipeline-readest/`) | `sdd/validacao-paridade.md` | 🟢 |
| `pipeline/src/aurelio_pipeline/validacao/paridade.py` | 186 | `pipeline-koreader/` | `sdd/validacao-paridade.md` | 🟢 |
| `pipeline/src/aurelio_pipeline/validacao/paridade_readest.py` | 294 | `pipeline-readest/` | n/a (feature 003) | 🟢 |
| `pipeline/conferencia_readest/conferir.ts` | 111 | `pipeline-readest/` (`contracts.md` §3) | n/a (feature 003) | 🟢 |
| `pipeline/conferencia_readest/fonte-readest.json` | 36 | `pipeline-readest/` (`contracts.md` §4) | n/a (feature 003) | 🟢 |
| `pipeline/conferencia_readest/package.json`, `package-lock.json` | 31 | `pipeline-readest/` | n/a (feature 003) | 🟢 |
| `pipeline/src/aurelio_pipeline/{dominio,infra,validacao}/__init__.py` | 0 | `pipeline-nucleo/` (marcadores de pacote, vazios) | n/a | 🟢 |
| `spike/001-flexoes/gerar_spike.py` | 428 | `spike-001-flexoes/` | `sdd/indice-de-flexoes.md` | 🟢 |

## Configuração e runbooks

| Arquivo do legado | Unit correspondente | Cobertura |
|-------------------|---------------------|-----------|
| `pipeline/manifesto-integridade.json` | `pipeline-nucleo/` (RB-15), `governanca-operacional/decisions.md` (G-02) | 🟢 |
| `pipeline/pyproject.toml`, `pipeline/uv.lock` | `pipeline-nucleo/` (pré-requisitos) | 🟢 |
| `pipeline/README.md` | `governanca-operacional/decisions.md` (G-05) | 🟢 |
| `spike/001-flexoes/pyproject.toml`, `uv.lock`, `README.md` | `spike-001-flexoes/` | 🟢 |
| `harness.toml` (`[regen]`) | `governanca-operacional/decisions.md` (G-01), `pipeline-nucleo/contracts.md` | 🟢 |
| `.gitignore` (blocos das features) | `governanca-operacional/decisions.md` (G-03, G-04) | 🟢 |
| `README.md` (seção do pipeline) | `governanca-operacional/decisions.md` (G-06) | 🟢 |

## Testes

| Arquivo | Unit | Cobertura |
|---------|------|-----------|
| `pipeline/tests/conftest.py` | `pipeline-nucleo/` (banco sintético com o mini-schema real) | 🟢 |
| `pipeline/tests/test_repositorio.py` | `pipeline-nucleo/` TT-01 | 🟢 |
| `pipeline/tests/test_indice_flexoes.py` | `pipeline-nucleo/` TT-02 | 🟢 |
| `pipeline/tests/test_renderizacao.py` | `pipeline-nucleo/` TT-03 | 🟢 |
| `pipeline/tests/test_validacao.py` | `pipeline-koreader/` TT-01 a TT-04 | 🟢 |
| `pipeline/tests/test_agrupamento_readest.py` | `pipeline-readest/` TT-01 | 🟢 |
| `pipeline/tests/test_escrita_readest.py` | `pipeline-readest/` TT-02 | 🟢 |
| `pipeline/tests/test_paridade_readest.py` | `pipeline-readest/` TT-03 | 🟢 |
| `pipeline/tests/test_conferencia_readest.py` | `pipeline-readest/` TT-04 e TT-05 | 🟢 |

## Fora do escopo de spec

| Caminho | Motivo |
|---------|--------|
| `dist/`, `spike/*/dist/` | Artefatos derivados, fora do git (RB-11) |
| `pipeline/conferencia_readest/.cache/`, `node_modules/` | Código de terceiros e dependências regeneráveis, fora do git |
| `_reversa_forward/001…003/*` | Artefatos do ciclo forward |

## Cobertura estimada

**100% do código versionado das features 001 a 003** (22 arquivos de código e da conferência, três deles marcadores de pacote vazios, 10 de configuração e runbook e 9 de teste) está mapeado a uma das units novas. A única ressalva 🟡 é o docstring de `__init__.py`.
