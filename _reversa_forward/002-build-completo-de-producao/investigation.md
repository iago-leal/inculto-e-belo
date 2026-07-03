# Investigation — 002-build-completo-de-producao

> Data: 2026-07-03 · Pesquisa de fundo do `/reversa-plan`
> A maior parte da investigação desta feature já foi paga pelo spike 001; este documento consolida o que se sabe, de onde veio, e o pouco que restou a verificar durante a implementação.

## 1. O que o spike já respondeu (evidência empírica, 🟢)

Fonte: `_reversa_forward/001-spike-de-flexoes/spike-report.md` e `spike/001-flexoes/gerar_spike.py` (referência de leitura, RN-08).

| Pergunta                                                | Resposta                                                                                                               | Consequência para o build                                                                    |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| O mecanismo `.syn` funciona no KOReader em escala real? | Sim — 774.003 formas, 20/20 do roteiro no sdcv embutido do KOReader macOS                                              | Arquitetura do índice confirmada; nada a re-investigar                                       |
| Como o PyGlossary materializa o `.syn`?                 | Chaves alternativas em `l_word` no `newEntry`/`addEntry`; `synwordcount` sai coerente no `.ifo`                        | D-04 do roadmap                                                                              |
| PyGlossary escreve em streaming ou memória?             | Em memória: 462 MB de pico com corpo trivial + 774 mil alternates                                                      | Streaming dos `Verbete` na leitura basta; sem chunking na escrita (D-03)                     |
| dictzip funciona out-of-the-box?                        | **Não** — exige `python-idzip==0.3.9`; sem ele degrada silenciosamente para `.dict`                                    | D-05: pinar e verificar o `.dict.dz` pós-build                                               |
| O lookup normaliza caixa/diacríticos?                   | Não no modo exato; fuzzy resgata                                                                                       | RN-07: formas gravadas como estão no banco, sem variantes                                    |
| Que HTML o popup renderiza?                             | `<b> <i> <u> <p> <ul> <li> <small>` ok no desktop                                                                      | D-06: vocabulário do renderizador                                                            |
| Ordem de fusão de homônimos                             | `ORDER BY lemma, COALESCE(homonym, 999999), COALESCE(sort_key, ''), id` produziu artigos corretos (coração ×3, mão ×3) | Reutilizar a mesma ordenação no repositório                                                  |
| RB-14 na prática                                        | Split por regex `,                                                                                                     | ou `sobre`flexions.flexion`; `conjugations` limpo; zero formas vazias (EC-04 nunca disparou) | Mesma regra no domínio, com o teste de unidade que o spike não tinha |

## 2. Formato StarDict para o parser de leitura próprio (D-07)

Fonte: documentação do formato no repositório do PyGlossary (`doc/p/stardict.md`) e o próprio artefato do spike como fixture real. Estrutura relevante para `validacao/leitor_stardict.py`:

- **`.ifo`** — texto UTF-8, primeira linha `StarDict's dict ifo file`, pares `chave=valor` (`version`, `wordcount`, `synwordcount`, `idxfilesize`, `bookname`, `sametypesequence`, `date`).
- **`.idx`** — sequência de registros: `palavra\0` (UTF-8) + `offset` (uint32 big-endian) + `size` (uint32 big-endian), ordenados por `g_ascii_strcasecmp`-like (a ordenação é do escritor; o leitor só percorre). `idxfilesize` do `.ifo` deve bater com o tamanho real do arquivo.
- **`.syn`** — sequência de registros: `forma\0` (UTF-8) + `índice do headword no .idx` (uint32 big-endian). `synwordcount` deve bater com o número de registros.
- **`.dict.dz`** — dictzip, que é **gzip válido com campo extra RA** (random access); o módulo `gzip` da stdlib descomprime o arquivo inteiro sem entender o campo extra. Para a validação (extração de ~500 artigos), descomprimir o `.dict` inteiro em memória uma vez (< 200 MB estimado) e fatiar por offset/size é mais simples e rápido que implementar acesso randômico por chunks — decisão de implementação registrada.
- Com `sametypesequence=h`, o conteúdo de cada fatia é o HTML do artigo puro (sem byte de tipo por entrada).

Verificação estrutural (RF-07 da spec de paridade): offsets estritamente não-decrescentes, `offset+size ≤ len(dict)`, strings decodáveis em UTF-8, contagens = declaradas.

## 3. Alternativas avaliadas e descartadas

| Alternativa                                      | Onde foi considerada                       | Por que foi descartada                                                                                    |
| ------------------------------------------------ | ------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| Writer StarDict próprio (~300 linhas, zero deps) | Decision log de `conversao-formato.md#15`  | PyGlossary pinado já resolve ordenação/offsets/dictzip; menos código próprio para mantenedor intermitente |
| Validar com sdcv externo                         | Decision log de `validacao-paridade.md#15` | Dependência de sistema não pinável; parser stdlib é trivial para leitura                                  |
| Validar lendo com o PyGlossary                   | idem                                       | Circularidade: defeito da biblioteca afetaria escrita e leitura igualmente                                |
| Hunspell/MorphoBr para flexões                   | Decision log de `indice-de-flexoes.md#15`  | O banco já traz as formas ligadas aos verbetes reais (99,9% de casamento)                                 |
| Hash por tabela no manifesto                     | OQ-01 de `ingestao-aurelio`                | Resolvida na sessão de esclarecimentos: só contagens (§9 do requirements)                                 |
| Retenção de artefato anterior                    | Lacuna implícita                           | Resolvida: substituição atômica sem retenção; rebuild é o rollback                                        |

## 4. Pontos que a implementação ainda deve confirmar (🟡, baratos)

1. **Extração de texto do artigo para a amostra de paridade (D-08):** strip de tags por regex simples (`<[^>]+>`) + `html.unescape` + colapso de whitespace deve bastar, dado o vocabulário fechado de tags do renderizador; confirmar com fixture real de verbete rico (ex.: `abacaxi`, `coração`). Se regex se mostrar frágil, `html.parser.HTMLParser` da stdlib é o plano B sem dependência nova.
2. **Projeção de memória com corpo integral:** 462 MB (spike) → estimar +HTML de 259.337 acepções, 54.726 exemplos, 22.168 locuções; esperado < 1,5 GB. Medir com `/usr/bin/time -l` no primeiro build (risco já tabelado no roadmap §9).
3. **`notes.parent_type`:** o spike consultou `parent_type='definition'` e `'entry'`; confirmar no dicionário de dados (`_reversa_sdd/data-dictionary.md`) se há outros valores com conteúdo relevante ao verbete.
4. **Tamanho final do `.dict.dz`:** estimativa < 250 MB por compressão ~3-4× de texto; medir e registrar no relatório de build.

## 5. Fontes externas

- PyGlossary 5.4.1 — https://github.com/ilius/pyglossary (formato StarDict em `doc/p/stardict.md`)
- Suporte a dicionários do KOReader — https://github.com/koreader/koreader/wiki/Dictionary-support
- python-idzip 0.3.9 — https://pypi.org/project/python-idzip/ (dictzip writer usado pelo PyGlossary)
- uv — https://docs.astral.sh/uv/ (gerenciador já em uso no spike)
