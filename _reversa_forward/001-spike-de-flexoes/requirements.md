# Requirements: Spike de flexões — validação do lookup de formas no KOReader

> Identificador: `001-spike-de-flexoes`
> Data: `2026-07-03`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Gerar um artefato StarDict de spike — todos os headwords no índice, corpo trivial, e índice `.syn` em escala real (~1 milhão de formas derivadas das tabelas `flexions` e `conjugations`) —, instalá-lo no Boox Air 4C com KOReader e executar um roteiro de 20 palavras flexionadas. O spike responde à premissa de maior risco do projeto (OQ-01 da spec `indice-de-flexoes`): o KOReader mantém latência aceitável de lookup com um `.syn` dessa magnitude? O resultado é um veredito GO/NO-GO que destrava (ou reabre) a decisão de formato antes de qualquer investimento no build completo.

## 2. Contexto a partir do legado

| Fonte                                                                       | Trecho relevante                                                                                                                                                             | Confidência |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `_reversa_sdd/sdd/indice-de-flexoes.md#14-open-questions`                   | OQ-01: latência do KOReader com `.syn` de ~1M de entradas em e-ink modesto (impacto alto); OQ-02: normalização de caixa/diacríticos no lookup do `.syn` (impacto médio)      | 🟡          |
| `_reversa_sdd/sdd/indice-de-flexoes.md#63-fluxos-alternativos`              | Fluxo Alternativo A: artefato mínimo + roteiro de 20 palavras em dispositivo real; positivo destrava o build, negativo reabre a decisão de formato                           | 🟡          |
| `_reversa_sdd/sdd/indice-de-flexoes.md#2-contexto-e-motivacao`              | Banco já contém as formas prontas: 175.259 em `flexions` + 869.119 em `conjugations`, com 99,9% de casamento com `entries.lemma` (levantamento de 2026-07-03)                | 🟢          |
| `_reversa_sdd/sdd/indice-de-flexoes.md#11-edge-cases-e-tratamento-de-erros` | EC-05: explosão de volume no `.syn` é cenário coberto pelo spike; o critério de fallback deve ser definido nele antes do build completo                                      | 🟡          |
| `_reversa_sdd/sdd/conversao-formato.md#15-decisoes-tomadas-decision-log`    | Ferramenta de geração decidida e pinada (2026-07-03); formato StarDict com `sametypesequence=h`; homônimos fundidos por lema                                                 | 🟢          |
| `_reversa_sdd/sdd/conversao-formato.md#14-open-questions`                   | OQ-01: modo de escrita da ferramenta (streaming vs. memória); OQ-02: subconjunto de HTML que o popup renderiza bem em e-ink — ambos com prazo "spike, antes do reversa-plan" | 🟡          |
| `_reversa_sdd/prd.md#8-riscos`                                              | Risco "KOReader não encontra palavras flexionadas" (impacto alto): mitigação é exatamente o protótipo de validação cedo, antes do pipeline completo                          | 🟡          |
| `_reversa_sdd/prd.md#6-restricoes`                                          | Conteúdo do Aurélio sob direitos autorais: uso estritamente pessoal, nenhum artefato distribuível publicamente                                                               | 🟢          |

## 3. Personas e cenários de uso

| Persona                | Objetivo                                                                             | Cenário-chave                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| iago-mantenedor-futuro | Provar (ou refutar) a premissa do `.syn` gastando o mínimo possível                  | Gera o artefato do spike, instala no Boox Air 4C, percorre o roteiro e registra o veredito no relatório |
| iago-leitor            | Confirmar que o toque em palavra flexionada abre o verbete certo em tempo de leitura | Toca "cantávamos" num livro real e o verbete "cantar" abre no popup em menos de 1 segundo               |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** O spike é gate do investimento: veredito GO destrava o build completo; veredito NO-GO aciona os fallbacks na ordem fixada em RN-05 antes de qualquer outra tarefa. 🟡
   - Origem no legado: `_reversa_sdd/sdd/indice-de-flexoes.md#13-plano-de-rollout`
   - Tipo: nova
2. **RN-02:** O banco `aurelio_normalized.db` é somente-leitura em todo o spike; formas órfãs são contadas e reportadas, jamais corrigidas. 🟢
   - Origem no legado: `_reversa_sdd/sdd/indice-de-flexoes.md#15-decisoes-tomadas-decision-log` (decisão do usuário, 2026-07-03)
   - Tipo: nova
