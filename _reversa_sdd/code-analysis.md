# Análise técnica — inculto-e-belo

> Gerado pelo reversa-archaeologist em 2026-10-15 (re-extração; a análise anterior, de 2026-07-03, cobria só `banco-lexical` e `governanca-operacional`)
> Módulos: `banco-lexical`, `governanca-operacional`, `pipeline-nucleo`, `pipeline-koreader`, `pipeline-readest`, `spike-001-flexoes`
> Confidência: 🟢 CONFIRMADO (extraído do código, do banco ou dos relatórios do último build), 🟡 INFERIDO, 🔴 LACUNA

## Módulo `banco-lexical`

### 1. Natureza

🟢 Continua sendo dado puro: schema e conteúdo de `aurelio_normalized.db` (SQLite, WAL, FTS5), sem código executável. O arquivo não mudou desde 2026-07-03: o mtime é o da importação, e as 12 contagens do `pipeline/manifesto-integridade.json` batem com o banco. A novidade está no consumo: o pipeline lê o banco em modo somente-leitura e passou a depender de um subconjunto declarado de colunas (ver `pipeline-nucleo`, §2).

### 2. Modelo hierárquico do verbete

🟢 Inalterado:

```
entries (1) ──< word_class_blocks (N, por classe gramatical)
                    └──< definitions (N, acepções ordenadas por position)
                              ├── rubric_id → rubrics
                              ├──< examples (kind: 'editor' | 'citation')
                              └──< notes (parent_type='definition')
entries ──< locutions ──< locution_definitions ──< examples / notes
entries ──< verb_rection (regência, fonte 'luft')
entries ──< notes (parent_type='entry')
entries ──< orthographic_marks → orthographic_rules
entries >── flexions (por entry_head, texto, não FK)   [175.259]
entries >── conjugations (por infinitive, texto, não FK) [869.119]
```

A ligação textual de `flexions` e `conjugations` com `entries.lemma` segue produzindo as 22 cabeças órfãs (11 infinitivos e 11 cabeças), que somam 748 formas descartadas no índice de flexões. 🟢

### 3. Contagens

| Tabela | Linhas | | Tabela | Linhas |
|--------|--------|-|--------|--------|
| entries | 143.376 | | locutions | 22.168 |
| word_class_blocks | 168.361 | | locution_definitions | 24.034 |
| definitions | 259.337 | | verb_rection | 6.170 |
| examples | 54.726 | | rubrics | 2.655 |
| notes | 28.903 | | word_classes | 302 |
| flexions | 175.259 | | orthographic_marks | 3.280 |
| conjugations | 869.119 | | orthographic_rules | 15 |

`sqlite_master` registra 25 tabelas: 14 de domínio, 10 internas do FTS5 e `sqlite_sequence`, que a extração anterior não somava. Há 18 índices, nenhuma view e nenhum trigger.

### 4. Domínios de valores

Os valores e as interpretações da extração anterior seguem válidos; o detalhe está em `data-dictionary.md`. O único ponto novo é `entries.most_used`, com 0 em 140.337 linhas e 1 em 3.039. Sua semântica continua 🟡 INFERIDA (vocabulário frequente), mas agora tem efeito: ordena os artigos não coincidentes nas páginas combinadas do Readest. Ao todo, 3.039 entradas resolvem para os lemas devolvidos por `lemas_frequentes()`.

### 5. Invariantes do schema

As seis invariantes da extração anterior seguem confirmadas: acepções em blocos de classe, homonímia em linhas separadas, pares HTML/texto, ordem por `position`, FTS5 external content e grafias pré-acordo. Uma sétima passou a ser imposta pelo consumidor, não pelo schema: o HTML do banco não contém `<hr>`, e o alvo Readest usa essa tag como fronteira entre artigos. 🟢 A validação do Readest reprova se a premissa falhar.

## Módulo `governanca-operacional`

### 1. Componentes

