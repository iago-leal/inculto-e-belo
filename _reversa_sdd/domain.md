# Domínio — inculto-e-belo

> Gerado pelo reversa-detective em 2026-07-03; re-extraído em 2026-10-15, depois das features 001, 002 e 003 do ciclo forward
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. O que o sistema é (uma frase)

🟢 O sistema é um léxico completo do Aurélio, normalizado em SQLite e mantido somente-leitura, do qual um pipeline Python gera dois dicionários StarDict de uso estritamente pessoal. O primeiro serve ao KOReader, com um artigo por lema e as formas flexionadas no `.syn`; o segundo serve ao Readest, com uma página por palavra reunindo todos os verbetes correspondentes. Cada dicionário só vale depois de aprovado num gate automático.

## 2. Glossário de domínio

### Do léxico

| Termo | Definição | Onde vive |
|-------|-----------|-----------|
| **Verbete (entry)** | Unidade editorial: lema, pronúncia, etimologia e blocos de acepções | `entries` |
| **Lema (lemma)** | Forma canônica de citação, com diacríticos; chave conceitual de todo o banco | `entries.lemma` |
| **Homônimo** | Verbetes distintos com o mesmo lema, discriminados por `homonym`; 4.585 lemas nessa condição | `entries.homonym` |
| **Slug** | Forma normalizada sem diacríticos | `entries.slug`, `flexions.*_slug` |
| **Bloco de classe** | Agrupamento das acepções por classe gramatical dentro do verbete | `word_class_blocks` |
| **Acepção (definition)** | Sentido numerado dentro de um bloco, com rubrica opcional | `definitions` |
| **Rubrica** | Marca de domínio, registro ou regionalismo da acepção; 2.655 distintas | `rubrics` |
| **Exemplo** | Abonação de uso: `editor` (do lexicógrafo) ou `citation` (literária) | `examples.kind` |
| **Locução** | Expressão fixa subordinada ao verbete, com definições próprias | `locutions`, `locution_definitions` |
| **Regência verbal** | Transitividade e preposições por acepção, fonte Luft | `verb_rection` |
| **Flexão** | Forma nominal derivada, ligada à cabeça por texto | `flexions` |
| **Conjugação** | Forma verbal (13 tempos, até 6 pessoas), ligada ao infinitivo por texto | `conjugations` |
| **Forma órfã** | Flexão ou conjugação cujo lema-alvo não existe em `entries.lemma`: 22 lemas, 748 formas | derivada |
| **Marca ortográfica** | Grafia anterior ao acordo ortográfico, com regra explicativa | `orthographic_marks/rules` |
| **Vocabulário frequente** | 🟡 Verbete marcado com `most_used = 1` (3.039); ordena artigos nas páginas do Readest | `entries.most_used` |

### Do pipeline e dos artefatos

