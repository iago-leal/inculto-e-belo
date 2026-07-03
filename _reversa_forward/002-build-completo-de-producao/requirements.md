# Requirements: Build completo de produção do dicionário StarDict

> Identificador: `002-build-completo-de-producao`
> Data: `2026-07-03`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Esta feature implementa o pipeline de produção que converte o banco lexical completo (143.376 entries) num dicionário StarDict instalável no KOReader, com verbetes integrais — definições, exemplos, locuções, notas e regência —, índice de flexões auditado e validação de paridade independente. Ela materializa as quatro specs SDD já aprovadas (`ingestao-aurelio` → `indice-de-flexoes` → `conversao-formato` → `validacao-paridade`), destravadas pelo veredito GO presumido do spike 001. Resolve o problema central do produto: o Aurélio normalizado está preso em SQLite, formato que nenhum leitor consome, e o spike entregou apenas corpo trivial para 20 lemas. O usuário é o próprio mantenedor, nos papéis de leitor e de operador intermitente do build. A distribuição via WebDAV fica para feature posterior.

## 2. Contexto a partir do legado

| Fonte                                                                                            | Trecho relevante                                                                                                                                                                        | Confidência |
| ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `_reversa_sdd/architecture.md#2-componentes`                                                     | Componentes planejados P-01 a P-04 com fronteiras decididas; fluxo C-01 → P-01 → (P-02 ‖ P-03) → P-04                                                                                   | 🟡          |
| `_reversa_sdd/architecture.md#4-decisões-arquiteturais-em-vigor`                                 | Specs antes de código; PyGlossary 5.4.1 pinado; banco somente-leitura; domínio puro isolado de infra via adaptadores                                                                    | 🟢          |
| `_reversa_sdd/domain.md#3-regras-de-negócio`                                                     | RB-02 (fusão de homônimos é do consumidor), RB-05 (integridade lemma↔formas é do consumidor; 22 órfãs), RB-09 a RB-13 (governança)                                                      | 🟢          |
| `_reversa_sdd/domain.md#achado-novo-da-revisão-rb-14`                                            | RB-14: `flexions.flexion` traz múltiplas formas por linha (1.349 com `,`, 15 com `" ou "`); consumidores devem dividir antes de indexar                                                 | 🟢          |
| `_reversa_sdd/domain.md#4-invariantes-quantitativas-baseline-2026-07-03`                         | 143.376 entries / 137.784 lemas únicos; 175.259 flexões + 869.119 conjugações; 22 órfãs                                                                                                 | 🟢          |
| `_reversa_sdd/sdd/ingestao-aurelio.md#6-requisitos-funcionais`                                   | Abertura `mode=ro`, manifesto de integridade versionado, agregados `Verbete`, iteradores de pares, erros nomeados                                                                       | 🟡          |
| `_reversa_sdd/sdd/indice-de-flexoes.md#6-requisitos-funcionais`                                  | Mapeamento forma→headword como domínio puro; descartes classificados (`orfa`, `duplicada`, `identica`); ambíguas preservadas; relatório JSON com invariante                             | 🟡          |
| `_reversa_sdd/sdd/conversao-formato.md#6-requisitos-funcionais`                                  | Homônimos fundidos por lema; HTML autocontido; PyGlossary 5.4.1; `sametypesequence=h`; dictzip; escrita atômica; metadados do `.ifo`                                                    | 🟡          |
| `_reversa_sdd/sdd/validacao-paridade.md#6-requisitos-funcionais`                                 | Parser StarDict próprio em stdlib; contagens integrais; amostras 500+500 com seed fixa; tolerância zero; exit code como gate                                                            | 🟡          |
| `_reversa_forward/001-spike-de-flexoes/spike-report.md#4-achados-que-alimentam-o-build-completo` | Baseline real do `.syn` = 774.003 pares válidos; RB-14 obrigatório; `python-idzip==0.3.9` necessário para dictzip; EC-04 nunca disparou; fusão de homônimos validada ponta a ponta      | 🟢          |
| `_reversa_forward/001-spike-de-flexoes/spike-report.md#3-respostas-às-open-questions`            | PyGlossary opera em memória com folga (462 MB de pico no spike); lookup exato não normaliza caixa/diacríticos (gravar formas como estão no banco); HTML básico renderiza bem no desktop | 🟢          |