| Arquivo | Papel | Análise |
|---------|-------|---------|
| `harness` (Bash, 13 linhas úteis) | Shim que lê `upstream_path` de `harness.toml` e faz `exec` do core Python do Harness | 🟢 Inalterado; falha barulhenta (exit 1) se o core não existir |
| `harness.toml` | Config do Harness | 🟢 Mudou: a seção `[regen]` está ativa, com `command = "cd pipeline && uv run aurelio-pipeline"`, que regenera **só o alvo KOReader** (D-19 da 003). O comentário cita «~12 s» |
| `.gitignore` | Exclusões | 🟢 Ampliado: além de bancos e caches, exclui `spike/*/dist/`, `spike/*/.venv/`, as medições do spike, `dist/`, `pipeline/.venv/`, `pipeline/.coverage`, o cache do código do Readest (AGPL-3.0, não redistribuído) e `node_modules/` |
| `README.md` (raiz) | Runbook do ativo | 🟢 Lista as 14 tabelas de domínio com contagens desde a feature 001, o que resolve a dívida DT-01, e ganhou a seção «Dicionário para o KOReader (pipeline de build)», que remete a `pipeline/README.md`. 🟡 Não menciona o alvo Readest |
| `pipeline/README.md` | Runbook do pipeline | 🟢 Reprodução do zero, números esperados, exit codes, instalação no KOReader, seção completa do Readest, atualização deliberada do manifesto, arquitetura e troubleshooting com 13 sintomas |
| `spike/001-flexoes/README.md` | Runbook do spike | 🟢 Reprodução, fallback de RN-05 e regras obedecidas |

### 2. Regras operacionais embutidas

1. 🟢 A fonte de verdade é a cópia local do `.db`, com backup único em `gdrive:inculto-e-belo/`.
2. 🟢 Banco mudado exige atualização deliberada do manifesto em commit próprio; sem ela, o build para com `ContagemDivergenteError`.
3. 🟢 Artefatos derivados nunca entram no git (`dist/`, `spike/*/dist/`).
4. 🟢 O código de terceiros obtido para a conferência fica só em cache local, nunca versionado.
5. 🟡 Continua sem verificação automática de integridade pós-restauração do `.db`, mas o primeiro build depois da restauração faz esse papel na prática, porque confere esquema e contagens.

## Módulo `pipeline-nucleo`

Arquivos: `cli.py` (304 linhas), `erros.py` (69), `dominio/modelos.py` (170), `infra/repositorio.py` (391), `dominio/indice_flexoes.py` (89), `dominio/renderizacao.py` (127), `manifesto-integridade.json`.

### 1. Orquestração (`cli.py`)

🟢 `executar(db, manifesto, dist, cobertura, alvo)`:

1. **Pré-verificação**, só com o Readest no alvo: `ConferenciaReadest().preparar()` antes de gastar o build (D-14 da 003).
2. **Ingestão**: `RepositorioAurelio.validar()` confere o esquema e as contagens contra o manifesto.
3. **Índice**: `construir_mapa` sobre `flexions` e, com `--cobertura total`, também `conjugations`.
4. **Renderização em memória**, só com o Readest no alvo: dicionário `lema → HTML` com os 137.784 artigos (D-18), reaproveitado pelo KOReader no mesmo processo.
5. **Alvos** na ordem `koreader`, `readest`; o exit code é o **pior** entre eles (`max`).

Exit codes 🟢: `0` aprovado; `2` para `ErroPipeline` capturado em `main()`; `3` para artefato reprovado. Tabela de alvos: `koreader` (padrão), `readest`, `ambos`.

O `.ifo` do KOReader leva `date=time.strftime("%Y-%m-%d")`, a data do build. O do Readest leva `gerado_em` do manifesto (`_data_referencia`), estável enquanto o banco não muda. 🟢 Essa assimetria é deliberada: D-11 da 003 só alterou o alvo novo.

### 2. Ingestão (`infra/repositorio.py`)

🟢 O módulo é o **único dono do SQL** e abre o banco com `file:...?mode=ro` (URI) e `timeout=5`. Na abertura:
- arquivo ausente vira `BancoAusenteError`, com o comando `rclone` na mensagem;
- `locked` ou `busy` vira `BancoIndisponivelError`;
- qualquer outro `DatabaseError` vira `BancoCorrompidoError`.

`validar()`:
- confere `COLUNAS_REQUERIDAS` (12 tabelas; em `entries`, `most_used` passou a ser requerida) e reúne todas as divergências numa única `EsquemaInvalidoError`;
- conta as 12 tabelas e compara com o manifesto, levantando `ContagemDivergenteError` com instrução de commit próprio.