| Termo | Definição | Onde vive |
|-------|-----------|-----------|
| **Alvo** | Leitor de destino de um artefato: `koreader` (padrão) ou `readest`; `ambos` gera os dois numa execução | `cli.py` |
| **Headword** | Entrada do `.idx` do KOReader: um lema com os homônimos fundidos num artigo | `dist/aurelio-stardict/` |
| **Artigo** | HTML integral de um lema, aberto por `<b>lema</b>`, com homônimos em seções numeradas | `dominio/renderizacao.py` |
| **`.syn`** | Índice StarDict de formas alternativas, cada uma apontando para uma entrada do `.idx` | artefatos |
| **Manifesto de integridade** | Contagens esperadas das 12 tabelas consumidas, mais a data de referência do banco | `pipeline/manifesto-integridade.json` |
| **Relatório de cobertura** | Contabilidade das formas: entrada, gravadas e descartes por classe (órfã, idêntica, duplicada) | `relatorio-cobertura.json` |
| **Paridade** | Gate do KOReader: comparação de tolerância zero entre banco e artefato | `validacao/paridade.py` |
| **Chave do Readest** | Texto em minúsculas; duas grafias com a mesma chave são, para o Readest, a mesma palavra | `dominio/agrupamento_readest.py` |
| **Comparação do Readest (`cmpAscii`)** | Ordem por unidades UTF-16 das minúsculas, usada na busca binária do leitor | idem |
| **Página** | O que uma chave do Readest abre: um artigo (simples) ou vários separados por `<hr>` (combinada) | `dist/readest/` |
| **Sequência distinta** | Lista ordenada de lemas de uma página combinada; cada uma é gravada uma vez no corpo | `infra/escrita_readest.py` |
| **Forma direta** | Forma de um só lema cuja página de lema é combinada; aponta só para o artigo do lema dentro dela | idem |
| **Forma sem letra** | Forma sem nenhuma letra («/» de verbos defectivos): 261, descartadas no Readest | relatório de agrupamento |
| **Impressão digital do conteúdo** | 16 primeiros hexadecimais do SHA-256 de `.idx + .syn + corpo`; vai na `description` do `.ifo` | idem |
| **Validação** | Primeira etapa do gate do Readest: recálculo independente e busca simulada, tolerância zero | `validacao/paridade_readest.py` |
| **Conferência** | Segunda etapa do gate do Readest: o código de busca real do Readest, executado no Node | `infra/conferencia_readest.py`, `conferir.ts` |
| **Fonte fixada** | Commit e hashes do código do Readest usado na conferência | `conferencia_readest/fonte-readest.json` |
| **Preparo / promoção** | Diretório temporário onde o artefato do Readest nasce; só sobe para `dist/readest/` se aprovado | `dist/.readest-preparo-*` |

## 3. Regras de negócio

### Do schema (🟢 CONFIRMADO)

1. **RB-01:** acepção nunca pertence diretamente ao verbete; pertence sempre a um bloco de classe gramatical (`definitions.word_class_block_id NOT NULL`).
2. **RB-02:** homonímia é preservada no banco: cada homônimo é uma linha própria de `entries`. A fusão é decisão do consumidor e acontece só no artefato:
   - o KOReader funde os homônimos de um lema num artigo;
   - o Readest vai além e une, numa página, homônimos e homógrafos entre lemas e formas.
3. **RB-03:** todo conteúdo textual existe em par exibição/busca (`content_html` / `content_text`). As tags de exibição limitam-se a `<em>`, `<u>` e `<strong>`; em particular, o banco não contém `<hr>`, que o Readest usa como fronteira entre artigos.
4. **RB-04:** a ordem editorial é dado explícito (`position`), nunca a ordem física de inserção.
5. **RB-05:** flexões e conjugações ligam-se ao verbete **por texto** (`entry_head`/`infinitive` ↔ `lemma`), sem constraint física. A integridade referencial cabe ao consumidor e tem 22 violações conhecidas: 11 infinitivos e 11 cabeças órfãs, que somam 748 formas.
6. **RB-06:** a busca textual do banco ignora diacríticos (`remove_diacritics 2`); as acepções usam também stemming Porter.
7. **RB-07:** o exemplo distingue a voz do lexicógrafo (`editor`) da abonação literária (`citation`). O renderizador preserva a distinção: o exemplo do editor vai em itálico, e a abonação em itálico reduzido.
8. **RB-08:** a regência tem fonte única declarada (`source='luft'`) e é exibida sob o título «Regência (Luft)».

### Da operação e das decisões registradas (🟢 em documento ou código, 🟡 quando inferida)

9. **RB-09** 🟢: o `.db` jamais entra no git. O backup é único, via rclone, em `gdrive:inculto-e-belo/`, e a fonte de verdade é a cópia local. A política se estende a `dist/`, aos ambientes locais e ao cache do código do Readest.
10. **RB-10** 🟢: o banco é **somente-leitura** em todo o ciclo forward, nos dois alvos e no spike. O pipeline o abre exclusivamente por URI `mode=ro` em `infra/repositorio.py`, e `entries.most_used` é apenas lida. Órfãs e anomalias são reportadas, nunca corrigidas.
11. **RB-11** 🟢: o conteúdo está sob direitos autorais do Aurélio, e todo artefato derivado é de uso estritamente pessoal, nunca publicado. A regra se traduz em quatro garantias:
    - o `bookname` leva «uso pessoal»;
    - `dist/` fica fora do git;
    - os testes usam só dados sintéticos, sem conteúdo do Aurélio no repositório;
    - o artefato do Readest só é armazenado na nuvem privada da conta do usuário, o que **não constitui publicação** (RN-08 da feature 003, decisão do usuário em 2026-10-15).
