# ADR-0003 — Governança de sessão via Harness com core no upstream

> Retroativo, gerado pelo reversa-detective em 2026-07-03. Status: **aceita** (em vigor). Confidência: 🟢 (commit 723ace6; shim `harness`; `harness.toml`)

## Contexto

O mantenedor opera dezenas de projetos com pausas longas; precisa de estado-da-sessão e registro de microdecisões retomáveis, sem duplicar o maquinário em cada repositório.

## Decisão

Instalar o Harness como shim bash de 15 linhas que resolve `upstream_path` em `harness.toml` e executa o core Python que vive em `~/dev/harness` (fonte única). Estado local em `.harness/` (estado-da-sessao.md, microdecisoes.md).

## Justificativa

- Zero duplicação de core entre projetos; atualizações num lugar só.
- Falha barulhenta se o upstream sumir (o shim valida e aborta com mensagem clara).

## Consequências

- Dependência de caminho absoluto do upstream: mover `~/dev/harness` quebra todos os shims (mitigado pelo erro claro).
- O encerramento de sessão grava commits `chore(sessao)` — o histórico git mistura trabalho e governança (aceito; facilita arqueologia, como esta).