Consultas expostas, sem nunca vazar cursor ou SQL:

| Método | Retorno | Observação |
|--------|---------|------------|
| `headwords()` | `list[str]` | `SELECT DISTINCT lemma ... ORDER BY lemma`: 137.784 |
| `lemas_frequentes()` | `frozenset[str]` | Lemas com ao menos uma entrada `most_used = 1` (feature 003) |
| `flexoes()` / `conjugacoes()` | iterador `(id, head, forma_bruta)` | `ORDER BY id` |
| `textos_definicoes(lemma)` | `list[str]` | `content_text` de todas as acepções do lema, para as amostras de conteúdo |
| `artigos()` | iterador `(lema, list[Verbete])` | Agregados completos na ordem de fusão |

`ORDEM_FUSAO = "ORDER BY lemma, COALESCE(homonym, 999999), COALESCE(sort_key, ''), id"`: os homônimos de um lema chegam juntos e ordenados, e os sem número vão ao fim. 🟢 A montagem do agregado faz consultas por entrada, uma por nível da hierarquia. É deliberadamente simples: o build completo levou cerca de 12 s só com o KOReader e 68 s com os dois alvos.

### 3. Índice de flexões (`dominio/indice_flexoes.py`)

🟢 É domínio puro. `dividir_formas` aplica RB-14 (`re.compile(r",| ou ")`) e levanta `FormaAnomalaError` se encontrar forma vazia ou fragmento vazio, informando tabela e id. `construir_mapa(fontes, headwords, progresso)` classifica cada forma em ordem fixa:
1. **órfã**, quando a cabeça não é headword;
2. **idêntica**, quando forma e cabeça coincidem, numa comparação exata e sensível a diacríticos;
3. **duplicada**, quando o par `(forma, cabeça)` já foi visto;
4. **gravada**, nos demais casos.

A função verifica por `assert` a invariante **Σ entrada = gravadas + Σ descartes**. No banco atual, 1.045.742 formas de entrada (176.623 de `flexions`, depois do split, e 869.119 de `conjugations`) resultam em 774.003 gravadas, 748 órfãs, 220.563 duplicadas e 50.428 idênticas; 124.069 headwords têm formas.

### 4. Renderização (`dominio/renderizacao.py`)

🟢 `renderizar_artigo(lemma, verbetes, advertir)` é pura e abre sempre com `<b>lema</b>`, marca que o alvo Readest usa para identificar artigos. Homônimos viram seções numeradas (`<b>1.</b>`...) quando há mais de um. Cada seção traz:
- o cabeçalho, com a forma estilizada quando difere do lema, a classe legível (`word_class_summary` com segmentos vazios removidos) e o IPA;
- a etimologia em `<small>`;
- os blocos de classe em `<i>` e o `intro_text`;
- as acepções em `<ul><li>`, com número em negrito e rubrica em itálico;
- os exemplos: os do editor em `<i>`, as abonações em `<small><i>`, preservando RB-07;
- as notas, como `[Obs.: …]` nas acepções e `[Nota: …]` no verbete;
- as locuções, sob o título «Locuções»;
- a regência, sob «Regência (Luft)».

`content_html` entra sem escape, porque é HTML curado (RB-03); os textos simples passam por `html.escape`. Artigo acima de 1 MB gera só advertência (EC-05).

### 5. Erros nomeados (`erros.py`)

🟢 Todos herdam de `ErroPipeline` e terminam em exit 2:

| Grupo | Erros |
|-------|-------|
| Ingestão | `BancoAusenteError`, `BancoIndisponivelError`, `BancoCorrompidoError`, `EsquemaInvalidoError`, `ContagemDivergenteError`, `ManifestoAusenteError` |
| Índice | `FormaAnomalaError` |
| Escrita | `FalhaGeracaoError` |
| Leitura do artefato | `ArtefatoAusenteError`, `ArtefatoCorrompidoError` |
| Conferência | `AmbienteConferenciaError` |

🟡 O docstring de `aurelio_pipeline/__init__.py` ainda descreve só as camadas da feature 002 e não cita os módulos do Readest.

## Módulo `pipeline-koreader`

Arquivos: `infra/escrita_stardict.py` (128), `validacao/leitor_stardict.py` (112), `validacao/paridade.py` (186).