## 3. Personas e cenários de uso

| Persona                | Objetivo                                                        | Cenário-chave                                                                                                                         |
| ---------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| iago-leitor            | Consultar o Aurélio completo durante leitura offline            | Toca em "cantávamos" no KOReader e o popup abre o verbete integral de "cantar" em menos de 1 s                                        |
| iago-mantenedor-futuro | Regenerar o artefato após meses de pausa, guiado só pelo README | Roda o pipeline por uma CLI única; smoke tests validam o banco, o build gera o artefato e a paridade aprova ou bloqueia com relatório |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** O banco permanece somente-leitura em todo o pipeline (abertura via `mode=ro`); órfãs e anomalias são reportadas, nunca corrigidas. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#3-regras-de-negócio` (RB-05, RB-10)
   - Tipo: herdada (inalterada)
2. **RN-02:** Toda forma de `flexions.flexion` é dividida pelos separadores `,` e `" ou "` antes de indexar (RB-14); `conjugations` não exige split. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#achado-novo-da-revisão-rb-14`
   - Tipo: nova (incorporação obrigatória do achado do spike)
3. **RN-03:** O alvo quantitativo do `.syn` é **774.003 pares únicos válidos** (= 100% dos pares após deduplicação e descartes auditados), substituindo a estimativa de ≥ 900 mil das specs; o valor é recalculado a cada regeneração do banco e conferido pela invariante `entrada = gravadas + descartes`. 🟢
   - Origem no legado: `_reversa_forward/001-spike-de-flexoes/spike-report.md#4` (altera `_reversa_sdd/sdd/indice-de-flexoes.md#3-goals`, métrica original)
   - Tipo: alterada
4. **RN-04:** Nenhum artefato é considerado entregue sem aprovação da validação de paridade independente (exit code 0); reprovação bloqueia qualquer uso ou distribuição, com tolerância zero a divergências. 🟡
   - Origem no legado: `_reversa_sdd/sdd/validacao-paridade.md#3-goals`
   - Tipo: nova
5. **RN-05:** O artefato herda a restrição de uso estritamente pessoal (conteúdo sob direitos autorais do Aurélio); nada é publicado. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#3-regras-de-negócio` (RB-11)
   - Tipo: herdada (inalterada)
6. **RN-06:** O build é determinístico e auditável: duas execuções sobre o mesmo banco produzem o mesmo conjunto de headwords, artigos e entradas do `.syn`, com relatórios JSON versionáveis por execução. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#3-regras-de-negócio` (RB-12)
   - Tipo: herdada (inalterada)
7. **RN-07:** As formas entram no `.syn` grafadas exatamente como estão no banco (minúsculas, com diacríticos); não se duplicam variantes capitalizadas, pois o resgate de caixa/diacríticos é do mecanismo fuzzy do leitor. 🟢
   - Origem no legado: `_reversa_forward/001-spike-de-flexoes/spike-report.md#3` (OQ-02 de `indice-de-flexoes`)
   - Tipo: nova (decisão de design validada no spike)
8. **RN-08:** O pipeline de produção nasce em pasta própria (`pipeline/`), implementando do zero as camadas das specs; `spike/001-flexoes/` permanece intocado como registro histórico do gate, servindo apenas de referência de leitura para os achados já incorporados às regras. 🟢
   - Origem no legado: decisão do usuário na sessão de esclarecimentos de 2026-07-03 (§9); coerente com o caráter descartável do spike em `_reversa_sdd/architecture.md#2-componentes` (S-01)
   - Tipo: nova

## 5. Requisitos Funcionais

