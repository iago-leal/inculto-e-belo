# Roadmap: Build completo de produção do dicionário StarDict

> Identificador: `002-build-completo-de-producao`
> Data: `2026-07-03`
> Requirements: `_reversa_forward/002-build-completo-de-producao/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

O pipeline nasce como pacote Python próprio em `pipeline/` (RN-08), com projeto uv independente do spike, e materializa os quatro componentes planejados P-01..P-04 de `_reversa_sdd/architecture.md#2-componentes` em camadas: um repositório de leitura encapsula todo o SQL (`ingestao-aurelio`), duas funções de domínio puro fazem o mapeamento de flexões e a renderização HTML (`indice-de-flexoes` e a metade pura de `conversao-formato`), um adaptador isola o PyGlossary na escrita, e um validador com parser StarDict próprio em stdlib fecha o gate (`validacao-paridade`). Uma CLI única encadeia as etapas numa mesma execução, eliminando por construção a dessincronia banco↔build↔validação (EC-06 da spec de paridade). O spike `spike/001-flexoes/` não é tocado: serve só de referência de leitura — as regras que ele validou (fusão de homônimos, RB-14, `l_word` como via do `.syn`, escrita atômica) entram reimplementadas nas camadas. O delta sobre o spike é qualitativo, não mecânico: corpo integral para os 137.784 headwords em vez de HTML trivial, mais a validação de paridade que o spike não tinha.

## 2. Princípios aplicados

`.reversa/principles.md` não existe neste projeto. Valem os princípios operacionais do mantenedor, já incorporados como requisitos (RNFs de testabilidade, reprodutibilidade e observabilidade do `requirements.md#6`):

| Princípio                                  | Como a feature se relaciona                                                                         | Status   |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------- | -------- |
| Estabilidade > novidade                    | Stack mínima e pinada: Python 3.12+, PyGlossary 5.4.1, python-idzip 0.3.9; validador em stdlib pura | respeita |
| Erros barulhentos > performance            | Erros nomeados em toda anomalia; tolerância zero na paridade; nenhum descarte silencioso            | respeita |
| Retomabilidade (mantenedor intermitente)   | README executável (RF-08) + manifesto de integridade versionado + relatórios JSON por build         | respeita |
| Rigor de Aplicação (Princípio nº 4 global) | Camadas, domínio puro testado ≥ 60%, contratos explícitos entre componentes                         | respeita |

## 3. Decisões técnicas

