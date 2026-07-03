# ADR-0002 — Banco fora do git; backup único no Google Drive via rclone

> Retroativo, gerado pelo reversa-detective em 2026-07-03. Status: **aceita** (em vigor). Confidência: 🟢 (commit f431607; `.gitignore`; README §Onde mora o dado)

## Contexto

O ativo de 189 MB excede o razoável para GitHub, e o conteúdo é protegido por direitos autorais (uso pessoal) — publicá-lo num repositório seria também um risco legal.

## Decisão

`.gitignore` exclui `*.db`/`*.sqlite` (e WAL/SHM). A fonte de verdade é a cópia local; o backup vive em `gdrive:inculto-e-belo/` com comandos `rclone copy` documentados nos dois sentidos.

## Justificativa

- Mantém o repositório leve e publicável (só docs e meta).
- Blindagem legal: o conteúdo do Aurélio nunca transita por canal público.
- rclone é ferramenta madura e já configurada no ambiente do mantenedor.

## Consequências

- Clone limpo não funciona sem o passo de restauração (`rclone copy`) — documentado no README.
- Ponto único de falha para desastre: Drive + cópia local (risco aceito, registrado em `dependencies.md` §2).
- Qualquer artefato derivado herdará regra análoga (dist/ fora do git ou de canal público).
