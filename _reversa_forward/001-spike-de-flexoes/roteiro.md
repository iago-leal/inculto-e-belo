# Roteiro do spike — 20 palavras flexionadas

> Identificador: `001-spike-de-flexoes` · Gerado na execução de T002 (2026-07-03)
> Instrumento de medida de RF-02/RF-03. Preencher as colunas de resultado durante a execução no Boox Air 4C (onboarding.md §4).
> Regra da faixa limítrofe: latência cronometrada entre 0,8 s e 1,2 s obriga remedição por vídeo; o valor remedido é o que vale.
>
> **[2026-07-03] Execução no dispositivo dispensada por decisão do usuário** — as colunas de resultado abaixo ficam vazias de propósito. Evidência coletada em substituição: teste preparatório no KOReader do macOS via sdcv embutido, **20/20 formas resolvidas** ao(s) lema(s) esperado(s) (mediana 16 ms, informativa), ambíguas listando múltiplos destinos, C01/C02 resolvidas apenas pelo fallback fuzzy (modo exato não normaliza caixa/diacríticos). Detalhes: `spike-report.md` §2.2 e §3. Se o roteiro for executado no Boox no futuro (condição de monitoramento do veredito), preencher as tabelas abaixo normalmente.

## Nominais (10, de `flexions`)

| #   | Forma tocada | Lema(s) esperado(s)                                | Verbete abriu? (qual) | Latência (s) | Remedição vídeo? |
| --- | ------------ | -------------------------------------------------- | --------------------- | ------------ | ---------------- |
| N01 | árvores      | árvore                                             |                       |              |                  |
| N02 | belas        | bela **e** belo (ambígua — as duas devem aparecer) |                       |              |                  |
| N03 | corações     | coração (3 homônimos fundidos)                     |                       |              |                  |
| N04 | flores       | flor                                               |                       |              |                  |
| N05 | irmãs        | irmã                                               |                       |              |                  |
| N06 | mãos         | mão (3 homônimos fundidos)                         |                       |              |                  |
| N07 | olhos        | olho                                               |                       |              |                  |
| N08 | papéis       | papel (2 homônimos fundidos)                       |                       |              |                  |
| N09 | pães         | pão                                                |                       |              |                  |
| N10 | vozes        | voz                                                |                       |              |                  |

## Verbais (10, de `conjugations`)

| #   | Forma tocada | Lema(s) esperado(s)                             | Verbete abriu? (qual) | Latência (s) | Remedição vídeo? |
| --- | ------------ | ----------------------------------------------- | --------------------- | ------------ | ---------------- |
| V01 | amei         | amar                                            |                       |              |                  |
| V02 | cantávamos   | cantar                                          |                       |              |                  |
| V03 | disse        | dizer                                           |                       |              |                  |
| V04 | dormiu       | dormir                                          |                       |              |                  |
| V05 | estivéssemos | estar                                           |                       |              |                  |
| V06 | fôssemos     | ir **e** ser (ambígua — as duas devem aparecer) |                       |              |                  |
| V07 | poderia      | poder                                           |                       |              |                  |
| V08 | saberão      | saber                                           |                       |              |                  |
| V09 | trouxe       | trazer                                          |                       |              |                  |
| V10 | viu          | ver (2 homônimos fundidos)                      |                       |              |                  |

## Testes dirigidos de OQ-02 (caixa e diacríticos)

Cobertura exigida por RF-02: ≥ 2 formas com diacríticos (há 10: N01, N03, N05, N06, N08, N09, V02, V05, V06, V08) e ≥ 2 capitalizadas como início de frase:

| #   | Teste                      | Como executar                                                                      | Abriu? | Observação |
| --- | -------------------------- | ---------------------------------------------------------------------------------- | ------ | ---------- |
| C01 | **Árvores** (capitalizada) | Tocar a forma em início de frase, ou digitá-la capitalizada na busca do dicionário |        |            |
| C02 | **Disse** (capitalizada)   | Idem                                                                               |        |            |

## Condições de medição

- Sessão fria: KOReader fechado e reaberto antes da primeira palavra; anotar se a 1ª consulta divergir visivelmente das demais.
- Todas as formas acima estão gravadas em minúsculas no `.syn` (verificado no banco); os testes C01–C02 medem exatamente a normalização de caixa do KOReader.

## Apêndice — queries de seleção e validação (auditabilidade, D-08)

```sql
-- Validação das nominais (todas retornam a cabeça esperada; type 1=plural, 3=fem. plural):
SELECT flexion, entry_head, type FROM flexions
WHERE flexion IN ('árvores','belas','corações','flores','irmãs','mãos','olhos','papéis','pães','vozes');

-- Validação das verbais:
SELECT conjugation, infinitive, tense, person FROM conjugations
WHERE conjugation IN ('amei','cantávamos','disse','dormiu','estivéssemos','fôssemos','poderia','saberão','trouxe','viu');

-- Confirmação de que todos os lemas-alvo existem (com contagem de homônimos):
SELECT lemma, COUNT(*) FROM entries WHERE lemma IN
('árvore','bela','belo','coração','flor','irmã','mão','olho','papel','pão','voz',
 'amar','cantar','dizer','dormir','estar','ir','ser','poder','saber','trazer','ver')
GROUP BY lemma;
```

Critério de escolha: palavras de alta frequência literária; 2 ambíguas deliberadas (N02, V06) para observar o popup com múltiplos destinos; 3 lemas com homônimos fundidos (N03, N06, N08, V10) para validar a fusão; candidatas "cães" e "mulheres" descartadas por ausência em `flexions` (verificado em 2026-07-03).