| ID   | Decisão                                                                                                                                                                                                                                         | Justificativa                                                                                                                                                                     | Alternativas descartadas                                                                                                            | Confidência |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| D-01 | Pacote uv em `pipeline/` com `src/aurelio_pipeline/` e console script `aurelio-pipeline`; `pyproject.toml` + `uv.lock` commitados                                                                                                               | RN-08 (pasta própria); padrão uv já validado no spike; console script dá o comando único de RF-07                                                                                 | Evoluir dentro de `spike/` (contraria RN-08); script solto sem pacote (sem camadas testáveis)                                       | 🟢          |
| D-02 | Camadas: `infra/repositorio.py` (único dono do SQL), `dominio/` (modelos, `indice_flexoes.py`, `renderizacao.py` — puros, sem I/O), `infra/escrita_stardict.py` (adaptador PyGlossary), `validacao/` (leitor + checks), `cli.py` (orquestração) | Specs §8 dos quatro componentes exigem domínio isolado de infra; testabilidade com fixtures mínimas                                                                               | Monólito estilo `gerar_spike.py` (inviabiliza cobertura de domínio); camadas por arquivo físico de saída (coesão temporal, evitada) | 🟢          |
| D-03 | Duas passadas sobre o banco na mesma execução: 1ª constrói headwords + mapa de flexões; 2ª itera `Verbete` completos por streaming e renderiza                                                                                                  | O `.syn` precisa do conjunto de headwords fechado antes da escrita; streaming mantém pico < 2 GB (OQ-01 de `conversao-formato` respondida: PyGlossary opera em memória com folga) | Passada única com mapa tardio (PyGlossary precisa dos alternates no `addEntry`); carregar agregados inteiros em memória             | 🟢          |
| D-04 | Formas entram como chaves alternativas (`l_word`) no `addEntry`; PyGlossary materializa o `.syn`                                                                                                                                                | Mecanismo validado ponta a ponta no spike (774.003 formas, 20/20 no roteiro)                                                                                                      | Escrever `.syn` manualmente (reimplementa o que a biblioteca já faz certo)                                                          | 🟢          |
| D-05 | `python-idzip==0.3.9` pinado; a escrita verifica que o `.dict.dz` existe ao fim do build e falha com erro nomeado se a compressão degradou                                                                                                      | Achado nº 3 do spike: sem idzip o PyGlossary degrada silenciosamente para `.dict` sem compressão — exatamente o modo de falha que RF-05 proíbe                                    | Aceitar `.dict` sem compressão como fallback (artefato divergente do spec)                                                          | 🟢          |
| D-06 | Renderizador `Verbete → HTML` como função pura, com o vocabulário validado no spike (`<b> <i> <u> <p> <ul> <li> <small>`); `content_html` do banco embutido como está (RB-03 limita as tags a `em/u/strong`)                                    | OQ-02 de `conversao-formato` respondida no desktop; RB-03 garante que o HTML de origem é seguro e mínimo                                                                          | Sanitização agressiva com parser HTML (complexidade sem defeito observado; EC-01 vira log de advertência)                           | 🟢          |
| D-07 | Parser StarDict de leitura em stdlib pura: `struct` para `.idx`/`.syn` (offsets/tamanhos uint32 big-endian, strings NUL-terminadas UTF-8), `gzip` para `.dict.dz` (dictzip é gzip válido)                                                       | RF-06 exige independência do PyGlossary; ler o formato é ordens de magnitude mais simples que escrever (decision log da spec de paridade)                                         | Validar com sdcv externo (dependência de sistema não pinável); validar com PyGlossary (circularidade)                               | 🟢          |
| D-08 | Comparação de conteúdo da amostra: extrai texto do artigo (strip de tags + unescape), colapsa whitespace dos dois lados e verifica `contains` do `content_text` do banco                                                                        | Decisão da sessão de esclarecimentos (§9 do requirements); o banco já traz `content_text` par de `content_html` (RB-03), dispensando reconversão de HTML                          | Contains estrito byte a byte (falso negativo por reformatação); comparação de HTML renderizado (frágil)                             | 🟢          |
| D-09 | Amostragem com `random.Random(seed)` e seeds fixas registradas no relatório (verbetes e flexões separadas)                                                                                                                                      | RNF-03 da spec de paridade: mesmo input + mesma seed → mesmo relatório                                                                                                            | `random` global sem seed (não reproduzível)                                                                                         | 🟢          |
| D-10 | `manifesto-integridade.json` versionado em `pipeline/`, só contagens por tabela (12 tabelas de domínio consumidas) + data de referência                                                                                                         | Decisão da sessão de esclarecimentos; mantém smoke tests < 5 s                                                                                                                    | Hash por tabela (custo de varredura integral; detecção redundante com a amostragem da paridade)                                     | 🟢          |
| D-11 | Artefato em `dist/aurelio-stardict/` na raiz do repo, substituído por rename atômico sem retenção; relatórios (`relatorio-cobertura.json`, `parity-report.json`) gravados dentro do diretório do artefato, fora do git                          | Caminho fixado nas specs; decisão de retenção da sessão de esclarecimentos; relatórios citam trechos sob direitos autorais → permanecem locais (spec paridade §12)                | Cópia `.prev` e versões datadas (custo de disco sem benefício: rebuild é determinístico e < 10 min)                                 | 🟢          |
| D-12 | Testes com pytest (dev-dependency pinada no grupo `dev` do uv), fixtures de banco SQLite em memória com mini-schema real; cobertura ≥ 60% no domínio medida com coverage                                                                        | RNF de testabilidade; fixtures em memória tornam a suíte rápida (< 2 min, sinal de dívida do mantenedor)                                                                          | Testar contra o banco real de 189 MB (lento, acopla suíte ao ativo); sem framework (asserts ad hoc)                                 | 🟢          |
| D-13 | Logs com `logging` stdlib em formato chave=valor, progresso a cada 100.000 pares / 10.000 verbetes (padrão do spike)                                                                                                                            | RNF de observabilidade; consistência com o código de referência                                                                                                                   | Biblioteca de logging estruturado externa (dependência a mais sem ganho local)                                                      | 🟢          |
| D-14 | `.gitignore` ganha `dist/` e `pipeline/.venv/`; `pyproject.toml`, `uv.lock` e `manifesto-integridade.json` entram no git                                                                                                                        | Artefato e venv são regeneráveis e volumosos; manifesto e locks são o contrato de reprodutibilidade (RB-12/RB-13)                                                                 | Commitar o artefato (189 MB+ derivado, viola RB-09 por analogia)                                                                    | 🟢          |

## 4. Premissas

Nenhuma: o `requirements.md` está sem `[DÚVIDA]` (as quatro dúvidas foram resolvidas na sessão de esclarecimentos de 2026-07-03, §9).

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
| -------- | -------------------------------- | --------------- |
| —        | —                                | —               |

## 5. Delta arquitetural