12. **RB-12** 🟢: a regeneração dos artefatos é determinística e auditável. Cada build grava relatórios JSON: cobertura e paridade no KOReader; agrupamento, validação e conferência no Readest. A invariante de cobertura (entrada = gravadas + descartes) e as sementes das amostras ficam registradas. No Readest, duas gerações sobre o mesmo banco produzem bytes idênticos nos quatro arquivos, e o `.ifo` leva a data do manifesto e a impressão digital do conteúdo. O `.ifo` do KOReader, por outro lado, leva a data do build.
13. **RB-13** 🟡: o projeto opera sob mantenedor único intermitente, e todo processo precisa ser retomável por README. Os runbooks são `README.md`, `pipeline/README.md` e `spike/001-flexoes/README.md`.
14. **RB-14** 🟢: `flexions.flexion` pode conter **múltiplas formas numa linha**, separadas por `,` (1.349 linhas) ou `" ou "` (15 linhas). Os consumidores dividem antes de indexar; o pipeline faz isso em `dominio/indice_flexoes.py`, com teste, e o spike tem cópia própria. `conjugations` não tem o fenômeno, e não há formas vazias.

### Do pipeline (🟢 CONFIRMADO no código, salvo indicação)

15. **RB-15:** a ingestão só expõe dados depois de conferir o esquema (12 tabelas, colunas requeridas) e as contagens contra o manifesto. Banco mudado exige atualizar o manifesto em **commit próprio**; até lá, o build para com `ContagemDivergenteError` (exit 2).
16. **RB-16:** toda forma de entrada recebe exatamente uma classificação, avaliada nesta ordem: órfã (cabeça fora dos headwords), idêntica (forma igual à cabeça, em comparação exata), duplicada (par já visto) ou gravada. A soma se conserva.
17. **RB-17:** o KOReader é o alvo padrão. Seu artefato tem 137.784 headwords e 774.003 formas e não mudou com a chegada do Readest (RN-01 da 003). O `[regen]` do Harness gera só esse alvo, porque o encerramento de sessão não deve depender de Node nem de rede.
18. **RB-18:** o gate do KOReader é a paridade de tolerância zero, que confere contagens, metadados do `.ifo` e duas amostras de 500 com sementes fixas. Artefato reprovado sai com exit 3 e **não deve ser instalado**. 🟡 Ele já estará em `dist/aurelio-stardict/`, porque a troca precede o veredito.
19. **RB-19:** no Readest, cada chave abre **exatamente** os artigos de todos os lemas a que corresponde, sem faltar nem sobrar (RN-02 e RN-03 da 003). A correspondência ignora a caixa, como faz o leitor.
20. **RB-20:** na página do Readest, os artigos seguem esta ordem (RN-04 da 003):
    - primeiro os lemas coincidentes com a chave, com a grafia exata à frente;
    - depois os de vocabulário frequente;
    - o desempate é alfabético, sem diacríticos nem caixa, e por fim pela grafia.
21. **RB-21:** formas sem nenhuma letra ficam fora do Readest e são listadas no relatório; lemas nunca são descartados (RN-06 da 003).
22. **RB-22:** nenhum artefato do Readest é entregue sem validação **e** conferência aprovadas (RN-07 da 003). O reprovado vai inteiro para `dist/readest.reprovado/`, e a versão aprovada anterior fica intacta. Em erro de ambiente, nada é promovido nem guardado.
23. **RB-23:** a conferência usa o código de busca do Readest fixado por commit, com SHA-256 dos originais e dos arquivos reescritos. Hash divergente é erro que não se contorna; atualizar a versão fixada é procedimento documentado no README.
24. **RB-24** 🟡: ao executar um build, o operador lê os exit codes como contrato: 0 permite instalar ou importar, 2 exige corrigir o ambiente ou o banco, 3 proíbe instalar e manda ler os relatórios. Com dois alvos, vale o pior.

