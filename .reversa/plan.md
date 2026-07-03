# Plano de Exploração — inculto-e-belo

> Criado pelo Reversa em 2026-07-03
> Marque cada tarefa com ✅ quando concluída.
> Você pode editar este plano antes de iniciar: adicione, remova ou reordene tarefas conforme necessário.

---

## Fase 1: Reconhecimento 🔍

- [x] **Scout** — Mapeamento de estrutura de pastas e tecnologias ✅
- [x] **Scout** — Análise de dependências e gerenciadores de pacotes ✅
- [x] **Scout** — Identificação de entry points, CI/CD e configurações ✅

## Decisão de organização das specs 🗂️

> Entre o Scout e o Arqueólogo, o Reversa pergunta como você quer organizar as specs (por módulo, caso de uso, endpoint, híbrida, por features ou customizada). A escolha fica persistida em `.reversa/config.toml` na seção `[specs]` e não será reperguntada em execuções futuras. Para reapresentar o menu, remova manualmente a seção.

## Fase 2: Escavação 🏗️

> O Reversa preenche esta seção com os módulos reais após o Scout concluir o reconhecimento.

- [x] **Arqueólogo** — Análise do módulo `banco-lexical` (schema e conteúdo do SQLite) ✅
- [x] **Arqueólogo** — Análise do módulo `governanca-operacional` (shim harness, backup, gitignore) ✅

## Fase 3: Interpretação 🧠

- [x] **Detetive** — Arqueologia Git e ADRs retroativos ✅
- [x] **Detetive** — Regras de negócio implícitas e máquinas de estado ✅
- [x] **Detetive** — Matriz de permissões (RBAC/ACL) ✅
- [x] **Arquiteto** — Diagramas C4 (Contexto, Containers, Componentes) ✅
- [x] **Arquiteto** — ERD completo e integrações externas ✅
- [x] **Arquiteto** — Spec Impact Matrix ✅

## Fase 4: Geração 📝

- [x] **Redator** — Specs SDD por componente ✅ (units `banco-lexical/`, `governanca-operacional/`)
- [x] **Redator** — OpenAPI (se aplicável) ✅ (n/a — sem API)
- [x] **Redator** — User Stories (se aplicável) ✅ (consulta-de-palavra, retomada-fria)
- [x] **Redator** — Code/Spec Matrix ✅

## Fase 5: Revisão ✅

- [x] **Revisor** — Revisão cruzada de specs ✅ (Codex indisponível; revisão própria com amostragem no banco)
- [x] **Revisor** — Resolução de lacunas com o usuário ✅ (4 lacunas resolvidas por amostragem; 1 pergunta opcional em questions.md)
- [x] **Revisor** — Relatório de confiança final ✅ (~92%)

---

## Agentes Independentes

> Execute estes agentes quando os recursos estiverem disponíveis — podem rodar em qualquer fase.

- [x] **Visor** — Análise de interface via screenshots ✅ (n/a — sem UI/screenshots)
- [x] **Data Master** — Análise completa do banco de dados ✅ (absorvida: DDL completo, contagens, enums e ERD em `data-dictionary.md` + `erd-complete.md`)
- [x] **Design System** — Extração de tokens de design ✅ (n/a — sem CSS/temas)
- [x] **Tracer** — Análise dinâmica (requer sistema acessível) ✅ (n/a — não instalado; sistema é arquivo estático)

---

## Próximo passo

Após o Time de Descoberta concluir e o `_reversa_sdd/` estar populado, você pode disparar um dos fluxos seguintes:

- `/reversa-migrate`: orquestrador do **Time de Migração** (Paradigm Advisor → Curator → Strategist → Designer → Screen Translator → Inspector). Gera as specs do sistema novo. Saída em `_reversa_sdd/migration/` e `_reversa_sdd/screens/`.
- `/reversa-reconstructor`: gera plano bottom-up para reimplementar o software a partir das specs do legado (uma tarefa por sessão).
