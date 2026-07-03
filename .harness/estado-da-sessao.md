---
commit: 3c812924ff9981a0f7cf0b295ec8c47d1f889f15
feature: default_feature
start_time: '2026-07-03T19:29:17.206265+00:00'
status: inactive
---

## O que foi feito
- Executado o pipeline `/reversa-new` (time greenfield do Reversa) para a primeira aplicação do dicionário: tornar o Aurélio (SQLite, ~143k verbetes) acessível ao KOReader em múltiplos dispositivos.
- Três dos quatro agentes concluídos, com artefatos em `_reversa_sdd/`:
- Commitada também a instalação do framework Reversa (skills em `.claude/` e `.agents/`, `.reversa/`, `CLAUDE.md`, `AGENTS.md`), que estava pendente no working tree.

## Próximos passos
- Retomar com `/reversa-new` → opção 1 (continuar): falta só o **reversa-spec-sdd**, que decompõe o PRD em componentes e gera as specs SDD com score em `_reversa_sdd/sdd/`.
- Depois das specs: `/reversa-forward` para iniciar o ciclo requirements → plan → to-do → coding.
- Decisões adiadas para a fase de specs: formato-alvo do dicionário (StarDict vs. alternativas) e ferramenta de geração (PyGlossary vs. implementação própria), sob o filtro de longevidade.

## Pendências / bloqueios
- Pendências de cobertura do PRD: prazo (nenhum declarado); alvo quantitativo para cobertura de flexões; não-objetivo "editar conteúdo do banco" sem decisão explícita.
- Premissa de maior risco a validar cedo (spike): o KOReader encontrar palavras flexionadas no formato-alvo.

## Ponteiros
- Estado do pipeline: `.reversa/state.json#newproject_progress` (`stage: spec-sdd`, concluídos: ideator, researcher, drafter).
- Artefatos: `_reversa_sdd/{newproject-brief,ideation,personas,prd}.md` — todos selo 🟡 (planejado).
- Infra de distribuição citada nas personas: WebDAV da VPS do projeto `koreader-notas`.