3. **RN-03:** O artefato do spike herda a restrição de uso pessoal: instalação apenas em dispositivos do usuário, sem publicação em canal público. 🟢
   - Origem no legado: `_reversa_sdd/prd.md#6-restricoes`
   - Tipo: nova
4. **RN-04:** O código do spike é descartável, mas reprodutível: versionado no repositório com instruções de execução, para que o veredito possa ser reproduzido após regeneração do banco. 🟡
   - Origem no legado: `_reversa_sdd/prd.md#3-metricas-de-sucesso` (retomada fria guiada só pelo README)
   - Tipo: nova
5. **RN-05:** O critério de veredito é pré-registrado e imutável durante a execução: NO-GO quando a latência mediana das 20 palavras for ≥ 1 s ou qualquer palavra atingir ≥ 3 s (o acerto é fixo pela spec: 20 de 20 abrindo o verbete esperado). Em NO-GO, os fallbacks são avaliados na ordem: (1º) reduzir a cobertura do `.syn` e repetir o roteiro; (2º) dividir em dois dicionários (base + flexões); (3º) reabrir a decisão de formato. Cada degrau só é acionado se o anterior falhar. 🟢
   - Origem no legado: `_reversa_sdd/sdd/indice-de-flexoes.md#11-edge-cases-e-tratamento-de-erros` (EC-05 delega a definição ao spike); decisão do usuário em 2026-07-03
   - Tipo: nova

## 5. Requisitos Funcionais

| ID    | Requisito                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Prioridade | Critério de aceite                                                                                                                                             | Confidência |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | O spike deve gerar um artefato StarDict instalável (`.ifo`, `.idx`, `.dict.dz`, `.syn`) com índices em escala real: todos os 143.376 entries do banco representados como headwords (com a fusão de homônimos por lema definida na spec de conversão), corpo trivial (HTML de uma linha) exceto para os lemas-alvo do roteiro, que recebem verbete completo, e `.syn` com todas as formas válidas derivadas das 1.044.378 formas de entrada de `flexions` + `conjugations` (após descarte de órfãs, duplicadas e idênticas ao headword). | Must       | O `.ifo` gerado declara `wordcount` coerente com o total de lemas únicos do banco e `synwordcount` ≥ 900.000, e o artefato abre sem erro no KOReader.          | 🟢          |
| RF-02 | O spike deve documentar um roteiro fixo de 20 palavras flexionadas — 10 nominais e 10 verbais —, cada uma com o lema esperado, incluindo ao menos 2 formas com diacríticos e 2 formas capitalizadas como em início de frase.                                                                                                                                                                                                                                                                                                            | Must       | O roteiro existe como artefato versionado, com as 20 linhas (forma → lema esperado → resultado observado).                                                     | 🟡          |
| RF-03 | O usuário deve poder instalar o artefato no Boox Air 4C com KOReader e executar o roteiro completo, registrando por palavra: verbete aberto (sim/não, qual) e latência medida por cronômetro; medição que caia na faixa de 0,8 s a 1,2 s é refeita por gravação de vídeo antes de entrar no relatório.                                                                                                                                                                                                                                  | Must       | As 20 linhas do roteiro têm resultado preenchido após execução no dispositivo, e nenhuma latência registrada na faixa limítrofe carece da remedição por vídeo. | 🟢          |
| RF-04 | O spike deve responder OQ-01: registrar a latência do lookup (toque → popup com verbete) com o `.syn` em escala real e aplicar o critério pré-registrado de RN-05 (mediana < 1 s e todas as palavras < 3 s para GO).                                                                                                                                                                                                                                                                                                                    | Must       | O relatório contém a latência observada por palavra, a mediana calculada e a conclusão explícita sobre OQ-01 derivada do critério de RN-05.                    | 🟢          |
| RF-05 | O spike deve responder OQ-02: verificar se o lookup resolve formas capitalizadas e com diacríticos exatamente como gravadas no `.syn`, registrando o comportamento de normalização observado.                                                                                                                                                                                                                                                                                                                                           | Must       | O relatório contém a conclusão explícita sobre OQ-02, sustentada pelas 4 formas de teste do roteiro.                                                           | 🟡          |
| RF-06 | O spike deve produzir um relatório final (`spike-report.md` na pasta da feature) com: veredito GO/NO-GO pelo critério de RN-05, respostas às OQs endereçadas, dados brutos do roteiro e, em caso de NO-GO, o registro do acionamento do primeiro fallback da ordem de RN-05.                                                                                                                                                                                                                                                            | Must       | O relatório existe, o veredito é um dos dois valores permitidos e cada OQ endereçada tem resposta ou registro de inconclusividade.                             | 🟢          |
| RF-07 | O spike deve registrar, como observação oportunista, o comportamento de memória e tempo da geração do artefato (subsidia a OQ-01 da spec `conversao-formato`: streaming vs. memória).                                                                                                                                                                                                                                                                                                                                                   | Should     | O relatório contém pico de memória aproximado e duração da geração.                                                                                            | 🟡          |
| RF-08 | O spike deve registrar, como observação oportunista, a qualidade de renderização do HTML dos verbetes-alvo no popup do dispositivo (subsidia a OQ-02 da spec `conversao-formato`).                                                                                                                                                                                                                                                                                                                                                      | Should     | O relatório contém nota sobre negrito, itálico e listas no popup e-ink.                                                                                        | 🟡          |

