# Spike report — 001-spike-de-flexoes

> Data: 2026-07-03 · Autor: reversa (execução) + iago (decisões)
> Feature: `_reversa_forward/001-spike-de-flexoes/` · Artefato: `spike/001-flexoes/dist/aurelio-spike/`

## 1. Veredito

**GO presumido — por decisão do usuário (2026-07-03), sem medição no dispositivo.**

O critério pré-registrado de RN-05 (NO-GO se mediana ≥ 1 s ou qualquer palavra ≥ 3 s, medido no Boox Air 4C) **não foi aplicado como pré-registrado**: após o teste preparatório completo no KOReader do macOS (20/20 formas resolvidas via o sdcv embutido do app), o usuário decidiu presumir o funcionamento no Boox e dispensar a execução de T009/T010 no dispositivo.

Consequências registradas:

- O risco residual é exatamente o que o desktop não mede: **custo de I/O e CPU do e-ink** na busca binária sobre `.syn` de 12,3 MB. Mediana de 16 ms no Mac; uma degradação de ~60× ainda ficaria dentro do limiar de 1 s.
- **Condição de monitoramento (herda o §13 da spec `indice-de-flexoes`):** nas primeiras sessões de leitura reais no Boox, observar a latência do toque. Se a experiência violar o espírito de RN-05 (típico ≥ 1 s ou pior caso ≥ 3 s), a escada de fallbacks permanece válida e na ordem fixada: (1º) `--cobertura flexions-somente`, (2º) dois dicionários, (3º) reabrir a decisão de formato.

## 2. O que foi efetivamente medido

### 2.1 Geração do artefato (escala real, MacBook)

| Métrica                 | Valor                                        | Limite            | Situação                        |
| ----------------------- | -------------------------------------------- | ----------------- | ------------------------------- |
| Duração                 | 4,9 s                                        | < 10 min          | folga de ~120×                  |
| Pico de memória (RSS)   | 462 MB                                       | < 2 GB            | folga de ~4×                    |
| `wordcount`             | 137.784                                      | = lemas únicos    | exato                           |
| `synwordcount`          | 774.003                                      | ≥ 900.000 (RF-01) | **desvio documentado** — ver §4 |
| Órfãs                   | 22 lemas (748 formas)                        | ≈ 22              | exato                           |
| Invariante do relatório | 1.045.742 = 774.003 + 748 + 220.563 + 50.428 | fecha             | ✅                              |

### 2.2 Roteiro de 20 palavras (KOReader macOS, sdcv embutido — preparatório)

20/20 formas abriram o(s) verbete(s) esperado(s); dados completos no `progress.jsonl` e na nota de `actions.md`. Destaques:

- Ambíguas planejadas corretas: `belas` → bela + belo; `fôssemos` → ir + ser.
- Ambiguidades extras legítimas: `flores` → flor/florar/florir; `papéis` → papel + papéis (EC-03: forma que também é headword).
- Homônimos fundidos abrem artigo único (coração ×3, mão ×3, papel ×2, ver ×2).
- Latência desktop: mediana 16 ms, máx 35 ms — **informativa, não vale para RN-05**.

## 3. Respostas às Open Questions

| OQ                        | Pergunta                                                  | Resposta                                                                                                                                                                                                                                                                                                                                | Status                                                                    |
| ------------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `indice-de-flexoes` OQ-01 | KOReader mantém < 1 s com `.syn` de escala real em e-ink? | **Não medida no dispositivo** (dispensada por decisão do usuário). Evidência indireta favorável: busca binária resolve em 16 ms no desktop com o mesmo binário sdcv; margem de ~60× até o limiar                                                                                                                                        | 🟡 presumida GO; monitorar nas primeiras leituras                         |
| `indice-de-flexoes` OQ-02 | Lookup normaliza caixa/diacríticos?                       | **O modo exato NÃO normaliza nada** ("Árvores", "Disse", "cantavamos" → vazio). O resgate vem das variantes que o KOReader tenta em Lua e do fuzzy do sdcv ("Árvores"→árvore, "Disse"→dizer). Implicação de design: gravar formas em minúsculas como estão no banco é correto; não é preciso duplicar variantes capitalizadas no `.syn` | 🟢 respondida (mecânica); comportamento fino do fuzzy no e-ink a observar |
| `conversao-formato` OQ-01 | PyGlossary: streaming ou memória? Precisa de chunking?    | Em memória: 462 MB de pico com corpo trivial + 774 mil alternates. Projeção para corpo completo (259 mil acepções em HTML) segue confortável no limite de 2 GB; chunking desnecessário                                                                                                                                                  | 🟢 respondida                                                             |
| `conversao-formato` OQ-02 | Que HTML o popup renderiza bem?                           | No desktop: negrito, itálico, listas `<ul>/<li>`, `<small>` e cabeçalho "Adj. · S. m. · Interj." renderizam corretamente (verificação visual do usuário: "funcionou"). Renderização no e-ink do Boox fica para o monitoramento                                                                                                          | 🟡 respondida no desktop; e-ink pendente                                  |

## 4. Achados que alimentam o build completo

1. **Baseline real do `.syn`: 774.003 pares únicos válidos** — a estimativa de ≥ 900 mil (RF-01) ignorava ~220 mil repetições legítimas de forma superficial entre pessoas/tempos ("eu cantava"/"ele cantava"). As specs `indice-de-flexoes` e `conversao-formato` devem usar 774.003 como alvo de `synwordcount` (recalcular a cada regeneração do banco).
2. **RB-14 é obrigatório:** 1.364 linhas de `flexions.flexion` carregam múltiplas formas (`,` e `" ou "`); sem split, ~1.400 entradas do `.syn` nasceriam corrompidas.
3. **`python-idzip==0.3.9` é dependência de fato** para `.dict.dz` com PyGlossary 5.4.1 — sem ela o writer degrada silenciosamente para `.dict` sem compressão. Pinar no build de produção.
4. EC-04 nunca disparou: zero formas vazias no banco atual.
5. Fusão de homônimos (137.784 headwords de 143.376 entries) validada de ponta a ponta.

## 5. Desfecho (T013)

**Build completo destravado.** Próximo passo natural do produto: nova feature forward para o pipeline de produção (`ingestao-aurelio` → `indice-de-flexoes` → `conversao-formato` → `validacao-paridade`), herdando os achados do §4. A instalação manual no Boox (cópia USB de `dist/aurelio-spike/` para `koreader/data/dict/`) continua disponível a qualquer momento — e é, ao mesmo tempo, o gesto que cumpre a condição de monitoramento do §1.

## 6. Decision log da feature

| Data       | Decisão                                                                                               | Autor                         |
| ---------- | ----------------------------------------------------------------------------------------------------- | ----------------------------- |
| 2026-07-03 | Critério RN-05 pré-registrado (mediana < 1 s, máx < 3 s, no Boox)                                     | iago                          |
| 2026-07-03 | Desvio de RF-01 aceito: 774.003 = 100% dos pares válidos (900 mil era estimativa)                     | reversa (verificado no banco) |
| 2026-07-03 | **Medição no dispositivo dispensada; veredito GO presumido com monitoramento nas primeiras leituras** | iago                          |