### 1. Escrita (`EscritorStarDict`)

🟢 É o adaptador do PyGlossary 5.4.1 e o **único acoplamento** à biblioteca no pipeline. Cada artigo entra como `newEntry([headword, *formas], html, defiFormat="h")`, e as formas viram chaves alternativas que o PyGlossary materializa no `.syn`. A escrita usa `formatName="Stardict"`, `dictzip=True` e `sametypesequence="h"`, com `bookname` igual a «Aurélio (uso pessoal)».

Depois de gravar, o adaptador confere os 4 arquivos e levanta `FalhaGeracaoError` se faltar algum; a ausência do `.dict.dz` indica python-idzip faltando, como prevê D-05. A troca é atômica: grava num diretório temporário, renomeia o anterior, renomeia o novo e apaga o anterior. Não há retenção de versão e não há gate antes da troca: **o artefato reprovado na paridade já está em `dist/aurelio-stardict/`**, e a proteção é o exit 3 com a mensagem «não instale».

### 2. Leitor próprio (`LeitorStarDict`)

🟢 É independente do PyGlossary, só com `gzip` e `struct`. Ele:
- exige os quatro arquivos;
- descomprime o `.dict.dz` inteiro;
- lê `.idx` (`palavra\0` + offset e tamanho de 32 bits big-endian) e `.syn` (`forma\0` + índice de 32 bits);
- valida a estrutura: terminador NUL, truncamento, UTF-8, offset além do corpo e índice do `.syn` fora do `.idx`.

Erros estruturais viram `ArtefatoCorrompidoError`. O mesmo leitor serve à validação do Readest.

### 3. Paridade (`executar_paridade`)

🟢 Tem tolerância zero e relatório integral. Os checks são:

| Check | O que confere |
|-------|---------------|
| `contagem-headwords` | Mesmo número e mesmo conjunto de headwords no `.idx` e no banco |
| `contagem-syn` | Número de entradas do `.syn` igual às formas gravadas |
| `metadados-ifo` | `wordcount`, `synwordcount` e `idxfilesize` declarados iguais aos reais |
| `amostra-verbetes` | 500 lemas (semente 20260703): cada `content_text` normalizado do banco aparece no texto do artigo |
| `amostra-flexoes` | 500 pares (semente 20260704): `(forma, headword)` presente no `.syn` |

A extração de texto do HTML remove tags sem pôr espaço, que é a mesma derivação do `content_text` do banco, e normaliza espaços. Último build: aprovado, com 137.784 e 774.003 entradas e 500 de 500 nas duas amostras.

## Módulo `pipeline-readest`

Arquivos: `dominio/agrupamento_readest.py` (133), `infra/escrita_readest.py` (245), `validacao/paridade_readest.py` (294), `infra/conferencia_readest.py` (284), `conferencia_readest/conferir.ts` (111), `conferencia_readest/fonte-readest.json`, `package.json` e `package-lock.json`.

### 1. Agrupamento (`agrupar`)

🟢 É domínio puro e parte de quatro primitivas:
- `chave_readest(texto) = texto.lower()`: duas grafias com a mesma chave são, para o Readest, a mesma palavra;
- `ordem_readest(texto) = texto.lower().encode("utf-16-be")`: reproduz o `cmpAscii` do Readest, que compara unidades UTF-16;
- `tem_letra`: procura um caractere de palavra que não seja dígito nem sublinhado;
- `_dobrar`: remove diacríticos (NFD) e põe em minúsculas.

O algoritmo:
1. Cada lema entra na sua chave; cada forma **com letra** entra na chave da forma, apontando para o lema. As formas sem letra são descartadas (RN-06; 261 formas «/» de verbos defectivos), e lemas nunca são descartados.
2. A sequência de artigos de cada chave é ordenada por `_ordem_na_pagina`: primeiro os lemas coincidentes com a chave, com a grafia exata à frente; depois os de vocabulário frequente; o desempate é alfabético sem diacríticos e, por fim, pela grafia.
3. O destino de cada chave no índice segue esta tabela:

