# Relatório de Confiança — inculto-e-belo

> Gerado pelo reversa-reviewer em 2026-07-03; refeito na re-extração de 2026-10-15, após as features 001, 002 e 003.

## Resumo Geral

Contagem das marcas de confiança nos artefatos da extração (units, histórias de usuário e transversais). Ficam fora da contagem as legendas da escala, os títulos «Lacunas Pendentes (🔴)» e as setas de reclassificação.

| Nível | Quantidade | Percentual |
|-------|-----------|------------|
| 🟢 CONFIRMADO | 489 | 88,1% |
| 🟡 INFERIDO | 66 | 11,9% |
| 🔴 LACUNA | 0 | 0% |
| **Total** | 555 | 100% |

**Confiança geral: 94%** (🟢 + metade dos 🟡). Em 2026-07-03 era cerca de 92%, sobre 140 marcas.

Nenhuma lacuna 🔴 bloqueia reimplementação ou o ciclo forward. As 🟡 concentram-se em três temas: o sentido editorial de `entries.most_used`, a latência no Boox (GO presumido) e o que ainda depende de verificação no aparelho ou de leitura humana.

## Por Spec

| Spec | 🟢 | 🟡 | 🔴 | Confiança |
|------|----|----|-----|-----------|
| `banco-lexical/` (preservada de 2026-07-03) | 32 | 4 | 0 | 94% |
| `governanca-operacional/` (preservada + `decisions.md` novo) | 32 | 8 | 0 | 90% |
| `pipeline-nucleo/` (nova) | 79 | 0 | 0 | 100% |
| `pipeline-koreader/` (nova) | 49 | 3 | 0 | 97% |
| `pipeline-readest/` (nova) | 91 | 4 | 0 | 98% |
| `spike-001-flexoes/` (nova) | 35 | 2 | 0 | 97% |
| `user-stories/` (2 preservadas + 2 novas) | 9 | 7 | 0 | 78% |
| Transversais (inventory, dependencies, code-analysis, data-dictionary, domain, state-machines, permissions, architecture, C4, ERD, flowcharts, ADRs, matrizes) | 162 | 38 | 0 | 90% |

A confiança das units do pipeline é alta porque cada afirmação foi conferida com o código, com os testes e com os relatórios do último build. As histórias de usuário ficam abaixo porque descrevem experiência no aparelho, que o código não prova.

## Revisão Cruzada

Não realizada: o plugin do Codex não está disponível nesta sessão.

## Revisão por unit

- As seis units têm os três arquivos canônicos; `pipeline-nucleo/` e `pipeline-readest/` têm também `contracts.md`, e `governanca-operacional/` ganhou `decisions.md`.
- `requirements.md`, `design.md` e `tasks.md` de cada unit nova são coerentes entre si; as tarefas cobrem todos os RF.
- As regras de negócio citadas nas units seguem a numeração de `domain.md` (RB-01 a RB-24); duas referências erradas do rascunho do Redator foram corrigidas antes da revisão.

## Revisão cruzada entre units

- Nenhuma contradição entre as units novas. A data do `.ifo` (build no KOReader, manifesto no Readest), os exit codes e a pré-verificação aparecem iguais em `pipeline-nucleo/`, `pipeline-koreader/` e `pipeline-readest/`.
- As units preservadas de 2026-07-03 tinham três afirmações vencidas pelo código; foram anotadas no lugar com «[Revisão 2026-10-15]» (ver Histórico).
- Units esperadas por `surface.json`: as seis existem. P-05 (`distribuicao-webdav`) segue planejado e sem unit, com spec greenfield em `sdd/distribuicao-webdav.md`.

## Validação das matrizes

- `traceability/code-spec-matrix.md` (2026-07-03) mais `traceability/code-spec-matrix-pipeline.md` (nova) cobrem 100% dos arquivos versionados fora das pastas de meta. A conferência foi feita com `git ls-files`; os três `__init__.py` vazios de subpacote, ausentes do rascunho, foram acrescentados.
- `traceability/spec-impact-matrix.md` reflete as dependências reais verificadas pelo Arquiteto (fronteiras por grep). Foi acrescentada a §4, que liga os IDs de componente às pastas de unit.

## Lacunas Pendentes 🔴

Nenhuma.

## Recomendações

- [ ] Mantenedor: mencionar o alvo Readest no `README.md` da raiz e atualizar o docstring de `pipeline/src/aurelio_pipeline/__init__.py` (fora do alcance do Reversa, non-destructive).
- [ ] Mantenedor: conferir no Readest o divisor `<hr>` no tema escuro e a chegada do dicionário ao iPhone pelo sync (O-05 da 003).
- [ ] Opcional: medir no Boox a abertura e a consulta do artefato de produção, o que transformaria o GO presumido da feature 001 em medido.
- [ ] Opcional: responder `questions.md` Pergunta 1 (`most_used`), que agora tem efeito na ordem das páginas do Readest.
- [ ] Próxima feature que toque o KOReader: avaliar a promoção condicionada, como no Readest (DT-07), para que um artefato reprovado não ocupe o lugar do aprovado.

## Histórico de Reclassificações

| Data | De | Para | Afirmação | Evidência |
|------|----|------|-----------|-----------|
| 2026-07-03 | 🔴 | 🟢 | `flexions.type`: 1=plural, 2=feminino, 3=fem. plural, 4=diminutivo, 5=aumentativo | Amostragem por tipo |
| 2026-07-03 | 🔴 | 🟢 | `entries.head_type`: 1=palavra, 2=símbolo/sigla, 3=afixo, 4=locução estrangeira | Amostragem por tipo |
| 2026-07-03 | 🟡 | 🟢 | `conjugations.tense` 1–13 nomeados | Paradigma completo de «cantar» |
| 2026-07-03 | — | 🟢 | RB-14: múltiplas formas por linha em `flexions` | `COUNT(*)` com LIKE |
| 2026-10-15 | 🔴 | 🟢 | Marca vencida em `banco-lexical/design.md` §Riscos sobre a semântica de `type`, `head_type` e `tense` | Já resolvida em 2026-07-03; `banco-lexical/questions.md` Q-01 a Q-03 |
| 2026-10-15 | 🟢 | 🟡 superada | `[regen]` reservado e comentado (`governanca-operacional/design.md`) | `harness.toml:16`, seção ativa |
| 2026-10-15 | 🟡 | 🟢 | Montagem do agregado com N+1 por verbete | `pipeline/src/aurelio_pipeline/infra/repositorio.py:266`–`:376` |
| 2026-10-15 | 🟡 | 🟢 | Docstring do pacote só com as camadas da 002 | `pipeline/src/aurelio_pipeline/__init__.py:1` |
| 2026-10-15 | 🟡 | 🟢 | Lógica do índice duplicada entre o spike e o pipeline | `spike/001-flexoes/gerar_spike.py:100`, `:112`; `dominio/indice_flexoes.py:20`, `:32` |
| 2026-10-15 | 🟢 | 🟢 corrigido | Tamanho do roteiro do spike: 22 lemas em `ROTEIRO_LEMAS`, e não 20 (o roteiro tem 20 palavras) | `spike/001-flexoes/gerar_spike.py:48` |
| 2026-10-15 | 🟡 | 🟡 anotado | Entrega no dispositivo «aguardando o pipeline» (`user-stories/consulta-de-palavra.md`) | O artefato existe desde a 002; a latência segue não medida |
