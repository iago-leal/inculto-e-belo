# Roadmap: Spike de flexões — validação do lookup de formas no KOReader

> Identificador: `001-spike-de-flexoes`
> Data: `2026-07-03`
> Requirements: `_reversa_forward/001-spike-de-flexoes/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Um único script Python descartável-mas-reprodutível (categoria **Snippet/Script**, Princípio nº 4 do usuário) lê `aurelio_normalized.db` em modo somente-leitura e gera, via PyGlossary 5.4.1 pinado — a mesma ferramenta decidida para produção em `_reversa_sdd/sdd/conversao-formato.md#15-decisoes-tomadas-decision-log` —, um artefato StarDict com índices em escala real: 137.784 headwords (143.376 entries fundidos por lema), corpo trivial de uma linha, verbete completo apenas para os 20 lemas do roteiro, e `.syn` com todas as formas válidas derivadas de `flexions` + `conjugations` (~1M). O script aplica uma versão mínima das regras de descarte da spec `indice-de-flexoes` (órfã, duplicada, idêntica ao headword) e grava relatório JSON de cobertura. O artefato é instalado no Boox Air 4C com KOReader; o roteiro de 20 palavras é executado com cronômetro (remedição por vídeo na faixa 0,8–1,2 s) e o resultado entra em `spike-report.md` com veredito GO/NO-GO pelo critério pré-registrado de RN-05. O spike não constrói nenhum dos cinco componentes de produção: ele apenas compra a informação que destrava (ou reabre) o build completo.

## 2. Princípios aplicados

`.reversa/principles.md` não existe neste projeto (nenhum princípio formal registrado via `/reversa-principles`). Aplicam-se, como referência, os princípios globais do mantenedor (CLAUDE.md do usuário):