## 6. Requisitos Não Funcionais

| Tipo              | Requisito                                                                                                           | Evidência ou justificativa                                                                    | Confidência |
| ----------------- | ------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ----------- |
| Desempenho        | Critério de veredito pré-registrado (RN-05): GO exige latência mediana < 1 s e nenhuma palavra ≥ 3 s no Boox Air 4C | `_reversa_sdd/prd.md#3-metricas-de-sucesso` (alvo de < 1 s); decisão do usuário em 2026-07-03 | 🟢          |
| Desempenho        | Geração do artefato do spike conclui em < 10 min no hardware do mantenedor                                          | Herdado de `_reversa_sdd/sdd/conversao-formato.md#7-requisitos-nao-funcionais` (RNF-01)       | 🟡          |
| Integridade       | Nenhuma escrita no banco de origem: o spike consome `aurelio_normalized.db` em modo somente-leitura                 | RN-02; decisão do usuário em 2026-07-03                                                       | 🟢          |
| Reprodutibilidade | Script do spike versionado, dependências pinadas em lock file, executável pelo README da feature                    | `_reversa_sdd/prd.md#4-escopo-in` (setup reproduzível)                                        | 🟡          |
| Observabilidade   | Falha barulhenta: forma vazia ou anômala nas tabelas de origem interrompe a geração com identificação do registro   | `_reversa_sdd/sdd/indice-de-flexoes.md#11-edge-cases-e-tratamento-de-erros` (EC-04)           | 🟡          |
| Segurança         | Artefato não sai do perímetro pessoal (dispositivos do usuário); nada publicado                                     | `_reversa_sdd/prd.md#6-restricoes`                                                            | 🟢          |

## 7. Critérios de Aceitação

```gherkin
Cenário: Roteiro completo com veredito GO
  Dado o artefato do spike instalado no Boox Air 4C com KOReader
  E o .syn contendo todas as formas válidas em escala real
  Quando o usuário toca cada uma das 20 palavras do roteiro em texto de leitura
  Então cada palavra abre o verbete do lema esperado
  E a latência mediana das 20 medições fica abaixo de 1 segundo
  E nenhuma medição individual atinge 3 segundos
  E o relatório do spike registra veredito GO com os dados brutos por palavra

Cenário: Forma capitalizada em início de frase
  Dado o artefato do spike instalado e uma forma do roteiro gravada em minúsculas no .syn
  Quando o usuário toca a mesma forma capitalizada como em início de frase
  Então o relatório registra se o verbete abriu ou não, respondendo OQ-02

Cenário: Medição na faixa limítrofe
  Dado uma palavra do roteiro cuja latência cronometrada caia entre 0,8 e 1,2 segundos
  Quando o resultado é registrado
  Então a medição é refeita por gravação de vídeo
  E o valor da remedição é o que entra no relatório

Cenário: Latência reprova a premissa (caso negativo)
  Dado o artefato do spike instalado com o .syn em escala real
  Quando a latência mediana atinge 1 segundo ou alguma palavra atinge 3 segundos
  Então o relatório registra veredito NO-GO
  E o primeiro fallback da ordem de RN-05 é acionado: reduzir a cobertura do .syn e repetir o roteiro
  E a decisão de formato da spec conversao-formato só é reaberta se os dois primeiros fallbacks falharem

Cenário: Observações oportunistas registradas
  Dado a geração do artefato do spike concluída e o roteiro executado no dispositivo
  Quando o relatório do spike é redigido
  Então ele registra pico de memória aproximado e duração da geração
  E registra nota sobre a renderização de negrito, itálico e listas no popup do dispositivo

Cenário: Registro anômalo no banco (caso negativo)
  Dado uma forma vazia ou composta apenas de espaços nas tabelas de origem
  Quando a geração do artefato do spike a encontra
  Então a geração falha com erro nomeado identificando o registro
  E nenhum artefato parcial é considerado válido para o roteiro
```

