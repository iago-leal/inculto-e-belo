# ADR-0005 — Spike em dispositivo real como gate do investimento no build completo

> Retroativo, gerado pelo reversa-detective em 2026-07-03. Status: **aceita** (em execução — feature `001-spike-de-flexoes`). Confidência: 🟢 (commit 32fee47; requirements.md da feature; OQ-01 da spec `indice-de-flexoes`)

## Contexto

A premissa de maior risco do produto é a latência do lookup no KOReader com um `.syn` de ~1 milhão de formas em e-ink modesto (Boox Air 4C). Nenhuma fonte externa responde isso; construir o pipeline inteiro para descobrir seria apostar o investimento na premissa não validada.

## Decisão

Antes do build completo, gerar artefato de spike com índices em escala real (todos os headwords + `.syn` completo, corpo trivial) e medir roteiro pré-registrado de 20 palavras no dispositivo, com critério de veredito imutável (RN-05: NO-GO se mediana ≥ 1 s ou qualquer palavra ≥ 3 s) e escada fixa de fallbacks (reduzir `.syn` → dois dicionários → reabrir formato).

## Justificativa

- Compra a informação mais cara primeiro, gastando o mínimo (padrão spike solution/XP).
- Critério pré-registrado imuniza o veredito contra racionalização pós-medição.
- As observações oportunistas (memória da geração, HTML no popup) respondem de graça as OQs da spec `conversao-formato`.

## Consequências

- Veredito GO destrava o build com as OQs de maior risco fechadas.
- Veredito NO-GO aciona fallbacks em ordem fixa antes de qualquer reabertura da decisão de formato.
- O código do spike é descartável, mas versionado e reprodutível (RN-04) — o veredito precisa sobreviver à regeneração do banco.
