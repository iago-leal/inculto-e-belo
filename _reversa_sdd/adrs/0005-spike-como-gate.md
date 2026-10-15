# ADR-0005 — Spike em dispositivo real como gate do investimento no build completo

> Retroativo, gerado pelo reversa-detective em 2026-07-03; status revisto na re-extração de 2026-10-15. Status: **aceita e executada**. Veredito **GO presumido** por decisão do usuário, sem a medição pré-registrada no Boox (commit 7703eb7; `_reversa_forward/001-spike-de-flexoes/spike-report.md`). Confidência: 🟢 (commits 32fee47 e 7703eb7; requirements.md da feature; OQ-01 da spec `indice-de-flexoes`)

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

## Desfecho (re-extração de 2026-10-15)

O critério de RN-05 não foi aplicado como pré-registrado. O teste preparatório no KOReader do macOS resolveu 20 de 20 formas, e o usuário dispensou a medição no Boox, presumindo o GO. O build completo seguiu (ADR-0006) e herdou a condição de monitoramento da latência nas primeiras leituras, com o fallback `--cobertura flexions-somente` disponível na CLI de produção.