| ID    | Requisito                                                                                                                                                                                                                                                                                                                                                                                                                                       | Prioridade | Critério de aceite                                                                                                                                                                    | Confidência |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| RF-01 | A ingestão abre o banco em `mode=ro`, valida esquema e contagens contra `manifesto-integridade.json` versionado (contagens por tabela, sem hash — ver §9) e falha com erros nomeados (`BancoAusenteError`, `EsquemaInvalidoError`, `ContagemDivergenteError`, `BancoCorrompidoError`) antes de qualquer conversão                                                                                                                               | Must       | Banco ausente, tabela faltante ou contagem divergente interrompem a execução com exit code ≠ 0 e mensagem acionável; suíte de testes cobre cada erro nomeado                          | 🟡          |
| RF-02 | A ingestão expõe iterador de agregados `Verbete` completos (blocos, definições, exemplos, locuções, notas, regência, ordenados por `position`/`sort_key`) e iteradores dos pares de flexão e conjugação, sem vazar SQL aos consumidores                                                                                                                                                                                                         | Must       | Iteração completa produz 143.376 agregados e 175.259 + 869.119 pares; o verbete `abacaxi` contém definições e exemplos na ordem do banco                                              | 🟡          |
| RF-03 | O índice de flexões constrói o mapeamento forma→headword como função de domínio pura: aplica o split de RN-02, resolve homônimos ao headword fundido, descarta com classificação (`orfa`, `duplicada`, `identica` — comparação exata sensível a diacríticos), preserva ambíguas em N entradas e grava relatório JSON cuja invariante fecha                                                                                                      | Must       | Sobre o banco atual: 774.003 pares gravados, 22 lemas órfãos (748 formas) listados nominalmente, invariante `entrada = gravadas + orfa + duplicada + identica` verificada por teste   | 🟢          |
| RF-04 | A conversão renderiza **cada** headword como artigo HTML autocontido e integral — lema estilizado, classe gramatical, IPA, etimologia, definições numeradas com rubrica, exemplos (preservando a distinção editor/citation de RB-07), locuções com definições, notas e regência —, fundindo homônimos em artigo único na ordem `homonym`/`sort_key`                                                                                             | Must       | O artigo de `coração` contém as seções dos 3 homônimos; o de `abacaxi` contém todas as definições e exemplos do banco; renderizador é função pura testada sem PyGlossary              | 🟡          |
| RF-05 | A geração StarDict usa PyGlossary `==5.4.1` com `python-idzip==0.3.9` (ambos no lock file), produz `.ifo`/`.idx`/`.dict.dz`/`.syn` com `sametypesequence=h`, metadados coerentes (`wordcount=137784`, `synwordcount=774003`, `bookname`, `date`) e escrita atômica (diretório temporário → rename para `dist/aurelio-stardict/`, substituindo a versão anterior sem retenção — regeneração é a via de rollback, ver §9)                         | Must       | Build interrompido não corrompe `dist/`; o `.ifo` declara os totais reais; ausência do idzip falha com erro nomeado em vez de degradar para `.dict` sem compressão                    | 🟢          |
| RF-06 | A validação de paridade lê o artefato com parser StarDict próprio (stdlib pura, sem importar PyGlossary), compara contagens integrais (headwords, `.syn`, metadados do `.ifo`) e amostras determinísticas de 500 lemas + 500 formas (seed fixa registrada); a comparação de conteúdo da amostra normaliza whitespace de ambos os lados antes do `contains` (ver §9); grava `parity-report.json` e retorna exit code 0 apenas em aprovação total | Must       | Um headword a menos, um `.syn` truncado ou uma definição ausente na amostra reprovam com a divergência exata no relatório; teste de importação comprova a independência do PyGlossary | 🟡          |
| RF-07 | Uma CLI única orquestra o pipeline ponta a ponta (ingestão → índice → conversão → validação) com logs estruturados chave=valor por etapa (totais, duração, tamanhos) e progresso periódico                                                                                                                                                                                                                                                      | Must       | `uv run <cli>` executa o fluxo completo; o log final contém `headwords=`, `sinonimos=`, `duracao_s=` e o caminho do `parity-report.json`                                              | 🟡          |
| RF-08 | O README do pipeline documenta reprodução completa do zero (restauração do banco via rclone, `uv sync`, build, validação, instalação manual no KOReader) e o fluxo de atualização deliberada do manifesto de integridade                                                                                                                                                                                                                        | Must       | Seguindo apenas o README, um operador leigo no projeto executa build + validação com sucesso; a atualização do banco exige commit explícito do manifesto                              | 🟢          |

## 6. Requisitos Não Funcionais