| Princípio                | Como a feature se relaciona                                                                                                    | Status   |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------ | -------- |
| Proporcionalidade (nº 4) | Spike declarado como Snippet/Script: sem camadas, sem suíte formal de testes; apenas encapsulamento básico, lock file e README | respeita |
| Estabilidade > novidade  | Ferramenta de geração é a mesma pinada para produção (PyGlossary 5.4.1), nada novo entra                                       | respeita |
| Erros barulhentos        | Forma vazia/anômala interrompe a geração com identificação do registro (EC-04 herdado)                                         | respeita |
| Setup reproduzível       | Dependência pinada em lock file; execução documentada em `onboarding.md` e no README do spike                                  | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                                                                                                                              | Justificativa                                                                                                                                                                              | Alternativas descartadas                                                                                                                                    | Confidência |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| D-01 | O código do spike vive em `spike/001-flexoes/` na raiz do repositório (pasta nova; nenhum arquivo pré-existente é tocado)                                                                                                                                                            | RN-04 exige código versionado e reprodutível; pasta própria isola o descartável do futuro código de produção                                                                               | Colocar em `_reversa_forward/` (artefatos de processo não são código); branch descartável sem merge (perderia a reprodutibilidade pós-regeneração do banco) | 🟢          |
| D-02 | Gerar o artefato com PyGlossary 5.4.1 pinado, formato StarDict `sametypesequence=h`, compressão dictzip — idêntico à decisão de produção                                                                                                                                             | O veredito só vale se o artefato do spike for gerado pelo mesmo caminho do artefato real; ferramenta divergente invalidaria a medição                                                      | Writer StarDict manual mínimo (divergiria da produção); artefato sem dictzip (formato diferente do alvo)                                                    | 🟢          |
| D-03 | Headwords em escala real com corpo trivial; verbete completo só para os 20 lemas do roteiro                                                                                                                                                                                          | Fixado em RF-01 após esclarecimento: a latência depende de `.idx` + `.syn` juntos; corpo mínimo demais geraria falso GO, corpo completo exigiria o renderizador antes da premissa validada | Corpo completo para os 143.376 entries; subconjunto de headwords                                                                                            | 🟢          |
| D-04 | O `.syn` do spike deriva de uma implementação mínima e inline das regras da spec `indice-de-flexoes` (descartes: órfã, duplicada, idêntica; ambíguas preservadas), sem criar o módulo de domínio de produção                                                                         | O spike precisa dos números reais de cobertura (`synwordcount` ≥ 900.000) mas não do componente testável de produção — construí-lo agora inverteria a ordem do SDD                         | Implementar já o componente `indice-de-flexoes` completo (investimento antes do gate); `.syn` sintético com formas fictícias (invalidaria OQ-01)            | 🟢          |
| D-05 | Sinônimos entram via chaves alternativas (`l_word`) das entradas do glossário PyGlossary, que materializa o `.syn` na escrita StarDict                                                                                                                                               | É o mecanismo documentado da biblioteca para sinônimos; evita pós-processamento manual do `.syn`                                                                                           | Escrever o `.syn` binário à mão após o build (duplicaria lógica que a ferramenta já tem)                                                                    | 🟡          |
| D-06 | Ambiente Python gerenciado por `uv` (`pyproject.toml` + `uv.lock` dentro de `spike/001-flexoes/`)                                                                                                                                                                                    | Lock file exigido pelo RNF de reprodutibilidade; `uv` já é padrão nos demais projetos Python do mantenedor                                                                                 | `requirements.txt` sem lock (não determinístico); Poetry (mais pesado que o escopo de snippet)                                                              | 🟡          |
| D-07 | Medição de memória e tempo da geração via `/usr/bin/time -l` (macOS), registrada no relatório                                                                                                                                                                                        | Responde RF-07 (OQ-01 da `conversao-formato`) sem instrumentar o código                                                                                                                    | Instrumentação com `tracemalloc`/`memory_profiler` (mede só o heap Python, subestima o RSS real; e é código a mais num snippet)                             | 🟢          |
| D-08 | As 20 palavras do roteiro são selecionadas por consulta ao banco (10 nominais de `flexions`, 10 verbais de `conjugations`), incluindo ≥ 2 formas com diacríticos e ≥ 2 registradas em minúsculas para o teste de capitalização; a seleção fica registrada com a query que a produziu | RF-02 exige roteiro fixo e verificável; a query versionada torna a escolha auditável e reprodutível                                                                                        | Escolha manual sem registro (irreprodutível); amostra aleatória a cada execução (quebraria a comparabilidade entre repetições do roteiro)                   | 🟢          |
| D-09 | Transferência do artefato ao Boox Air 4C por USB (MTP), destino `koreader/data/dict/`; alternativa via rede fica fora do spike                                                                                                                                                       | Caminho mais simples e offline; o componente `distribuicao-webdav` é de outro ciclo e não é pré-requisito do veredito                                                                      | Distribuição via WebDAV já neste spike (anteciparia componente inteiro sem necessidade)                                                                     | 🟡          |
| D-10 | Em veredito NO-GO, o spike executa apenas o 1º fallback de RN-05 (reduzir cobertura do `.syn` e repetir o roteiro) e re-registra; fallbacks 2 e 3 são decisão de pipeline, não deste spike                                                                                           | RN-05 fixa a ordem e o requirements limita o relatório ao registro do primeiro acionamento (RF-06)                                                                                         | Automatizar toda a escada de fallbacks (escopo além do gate)                                                                                                | 🟢          |

## 4. Premissas

Nenhum marcador `[DÚVIDA]` restou no `requirements.md` (sessão de esclarecimentos de 2026-07-03). Premissas técnicas assumidas pelo plano, todas verificáveis na primeira ação de codificação:

| Premissa                                                                                                           | Origem (`requirements.md` seção) | Risco se errada                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------ | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| O PyGlossary 5.4.1 grava `.syn` a partir de chaves alternativas das entradas, com `synwordcount` correto no `.ifo` | §5 RF-01 (mecânica de geração)   | Média: exigiria pós-processamento próprio do `.syn` ou ajuste de opções do writer; verificar com artefato-piloto minúsculo antes da geração em escala |
| O KOReader do Boox Air 4C lê dicionário instalado em `koreader/data/dict/` sem passos extras                       | §5 RF-03 (instalação)            | Baixa: caminho documentado pelo projeto KOReader; se falhar, usar o gerenciador de dicionários da própria UI                                          |
| 137.784 headwords (lemas únicos) é o `wordcount` esperado após fusão de homônimos                                  | §5 RF-01 (critério de aceite)    | Baixa: contagem verificada no banco em 2026-07-03 (`SELECT COUNT(DISTINCT lemma) FROM entries` → 137.784)                                             |

## 5. Delta arquitetural

Não existe `_reversa_sdd/architecture.md` (projeto greenfield; a extração contém PRD e specs SDD). O delta é expresso contra os componentes planejados nas specs:

| Componente                              | Arquivo de origem no legado               | Tipo de mudança | Resumo                                                                                                                                           |
| --------------------------------------- | ----------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `spike/001-flexoes` (novo, descartável) | —                                         | componente-novo | Script único que gera o artefato do spike; não é componente de produção e será substituído pelo pipeline real                                    |
| `indice-de-flexoes`                     | `_reversa_sdd/sdd/indice-de-flexoes.md`   | regra-alterada  | Nenhum código criado; o spike resolve OQ-01/OQ-02 e fixa (ou aciona) o fallback de EC-05 — a spec sai do spike com as open questions respondidas |
| `conversao-formato`                     | `_reversa_sdd/sdd/conversao-formato.md`   | regra-alterada  | Nenhum código criado; observações oportunistas respondem OQ-01 (memória/streaming) e OQ-02 (HTML no popup e-ink) da spec                         |
| `ingestao-aurelio`                      | `_reversa_sdd/sdd/ingestao-aurelio.md`    | — (não tocado)  | O spike lê o banco diretamente com queries próprias; não antecipa os iteradores de produção                                                      |
| `distribuicao-webdav`                   | `_reversa_sdd/sdd/distribuicao-webdav.md` | — (não tocado)  | Transferência manual por USB neste spike (D-09)                                                                                                  |
| `validacao-paridade`                    | `_reversa_sdd/sdd/validacao-paridade.md`  | — (não tocado)  | A validação do spike é o próprio roteiro de 20 palavras                                                                                          |

## 6. Delta no modelo de dados

- Resumo das mudanças: nenhuma. O banco `aurelio_normalized.db` permanece somente-leitura (RN-02); o spike só produz artefatos regeneráveis fora do banco (StarDict, relatório JSON, `spike-report.md`).
- Detalhe completo em: `_reversa_forward/001-spike-de-flexoes/data-delta.md`

## 7. Delta de contratos externos

| Contrato                                             | Tipo    | Arquivo de detalhe                                                            |
| ---------------------------------------------------- | ------- | ----------------------------------------------------------------------------- |
| Artefato StarDict do spike (consumido pelo KOReader) | arquivo | `_reversa_forward/001-spike-de-flexoes/interfaces/artefato-stardict-spike.md` |

## 8. Plano de migração

n/a — o spike não migra dados nem substitui sistema em uso; produz artefato descartável e um relatório.

## 9. Riscos e mitigações

| Risco                                                                              | Impacto | Probabilidade | Mitigação                                                                                                                                                               |
| ---------------------------------------------------------------------------------- | ------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PyGlossary não materializar o `.syn` como esperado a partir de chaves alternativas | alto    | baixo         | Artefato-piloto com ~10 verbetes antes da geração em escala; se falhar, investigar opções do writer StarDict antes de qualquer workaround                               |
| Latência reprovada (NO-GO) — a própria hipótese do spike                           | alto    | médio         | É o cenário previsto: RN-05 pré-registra o critério e a ordem de fallbacks; o 1º (reduzir `.syn`) roda ainda dentro do spike (D-10)                                     |
| Medição manual por cronômetro imprecisa perto do limiar                            | médio   | médio         | Protocolo de RF-03: faixa 0,8–1,2 s obriga remedição por gravação de vídeo                                                                                              |
| Geração estourar memória no MacBook (glossário inteiro em RAM)                     | médio   | médio         | `/usr/bin/time -l` registra o pico (RF-07); corpo trivial reduz o volume; se estourar, o dado alimenta a resposta da OQ-01 da `conversao-formato` (chunking necessário) |
| Cache do KOReader mascarar a latência real do primeiro lookup                      | médio   | baixo         | Roteiro executado em sessão fria (reiniciar o KOReader antes); anotar 1ª consulta vs. consultas seguintes se houver discrepância perceptível                            |
| Formas anômalas no banco interromperem a geração                                   | baixo   | baixo         | Comportamento desejado (falha barulhenta, EC-04); o registro identificado vai ao relatório e o banco não é corrigido (RN-02)                                            |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `spike-report.md` existe com veredito GO ou NO-GO pelo critério de RN-05, respostas às 4 OQs endereçadas (OQ-01/OQ-02 de `indice-de-flexoes`; OQ-01/OQ-02 de `conversao-formato`) e dados brutos das 20 palavras
- [ ] Relatório JSON de cobertura do `.syn` gravado (entradas, gravadas, descartes por motivo, órfãs nominais)
- [ ] `regression-watch.md` gerado
- [ ] Em NO-GO: registro do acionamento do 1º fallback de RN-05 com o resultado da repetição do roteiro

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-07-03 | Versão inicial gerada por `/reversa-plan` | reversa |