## 4. Invariantes quantitativas

### Banco (baseline 2026-07-03, inalterada)

| Invariante | Valor | Uso |
|------------|-------|-----|
| Entries / lemas únicos | 143.376 / 137.784 | `wordcount` do KOReader |
| Formas de flexão / conjugação (linhas) | 175.259 / 869.119 | Entrada do índice de flexões |
| Formas depois do split RB-14 | 176.623 + 869.119 = 1.045.742 | Entrada do relatório de cobertura |
| Órfãs conhecidas | 22 lemas (11 infinitivos e 11 cabeças), 748 formas | Contrato de descarte |
| Acepções / blocos | 259.337 / 168.361 | Paridade em re-extrações |
| Vocabulário frequente | 3.039 entries com `most_used = 1` | Ordem das páginas do Readest |

### Alvo KOReader (`dist/aurelio-stardict/`)

| Invariante | Valor |
|------------|-------|
| `wordcount` / `synwordcount` | 137.784 / 774.003 |
| Descartes | 748 órfãs, 220.563 duplicadas, 50.428 idênticas |
| Headwords com formas | 124.069 |

### Alvo Readest (`dist/readest/aurelio-readest/`)

| Invariante | Valor |
|------------|-------|
| Chaves pesquisáveis | 887.546 |
| `.idx` | 160.302 (137.652 chaves de lema, 9.101 formas combinadas, 13.549 formas diretas) |
| `.syn` | 727.244 |
| Páginas combinadas / sequências distintas | 22.913 / 16.910 |
| Artigos por página combinada | 21.891 com 2, 979 com 3, 41 com 4, 2 com 5 |
| Formas sem letra descartadas | 261 |
| Colisões de caixa entre lemas | 132 (137.784 − 137.652) |
| Trechos no corpo / corpo descomprimido | 140.750 / 73.747.274 B |
| Impressão digital do conteúdo | `d4bc5db7f94992ba` |

## 5. TODOs e intenções não implementadas

- 🟢 A distribuição por WebDAV (P-05, `sdd/distribuicao-webdav.md`) não foi implementada. A instalação no KOReader é manual, por cópia; a importação no Readest é manual, com sincronização pela nuvem da conta.
- 🟡 O README da raiz descreve só o alvo KOReader, e o docstring de `aurelio_pipeline/__init__.py` não cita os módulos do Readest. O runbook completo está em `pipeline/README.md`.
- 🟡 A latência no Boox Air 4C nunca foi medida; o veredito do spike é GO presumido, com monitoramento nas primeiras leituras e fallback `--cobertura flexions-somente`.
- 🟡 A visibilidade do divisor `<hr>` no tema escuro do Readest não teve conferência visual explícita (O-05 da 003).
- 🟡 O Readest instalado no Mac é a 0.12.12, e a conferência está fixada na 0.12.16. Os arquivos de busca das duas versões são idênticos, e uma versão futura que mude a busca exige atualizar a fonte fixada.

## 6. Lacunas 🔴

Nenhuma lacuna 🔴 nesta re-extração. Situação das lacunas registradas em 2026-07-03:

| # | Lacuna original | Situação |
|---|-----------------|----------|
| L-01 | Semântica de `flexions.type` | 🟢 1=plural, 2=feminino, 3=feminino plural, 4=diminutivo, 5=aumentativo |
| L-02 | Semântica de `entries.head_type` | 🟢 1=palavra, 2=letra/sigla/símbolo, 3=afixo, 4=locução/expressão estrangeira |
| L-03 | Mapa de `conjugations.tense` | 🟢 1–13 nomeados (`data-dictionary.md` §conjugations) |
| L-04 | Critério de `entries.most_used` | 🟡 Vocabulário básico ou frequente; o critério editorial exato segue inferido. Desde a feature 003 a marca tem efeito: se mudar de sentido numa versão nova do banco, a ordem das páginas do Readest muda sem erro (O-03 da 003) |

O achado RB-14, da revisão de 2026-07-03, passou para a §3 como regra.