| Tipo                  | Requisito                                                                                                                                     | Evidência ou justificativa                                                                                                                          | Confidência |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| Desempenho            | Build completo < 10 min; validação < 3 min; smoke tests < 5 s (MacBook do mantenedor)                                                         | `_reversa_sdd/sdd/conversao-formato.md#7`, `validacao-paridade.md#7`; spike gerou em 4,9 s com corpo trivial — folga ampla mesmo com corpo integral | 🟡          |
| Memória               | Pico do processo de build < 2 GB, sem chunking                                                                                                | Spike: 462 MB de pico em memória; projeção com 259 mil acepções em HTML segue confortável (`spike-report.md#3`, OQ-01 de `conversao-formato`)       | 🟢          |
| Tamanho               | Artefato final < 250 MB                                                                                                                       | `_reversa_sdd/sdd/conversao-formato.md#7` (RNF-03: cabe em dispositivo modesto)                                                                     | 🟡          |
| Confiabilidade        | Falhas barulhentas com erros nomeados em toda condição anômala; nunca artefato parcial em silêncio; escrita atômica em `dist/`                | PRD e specs (mantenedor intermitente descobriria falha silenciosa meses depois); `ingestao-aurelio.md#11`, `conversao-formato.md#11`                | 🟡          |
| Testabilidade         | Domínio puro (índice de flexões, renderizador, checks de paridade) com testes de unidade e cobertura ≥ 60%; erros nomeados cobertos por teste | Princípios do mantenedor (rigor de Aplicação); `indice-de-flexoes.md#8`, `validacao-paridade.md#8`                                                  | 🟡          |
| Reprodutibilidade     | `pyproject.toml` + `uv.lock` commitados com versões exatas (PyGlossary 5.4.1, python-idzip 0.3.9); Python 3.12+; build determinístico         | RB-12/RB-13 (`domain.md#3`); padrão já validado em `spike/001-flexoes/`                                                                             | 🟢          |
| Observabilidade       | Logs estruturados chave=valor por etapa; relatórios JSON (cobertura do índice e paridade) persistidos por execução                            | `ingestao-aurelio.md#12`, `validacao-paridade.md#12`                                                                                                | 🟡          |
| Segurança/privacidade | Sem PII; conteúdo sob direitos autorais restrito a uso pessoal; nenhum dado sai do processo local                                             | `_reversa_sdd/domain.md#3` (RB-11); `inventory.md#7`                                                                                                | 🟢          |

## 7. Critérios de Aceitação

```gherkin
Cenário: build completo aprovado de ponta a ponta
  Dado o banco aurelio_normalized.db íntegro e o manifesto de integridade em dia
  Quando o mantenedor executa a CLI do pipeline
  Então dist/aurelio-stardict/ contém .ifo, .idx, .dict.dz e .syn com wordcount=137784 e synwordcount=774003
  E o parity-report.json registra veredito "aprovado" e o processo termina com exit code 0

Cenário: verbete integral no artefato
  Dado o artefato aprovado instalado num KOReader
  Quando o leitor toca na forma flexionada "cantávamos"
  Então o popup abre o artigo de "cantar" contendo definições numeradas, exemplos, locuções, notas e regência presentes no banco

Cenário: linha de flexão com múltiplas formas (RB-14)
  Dado um registro de flexions cuja coluna flexion contém "amigas, amiguinhas"
  Quando o índice de flexões processa o par
  Então cada forma resultante do split entra como entrada própria do mapeamento apontando ao headword correto

Cenário: banco ausente interrompe o pipeline
  Dado que aurelio_normalized.db não existe no caminho configurado
  Quando o pipeline inicia
  Então a execução termina com exit code ≠ 0 e a mensagem contém o caminho esperado e o comando de restauração via rclone

Cenário: paridade reprovada bloqueia a entrega
  Dado um artefato gerado com um headword a menos que o esperado
  Quando a validação de paridade executa
  Então o parity-report.json registra veredito "reprovado" com esperado vs. obtido e o processo termina com exit code ≠ 0

Cenário: ingestão entrega os totais do manifesto
  Dado o banco íntegro e o manifesto de integridade em dia
  Quando a iteração completa dos agregados e dos pares executa
  Então são produzidos 143.376 agregados Verbete, 175.259 pares de flexão e 869.119 pares de conjugação, sem consulta SQL fora da camada de ingestão

Cenário: reprodução do zero guiada pelo README
  Dado um clone limpo do repositório numa máquina com o gerenciador de pacotes instalado e sem o banco local
  Quando o operador segue apenas os passos do README (restauração do banco, sincronização de dependências, build e validação)
  Então o pipeline conclui com artefato aprovado sem nenhum passo não documentado
```

