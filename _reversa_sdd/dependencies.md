# Dependências — inculto-e-belo

> Gerado pelo reversa-scout em 2026-07-03
> Confidência: 🟢 CONFIRMADO

## 1. Dependências de runtime do ativo

O projeto não tem manifesto de dependências (sem `package.json`, `requirements.txt`, `pyproject.toml` etc.). As dependências são ferramentas de sistema usadas operacionalmente:

| Ferramenta                   | Uso                                                                               | Versão exigida                         | Criticidade                                              |
| ---------------------------- | --------------------------------------------------------------------------------- | -------------------------------------- | -------------------------------------------------------- |
| SQLite 3 (CLI ou biblioteca) | Único meio de consultar o dado; FTS5 exigido para `fts_entries`/`fts_definitions` | Qualquer 3.x com FTS5 habilitado       | Alta — sem ele o ativo é ilegível                        |
| rclone                       | Backup/restauração do `.db` contra `gdrive:inculto-e-belo/`                       | Configuração local com remote `gdrive` | Alta para recuperação de desastre; nenhuma para consulta |
| git                          | Versionamento da camada de docs/meta (o `.db` fica fora)                          | —                                      | Média                                                    |
| Bash                         | Shim `harness`                                                                    | —                                      | Baixa — só governança de sessão                          |

## 2. Dependências externas de infraestrutura

| Recurso                                 | Papel                                                                 | Risco                                                                                      |
| --------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `~/dev/harness` (upstream do Harness)   | O shim `harness` executa `main.py` do core no upstream via venv de lá | Se o upstream mudar de caminho, o shim falha com erro claro (verificado no código do shim) |
| Google Drive (`gdrive:inculto-e-belo/`) | Único backup do ativo de 189 MB                                       | Perda do remote + perda local = perda total do dado                                        |

## 3. Dependências planejadas (ciclo forward, ainda não instaladas)

| Dependência                   | Onde está decidida                                        | Status                                                  |
| ----------------------------- | --------------------------------------------------------- | ------------------------------------------------------- |
| PyGlossary `==5.4.1` (pinada) | `_reversa_sdd/sdd/conversao-formato.md#15` (decision log) | 🟡 Planejada — entra com o spike `001-spike-de-flexoes` |
| uv (gerenciador Python)       | `_reversa_forward/001-spike-de-flexoes/roadmap.md` (D-06) | 🟡 Planejada                                            |

## 4. Sinais de dívida de dependência

Nenhum: não há lock file desatualizado nem biblioteca abandonada porque não há dependências declaradas. O ponto de atenção é operacional, não de biblioteca: o backup único no Drive (seção 2).