| Componente                      | Arquivo de origem no legado                  | Tipo de mudança        | Resumo                                                                                                      |
| ------------------------------- | -------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------- |
| `ingestao-aurelio` (P-01)       | `_reversa_sdd/architecture.md#2-componentes` | componente-novo        | Nasce como `infra/repositorio.py` + smoke tests contra manifesto; primeiro código de produção do componente |
| `indice-de-flexoes` (P-02)      | `_reversa_sdd/architecture.md#2-componentes` | componente-novo        | Nasce como `dominio/indice_flexoes.py`, função pura com relatório de cobertura; alvo 774.003 (RN-03)        |
| `conversao-formato` (P-03)      | `_reversa_sdd/architecture.md#2-componentes` | componente-novo        | Nasce como `dominio/renderizacao.py` (puro) + `infra/escrita_stardict.py` (adaptador PyGlossary)            |
| `validacao-paridade` (P-04)     | `_reversa_sdd/architecture.md#2-componentes` | componente-novo        | Nasce como `validacao/` com parser stdlib e checks de tolerância zero; gate por exit code                   |
| `banco-lexical` (C-01)          | `_reversa_sdd/architecture.md#2-componentes` | inalterado             | Consumido exclusivamente em `mode=ro`; nenhuma escrita, nenhuma correção (RN-01)                            |
| `spike/001-flexoes` (S-01)      | `_reversa_sdd/architecture.md#2-componentes` | inalterado (congelado) | Permanece como registro histórico do gate (RN-08); nenhuma linha movida ou alterada                         |
| `governanca-operacional` (C-02) | `_reversa_sdd/architecture.md#2-componentes` | contrato-alterado      | `.gitignore` ganha `dist/` e `pipeline/.venv/`; README do repo ganha ponteiro para `pipeline/README.md`     |
| `distribuicao-webdav` (P-05)    | `_reversa_sdd/architecture.md#2-componentes` | fora do escopo         | Permanece só como spec; a instalação nesta feature é manual (USB/cópia local)                               |

## 6. Delta no modelo de dados

- Resumo das mudanças: o banco não muda (somente-leitura). Nascem quatro dados derivados: o manifesto de integridade versionado, o artefato StarDict e os dois relatórios JSON (cobertura do índice e paridade), todos regeneráveis.
- Detalhe completo em: `_reversa_forward/002-build-completo-de-producao/data-delta.md`

## 7. Delta de contratos externos

| Contrato                                  | Tipo    | Arquivo de detalhe                                                                |
| ----------------------------------------- | ------- | --------------------------------------------------------------------------------- |
| Artefato StarDict consumido pelo KOReader | arquivo | `_reversa_forward/002-build-completo-de-producao/interfaces/artefato-stardict.md` |

## 8. Plano de migração

Não há migração de dados. Há uma troca operacional de artefato instalado:

1. Gerar e validar o artefato de produção (`dist/aurelio-stardict/` aprovado pela paridade).
2. No KOReader de teste (macOS), instalar `aurelio-stardict/` e remover `aurelio-spike/` do diretório de dicionários — evita resultados duplicados no popup.
3. No Boox, quando a instalação acontecer (gesto que cumpre a condição de monitoramento do GO presumido do spike), aplicar a mesma troca.

## 9. Riscos e mitigações

| Risco                                                                                   | Impacto | Probabilidade      | Mitigação                                                                                                                                                             |
| --------------------------------------------------------------------------------------- | ------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pico de memória acima de 2 GB com corpo integral (spike mediu 462 MB com corpo trivial) | médio   | baixo              | Medir com `/usr/bin/time -l` no primeiro build completo; se estourar, chunking na adição de entradas é o plano B já apontado pela spec (OQ-01)                        |
| Artefato acima de 250 MB comprimido                                                     | baixo   | baixo              | dictzip comprime texto ~3-4×; medir no primeiro build; se estourar, avaliar poda de exemplos `citation` como corte deliberado e documentado                           |
| Latência no e-ink segue presumida (herança do GO presumido do spike)                    | médio   | baixo              | Fora do escopo desta feature reavaliar; a escada de fallbacks de RN-05 do spike permanece válida (`--cobertura flexions-somente` vira flag da CLI também na produção) |
| Falso negativo na amostra de paridade por HTML de origem malformado (EC-01)             | baixo   | médio              | Comparação usa `content_text` do banco (não o HTML); advertências de saneamento logadas com id do verbete para triagem manual                                         |
| Regeneração futura do banco muda contagens e quebra o build                             | baixo   | certo (por design) | É o comportamento desejado: `ContagemDivergenteError` + fluxo de atualização deliberada do manifesto em commit próprio (RF-01/RF-08)                                  |
| PyGlossary 5.4.1 mudar comportamento em reinstalação futura                             | baixo   | baixo              | Versões exatas no `uv.lock`; paridade independente detectaria qualquer divergência estrutural do artefato                                                             |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `parity-report.json` com veredito **aprovado**: 137.784 headwords, 774.003 entradas no `.syn`, amostras 500+500 sem divergência
- [ ] Suíte de testes verde com cobertura ≥ 60% no domínio (`dominio/` e `validacao/paridade`)
- [ ] `pipeline/README.md` cobre reprodução do zero (cenário Gherkin de RF-08)
- [ ] Artefato instalado e conferido no KOReader do macOS (smoke com 3 palavras do roteiro do spike)
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data       | Alteração                                 | Autor   |
| ---------- | ----------------------------------------- | ------- |
| 2026-07-03 | Versão inicial gerada por `/reversa-plan` | reversa |