## 8. Prioridade MoSCoW

| Item                 | MoSCoW | Justificativa                                                                                              |
| -------------------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| RF-01, RF-02         | Must   | Sem ingestão validada, o pior modo de falha do PRD (dicionário silenciosamente incompleto) fica sem defesa |
| RF-03                | Must   | O lookup de flexionadas é a promessa central do produto; baseline e regras já validados pelo spike         |
| RF-04                | Must   | É o delta essencial sobre o spike: corpo integral dos 137.784 artigos, não mais HTML trivial               |
| RF-05                | Must   | Sem artefato StarDict correto e atômico não há produto; pinagens já comprovadas                            |
| RF-06                | Must   | Gate que separa "build concluiu" de "build está correto"; tolerância zero é decisão registrada             |
| RF-07                | Must   | Mantenedor intermitente precisa de um comando único; orquestração manual das etapas é fonte de erro        |
| RF-08                | Must   | Retomabilidade por README é regra de operação do projeto (RB-13)                                           |
| RNF de desempenho    | Should | Limites folgados pelas medições do spike; estouro indica defeito, não exige otimização preventiva          |
| RNF de testabilidade | Must   | Categoria Aplicação: domínio puro testado é precondição da entrega, não acessório                          |

## 9. Esclarecimentos

### Sessão 2026-07-03

- **Q:** Onde nasce o código do pipeline de produção e qual o destino da pasta `spike/`?
  **R:** Pasta nova (`pipeline/`), implementando as camadas das specs do zero; `spike/001-flexoes/` permanece intocado como registro histórico do gate, consultado apenas como referência dos achados. Integrado como RN-08.
- **Q:** Na amostragem de conteúdo da validação de paridade, como comparar o texto da definição do banco com o artigo extraído do artefato? (OQ-01 de `validacao-paridade`)
  **R:** Normalizar whitespace de ambos os lados (colapso de espaços e quebras) antes do `contains`; perda real de texto continua reprovando. Integrado ao RF-06.
- **Q:** O manifesto de integridade deve registrar hash por tabela além das contagens? (OQ-01 de `ingestao-aurelio`)
  **R:** Não: só contagens por tabela, preservando o limite de 5 s dos smoke tests. Mutação com contagem idêntica é cenário remoto num banco somente-leitura, e a amostragem da paridade compara conteúdo real a cada build. Integrado ao RF-01.
- **Q:** Ao regenerar `dist/aurelio-stardict/`, reter a versão anterior do artefato?
  **R:** Não: o rename atômico substitui sem retenção. O build é determinístico e barato (< 10 min); banco + código versionado reproduzem qualquer versão passada. Integrado ao RF-05.

## 10. Lacunas

- Nenhuma lacuna aberta. As três dúvidas da versão inicial foram resolvidas na sessão de 2026-07-03 (ver §9).

## Pendências de Qualidade

- **SoluçãoImplícita (Q-018), exceção deliberada:** o documento nomeia ferramentas concretas (PyGlossary 5.4.1, python-idzip 0.3.9, formato StarDict, rclone). Não é solução implícita do redator: são decisões já registradas e em vigor (ADR-0004, decision logs das specs SDD e achado nº 3 do `spike-report.md#4`), cuja omissão tornaria os requisitos infiéis ao contrato herdado. Mantidas por fidelidade à fonte.

## 11. Histórico de alterações

| Data       | Alteração                                                                                                        | Autor          |
| ---------- | ---------------------------------------------------------------------------------------------------------------- | -------------- |
| 2026-07-03 | Versão inicial gerada por `/reversa-requirements`                                                                | reversa        |
| 2026-07-03 | Sessão de esclarecimentos: 4 dúvidas resolvidas (RN-08 criada; RF-01, RF-05 e RF-06 precisados); lacunas zeradas | reversa + iago |
