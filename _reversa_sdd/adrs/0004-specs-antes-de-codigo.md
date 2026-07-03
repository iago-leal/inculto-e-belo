# ADR-0004 — Especificação completa (Reversa greenfield) antes de qualquer código

> Retroativo, gerado pelo reversa-detective em 2026-07-03. Status: **aceita** (em vigor). Confidência: 🟢 (commits c690b10 e ed1c173; `_reversa_sdd/prd.md` e `sdd/*.md`)

## Contexto

A primeira aplicação sobre o léxico (dicionário StarDict para KOReader) nasceu sem código legado. O mantenedor intermitente precisa que as decisões sobrevivam às pausas — código sem spec vira arqueologia cara.

## Decisão

Rodar o pipeline `/reversa-new` até o fim antes de codar: brief → ideation → personas → PRD → 5 specs SDD (`ingestao-aurelio`, `conversao-formato`, `indice-de-flexoes`, `validacao-paridade`, `distribuicao-webdav`), com decisões pinadas em decision logs (PyGlossary 5.4.1; 100% das flexões do banco; banco somente-leitura; parser StarDict próprio em stdlib para a validação de paridade).

## Justificativa

- As decisões de maior risco (formato, ferramenta, alvo de cobertura) ficaram registradas com alternativas descartadas — retomáveis após meses.
- A decomposição em 5 componentes deu fronteiras de acoplamento antes da primeira linha de código.

## Consequências

- O ciclo forward (features) ancora cada requisito em spec — rastreabilidade de nascença.
- Custo pago adiantado: specs podem divergir da realidade conforme o código nascer; mitigado por re-extrações do Reversa e pela validação de paridade independente.
