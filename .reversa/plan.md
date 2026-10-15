# Plano de Exploração — inculto-e-belo (re-extração)

> Criado pelo Reversa em 2026-10-15, no modo autônomo, para a re-extração após as features 001, 002 e 003 do ciclo forward.
> O plano da extração anterior está em `.reversa/plan-extracao-2026-07-03.md`.
> Marque cada tarefa com ✅ quando concluída.

---

## Fase 1: Reconhecimento 🔍

- [x] **Scout** — Mapeamento de estrutura de pastas e tecnologias ✅
- [x] **Scout** — Análise de dependências e gerenciadores de pacotes ✅
- [x] **Scout** — Identificação de entry points, CI/CD e configurações ✅

## Decisão de organização das specs 🗂️

> Já decidida em `.reversa/config.toml`, seção `[specs]` (por módulo, `feature-folder`), e mantida nesta re-extração.

## Fase 2: Escavação 🏗️

- [x] **Arqueólogo** — Análise do módulo `banco-lexical` (schema e conteúdo do SQLite; conferência de inalteração) ✅
- [x] **Arqueólogo** — Análise do módulo `governanca-operacional` (Harness com `[regen]`, backup, `.gitignore`, READMEs como runbook) ✅
- [x] **Arqueólogo** — Análise do módulo `pipeline-nucleo` (CLI, erros, modelos, ingestão com manifesto, índice de flexões, renderização) ✅
- [x] **Arqueólogo** — Análise do módulo `pipeline-koreader` (escrita via PyGlossary, leitor próprio, paridade) ✅
- [x] **Arqueólogo** — Análise do módulo `pipeline-readest` (agrupamento, escritor próprio, validação, conferência em Node) ✅
- [x] **Arqueólogo** — Análise do módulo `spike-001-flexoes` (gerador descartável da feature 001) ✅

## Fase 3: Interpretação 🧠

- [x] **Detetive** — Arqueologia Git e ADRs retroativos ✅
- [x] **Detetive** — Regras de negócio implícitas e máquinas de estado ✅
- [x] **Detetive** — Matriz de permissões (RBAC/ACL) ✅
- [x] **Arquiteto** — Diagramas C4 (Contexto, Containers, Componentes) ✅
- [x] **Arquiteto** — ERD completo e integrações externas ✅
- [x] **Arquiteto** — Spec Impact Matrix ✅

## Fase 4: Geração 📝

- [x] **Redator** — Specs SDD por componente ✅
- [x] **Redator** — OpenAPI (se aplicável) ✅ n/a: sem API HTTP; contratos da CLI e da conferência em `contracts.md`
- [x] **Redator** — User Stories (se aplicável) ✅
- [x] **Redator** — Code/Spec Matrix ✅

## Fase 5: Revisão ✅

- [x] **Revisor** — Revisão cruzada de specs ✅ (sem Codex; revisão própria)
- [x] **Revisor** — Resolução de lacunas ✅
- [x] **Revisor** — Relatório de confiança final ✅

## Verificação de regressão semântica 🔁

- [x] **Reversa** — Watch items de `001-spike-de-flexoes`, `002-build-completo-de-producao` e `003-dicionario-readest`; adendos vigentes marcados como superados ✅ (17 🟢, 1 🟡, 0 🔴)

---

## Agentes Independentes

- [x] **Visor** — n/a, sem UI ✅
- [x] **Data Master** — absorvido pelo Arqueólogo (`data-dictionary.md`, `erd-complete.md`) ✅
- [x] **Design System** — n/a ✅
- [x] **Tracer** — n/a, não instalado ✅
