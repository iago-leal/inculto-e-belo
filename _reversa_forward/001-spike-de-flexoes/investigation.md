# Investigation: Spike de flexões — validação do lookup de formas no KOReader

> Identificador: `001-spike-de-flexoes`
> Data: `2026-07-03`
> Confidência: 🟢 CONFIRMADO (verificado no banco/fonte primária), 🟡 INFERIDO (conhecimento de fundo, a confirmar no spike), 🔴 LACUNA

## 1. A pergunta que o spike compra

O mecanismo `.syn` do StarDict é a via estabelecida para formas flexionadas, mas a literatura disponível não documenta o comportamento do KOReader com um `.syn` de ~1 milhão de entradas em hardware e-ink modesto. Não há benchmark publicado que responda OQ-01; a única forma barata de saber é medir no dispositivo real. Por isso o spike existe — e por isso ele precisa de índices em escala real, não de amostra.

## 2. Fatos verificados no banco (2026-07-03)

| Fato                                                | Valor                                                                                          | Como verificar                                                              |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| 🟢 Entries totais                                   | 143.376                                                                                        | `SELECT COUNT(*) FROM entries`                                              |
| 🟢 Lemas únicos (headwords após fusão de homônimos) | 137.784                                                                                        | `SELECT COUNT(DISTINCT lemma) FROM entries`                                 |
| 🟢 Formas em `flexions`                             | 175.259                                                                                        | `SELECT COUNT(*) FROM flexions`                                             |
| 🟢 Formas em `conjugations`                         | 869.119                                                                                        | `SELECT COUNT(*) FROM conjugations`                                         |
| 🟢 Colunas de junção                                | `flexions(entry_head, flexion)`, `conjugations(infinitive, conjugation)`, alvo `entries.lemma` | `.schema` das três tabelas                                                  |
| 🟢 Casamento forma→lema                             | 99,9% (12.535/12.546 infinitivos; 111.544/111.555 cabeças)                                     | levantamento da sessão de specs (`_reversa_sdd/sdd/indice-de-flexoes.md#2`) |

Consequência para o `.ifo` esperado: `wordcount = 137.784` e `synwordcount ≥ 900.000` (1.044.378 formas de entrada menos órfãs, duplicadas e idênticas ao headword — os números exatos saem do relatório JSON da geração).

## 3. Pesquisa de fundo

### 3.1 Mecânica do lookup StarDict no KOReader

- 🟡 O KOReader usa internamente o `sdcv` (StarDict console version) para consultar dicionários; o `.syn` é um índice paralelo ao `.idx` que aponta sinônimo → posição do artigo. A busca é binária sobre índice ordenado, o que em princípio escala em O(log n) — a dúvida de OQ-01 não é algorítmica, é o custo constante de I/O e parsing em e-ink modesto (CPU fraca, armazenamento lento).
- 🟡 Sobre normalização (OQ-02): o comportamento esperado do `sdcv`/KOReader inclui tentativas de fuzzy match e variações de caixa quando o match exato falha, mas o comportamento preciso com diacríticos e capitalização inicial não está documentado de forma confiável — é exatamente o que as 4 formas de teste do roteiro (2 com diacríticos, 2 capitalizadas) vão observar.
- Fontes: <https://github.com/koreader/koreader/wiki/Dictionary-support> (formato aceito, instalação); referência da spec sobre sinônimos como via para flexões (apêndice de `_reversa_sdd/sdd/indice-de-flexoes.md`).

### 3.2 PyGlossary 5.4.1 e o `.syn`

- 🟡 No modelo de dados do PyGlossary, cada entrada tem uma lista de palavras (`l_word`): a primeira é o headword, as demais são alternates. O writer StarDict materializa os alternates no `.syn` e preenche `synwordcount` no `.ifo`. É o mecanismo de D-05.
- 🟡 O writer StarDict ordena o índice conforme a regra do formato (comparação por `g_ascii_strcasecmp` e fallback binário) — motivo pelo qual a spec `conversao-formato` (RF-08) delega a ordenação à biblioteca em vez de reimplementar.
- 🟡 Modo de escrita (OQ-01 da `conversao-formato`): não se sabe, sem medir, se o caminho SQLite→glossário→StarDict do PyGlossary mantém o glossário inteiro em memória. Com corpo trivial o volume dominante são as ~1M strings do `.syn`; o `/usr/bin/time -l` (D-07) responde empiricamente.
- Fonte: <https://github.com/ilius/pyglossary> (release 5.4.1; documentação do formato StarDict no repositório).

### 3.3 Instalação no Boox Air 4C

- 🟡 KOReader lê dicionários de `koreader/data/dict/` no armazenamento do dispositivo; a UI (Configurações → Dicionário) permite conferir os dicionários detectados e ativar/desativar por livro. Transferência por USB/MTP é suficiente (D-09).
- 🟡 Para sessão fria (risco de cache): fechar e reabrir o KOReader antes do roteiro; a primeira consulta após abrir tende a pagar o custo de abertura dos índices — se houver discrepância perceptível entre 1ª consulta e seguintes, ambas entram anotadas no relatório.

## 4. Alternativas avaliadas (e descartadas) para o desenho do spike

| Alternativa                                               | Por que foi descartada                                                                                                                        |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Testar no emulador desktop do KOReader                    | Decisão do usuário (requirements §9): resultados de desktop não substituem o dispositivo; a pergunta é sobre e-ink modesto                    |
| Artefato com amostra de formas (ex.: 10k)                 | Falso GO garantido: a premissa em risco é justamente a escala do `.syn` (EC-05)                                                               |
| Corpo completo para todos os verbetes                     | Exigiria o renderizador de produção antes do gate — inversão da ordem do SDD; fixado em RF-01                                                 |
| Gerar flexões por Hunspell/MorphoBr para engordar o teste | NG-01 da spec `indice-de-flexoes`: a fonte única são as tabelas do banco                                                                      |
| Instrumentar a latência via log do KOReader               | Complexidade de setup (shell no dispositivo, parsing de log) desproporcional a um snippet; cronômetro + vídeo na faixa limítrofe atende RF-03 |

## 5. Padrões aplicáveis

- **Spike solution (XP):** código descartável para comprar informação; o entregável é o relatório, não o código. Reprodutibilidade mínima preservada por RN-04 (versionado + lock file).
- **Pré-registro de critério (RN-05):** o limiar GO/NO-GO e a escada de fallbacks foram fixados antes da medição, imunizando o veredito contra racionalização pós-hoc.
- **Falha barulhenta (EC-04):** forma vazia/anômala interrompe a geração com identificação do registro — princípio de observabilidade do mantenedor.

## 6. Lacunas que permanecem após esta investigação

| #       | Lacuna                                                                                             | Quem responde                                                                         |
| ------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| 🔴 L-01 | Latência real do lookup com `.syn` ~1M no Boox Air 4C                                              | O roteiro (RF-03/RF-04)                                                               |
| 🔴 L-02 | Normalização de caixa/diacríticos no lookup                                                        | As 4 formas de teste (RF-05)                                                          |
| 🔴 L-03 | Pico de memória e duração da geração                                                               | `/usr/bin/time -l` na execução (RF-07)                                                |
| 🔴 L-04 | Qualidade do HTML no popup e-ink (negrito, itálico, listas)                                        | Inspeção visual dos 20 verbetes completos (RF-08)                                     |
| 🔴 L-05 | Confirmação de que o PyGlossary 5.4.1 materializa `.syn` via alternates com `synwordcount` correto | Artefato-piloto de ~10 verbetes, primeira ação de codificação (premissa 1 do roadmap) |