## 8. Prioridade MoSCoW

| Item                       | MoSCoW | Justificativa                                                                                                     |
| -------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------- |
| RF-01                      | Must   | Sem índices em escala real (`.idx` e `.syn`), o veredito valeria para um artefato que jamais existirá em produção |
| RF-02                      | Must   | O roteiro fixo é o instrumento de medida; sem ele o veredito vira impressão subjetiva                             |
| RF-03                      | Must   | A validação só vale em dispositivo real (OQ-01 fala de e-ink modesto; o Boox Air 4C é o alvo definido)            |
| RF-04                      | Must   | Responder OQ-01 é o objetivo primário do spike                                                                    |
| RF-05                      | Must   | OQ-02 afeta a cobertura real do lookup em texto corrente (frases começam capitalizadas)                           |
| RF-06                      | Must   | O relatório é o entregável que destrava ou bloqueia o restante do pipeline                                        |
| RF-07                      | Should | Observação oportunista: barata de coletar agora, evita spike adicional para a OQ-01 da conversão                  |
| RF-08                      | Should | Observação oportunista: idem, para o vocabulário HTML do renderizador                                             |
| RNF de desempenho (lookup) | Must   | É a própria pergunta do spike                                                                                     |
| RNF de reprodutibilidade   | Should | Spike é descartável, mas o veredito precisa ser reproduzível após regeneração do banco                            |

## 9. Esclarecimentos

### Sessão 2026-07-03

- **Q:** Em qual dispositivo o roteiro de 20 palavras será executado?
  **R:** Boox Air 4C com KOReader (decisão do usuário). O emulador desktop fica descartado como via principal; se usado em preparação, seus resultados não substituem os do dispositivo.
- **Q:** Qual o limiar de reprovação (NO-GO) para a latência?
  **R:** NO-GO se a latência mediana das 20 palavras for ≥ 1 s ou se qualquer palavra atingir ≥ 3 s. Racional: a mediana captura a experiência típica contra o alvo do PRD e o teto de 3 s captura o pior caso tolerável; um critério de palavra única seria frágil ao ruído de medição manual em e-ink. Registrado como RN-05.
- **Q:** Em caso de NO-GO, qual fallback avaliar primeiro?
  **R:** Ordem fixa: (1º) reduzir a cobertura do `.syn` e repetir o roteiro — menor raio de impacto, contido como política de filtragem no domínio do `indice-de-flexoes`; (2º) dois dicionários (base + flexões) — custa dívida operacional permanente; (3º) reabrir a decisão de formato — último recurso, invalida o decision log da `conversao-formato`. Registrado como RN-05.
- **Q:** Qual a composição do corpo do artefato do spike?
  **R:** Todos os 143.376 entries como headwords (com fusão de homônimos por lema) com conteúdo trivial de uma linha; verbete completo apenas para os lemas do roteiro. Racional: a latência depende do `.idx` e do `.syn` juntos; corpo mínimo geraria veredito sobre artefato irreal (falso GO), e corpo completo real exigiria construir o renderizador antes de a premissa estar validada, invertendo a ordem do SDD. Registrado em RF-01.
- **Q:** Como medir a latência do lookup?
  **R:** Cronômetro com registro por palavra; medição na faixa de 0,8 s a 1,2 s é refeita por gravação de vídeo (precisão extra só onde altera a decisão). Proporcional ao escopo de snippet do spike. Registrado em RF-03.

## 10. Lacunas

- Nenhuma lacuna aberta. As duas dúvidas da versão inicial (dispositivo-alvo e limiar de reprovação com plano B) foram resolvidas na sessão de esclarecimentos de 2026-07-03.

## 11. Histórico de alterações

| Data       | Alteração                                                                                                                 | Autor   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------- | ------- |
| 2026-07-03 | Versão inicial gerada por `/reversa-requirements`                                                                         | reversa |
| 2026-07-03 | Sessão de esclarecimentos: 5 respostas integradas, RN-05 criada, RF-01/RF-03/RF-04/RF-06 reescritos, 2 dúvidas resolvidas | reversa |