| Situação | Destino | Grafia gravada |
|----------|---------|----------------|
| Chave de lema | `idx-lema` | O primeiro lema da sequência |
| Forma de dois ou mais lemas | `idx-forma-combinada` | A própria chave, se for uma das grafias da forma; senão a menor grafia |
| Forma de um só lema cuja página de lema é combinada | `idx-forma-direta` | Idem; aponta só para o artigo do lema, dentro da página combinada (RN-03) |
| Forma de um só lema cuja página de lema é simples | `syn` | Idem; aponta para a entrada do lema no `.idx` |

A função verifica por `assert` que `chaves == idx + syn`. Último build: 887.546 chaves, das quais 864.633 têm página simples e 22.913 página combinada, com 16.910 sequências distintas. Os artigos por página se distribuem assim: 21.891 páginas com 2, 979 com 3, 41 com 4 e 2 com 5. No índice, o `.idx` tem 160.302 entradas (137.652 lemas, 9.101 formas combinadas e 13.549 formas diretas) e o `.syn` tem 727.244. Os 137.652 lemas do `.idx`, contra 137.784 headwords, refletem as 132 colisões de caixa fundidas numa chave só.

### 2. Escritor próprio (`EscritorReadest`)

🟢 Usa stdlib e python-idzip, sem PyGlossary, porque o Readest exige a ordem do `cmpAscii` e entradas que apontam para trechos já gravados. Antes de gravar, `_conferir_entrada` recusa grafias com tabulação, quebra de linha ou NUL e lemas do plano sem artigo renderizado.

O corpo é montado assim:
1. As páginas de lema são gravadas na ordem do índice; dentro de cada uma, registra-se a posição exata do artigo do próprio lema, para servir às formas diretas.
2. Em seguida vêm as sequências combinadas de formas ainda não gravadas, **uma vez por sequência distinta** (D-08).

Os artigos de uma página são separados por `<hr>` (D-10). O `.syn` só aponta para entradas do `.idx` cuja sequência é idêntica à da forma, com `FalhaGeracaoError` como salvaguarda.

O `.ifo` é determinístico:
- `version=3.0.0`, `bookname=Aurélio (uso pessoal, Readest)` e `sametypesequence=h`;
- `date` igual à data do manifesto;
- `description` terminando em «Versão do conteúdo <impressão>», em que a impressão digital são os 16 primeiros hexadecimais do SHA-256 de `idx + syn + corpo`.

O gzip é gravado com `mtime=0` (RN-09). O artefato nasce em `dist/.readest-preparo-*`, junto com `expectativa-conferencia.tsv`, que tem uma linha `grafia\toffset\ttamanho` por chave do `.idx` e do `.syn`.

A promoção é condicionada (D-15):
- `promover` remove a expectativa e troca `dist/readest/` atomicamente;
- `reprovar` move o preparo inteiro para `dist/readest.reprovado/` e mantém intacta a versão aprovada anterior;
- `descartar`, usada em erro de ambiente ou de execução, apaga o preparo sem guardar nada.

Último build: 140.750 trechos, corpo de 73.747.274 B e impressão `d4bc5db7f94992ba`.

### 3. Validação independente (`executar_validacao_readest`)

🟢 Não importa o agrupamento nem o escritor: `paginas_esperadas` recalcula as páginas a partir de headwords, mapa e frequentes. Ela simula a busca do Readest por bisseção no `.idx` e, se não achar, no `.syn`. Cada página é recortada em `<hr>`, e cada artigo é identificado pelo `<b>…</b>` de abertura.

Nove checks, com contagem integral e até 50 detalhes por check:

| Check | O que confere |
|-------|---------------|
| `ordem-idx`, `ordem-syn` | Ordem estrita na comparação do Readest |
| `unicidade-cruzada` | Nenhuma chave nos dois índices |
| `nfc` | Grafias em NFC |
| `pagina-artigos` | Todas as chaves esperadas abrem exatamente os artigos esperados, na ordem |
| `chaves-inesperadas` | Nenhuma chave sem página esperada |
| `acesso-isolado-sem-copia` | Forma de um só lema aponta para dentro da página do lema |
| `metadados-ifo` | Contagens, versão, bookname, `sametypesequence`, data e impressão digital recalculada |
| `amostra-conteudo` | 500 lemas (semente 20261015) com todas as definições presentes |

Último build: aprovado, com 887.546 de 887.546 páginas certas e 500 de 500 na amostra.

### 4. Conferência com o código do Readest (`ConferenciaReadest` + `conferir.ts`)

🟢 `preparar()` é idempotente e faz três coisas:
1. `verificar_ambiente` exige Node ≥ `node_minimo` (22.18), comparando maior e menor versão, e npm presente.
2. `_cache_valido` confere o marcador `.pronto` e os SHA-256 dos reescritos. Se o cache não vale, `_obter` baixa os dois arquivos do commit fixado por `raw.githubusercontent.com`, com timeout de 30 s, e confere o SHA-256 dos originais. Aplica então as três reescritas mecânicas, cada uma exigindo exatamente uma ocorrência, confere o SHA-256 do resultado e só depois grava o cache e o marcador.
3. `_modulos_validos` exige o `fflate` na versão fixada; sem ele, roda `npm ci --no-audit --no-fund`, com timeout de 300 s.

Toda falha nessa etapa vira `AmbienteConferenciaError`, com instrução acionável.

`conferir()` executa `node conferir.ts <artefato> <basename> <expectativa>` com timeout de 600 s; estourar o tempo é veredito reprovado, não erro. Os códigos de saída 0 e 1 são vereditos; qualquer outro, ou uma saída que não seja JSON, é erro de ambiente.

`conferir.ts` faz o mesmo que o provedor do Readest:
- carrega o artefato com o `StarDictReader` real;
- para cada chave da expectativa, chama `lookup` e, se falhar, `resolveSynonym`, e compara offset e tamanho;
- relê cada trecho distinto pelo leitor por blocos e o compara com a descompressão integral do `fflate`.

Último build: 887.546 de 887.546 chaves e 147.263 trechos íntegros, em 41,6 s, com Node v26.10.0.

### 5. Ordem do gate

🟢 O alvo Readest percorre: agrupamento → escrita no preparo → `relatorio-agrupamento.json` → validação → `validacao-readest.json` → conferência → `conferencia-readest.json` → promoção ou reprovação. Uma exceção em qualquer ponto depois da escrita descarta o preparo e é relançada.

## Módulo `spike-001-flexoes`

🟢 `spike/001-flexoes/gerar_spike.py` (428 linhas) é autocontido e não importa o pipeline. Ele:
- reimplementa a conexão `mode=ro`, a divisão RB-14, os descartes classificados e a escrita via PyGlossary;
- gera índices em escala real (137.784 headwords e 774.003 formas) com **corpo trivial**, exceto para os 22 lemas de `ROTEIRO_LEMAS`, tirados do roteiro de medição de 20 palavras,, que recebem o verbete completo;
- aceita as opções `--piloto` (só os lemas do roteiro) e `--cobertura flexions-somente` (fallback de RN-05);
- grava em `spike/001-flexoes/dist/aurelio-spike/`, fora do git.

O veredito registrado é **GO presumido** por decisão do usuário, sem medição no Boox (`_reversa_forward/001-spike-de-flexoes/spike-report.md`). O código ficou como evidência reprodutível; o pipeline de produção substituiu-o funcionalmente. 🟡 A lógica do índice está duplicada entre o spike e `dominio/indice_flexoes.py`, uma duplicação aceita por ser descartável.

## Resumo para o Reversa

- **Módulos analisados:** 6 de 6.
- **Algoritmos principais:**
  - classificação de formas com invariante de conservação;
  - fusão de homônimos por lema;
  - renderização HTML hierárquica;
  - agrupamento por chave na comparação do Readest, com ordenação editorial de artigos e roteamento entre `.idx` e `.syn`;
  - escrita StarDict com trechos compartilhados e impressão digital do conteúdo;
  - validação por busca simulada;
  - conferência com o código real do leitor;
  - promoção condicionada.
- **Entidades:**
  - 14 tabelas de domínio;
  - 13 classes de dados em `modelos.py`, mais o `ParityReport` de `validacao/paridade.py`;
  - 5 artefatos JSON de relatório;
  - 3 arquivos de configuração versionados: o manifesto, a fonte fixada e o lockfile npm.
- **Lacunas e observações:**
  - 🟡 semântica de `most_used`, agora com efeito;
  - 🟡 README da raiz e docstring do pacote sem o alvo Readest;
  - 🟡 o KOReader troca o artefato antes do veredito da paridade.
