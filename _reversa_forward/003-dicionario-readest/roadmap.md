# Roadmap: Dicionário do Aurélio para o Readest

> Identificador: `003-dicionario-readest`
> Data: `2026-10-15`
> Requirements: `_reversa_forward/003-dicionario-readest/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

O pipeline de `pipeline/` ganha um segundo alvo, o Readest, que reaproveita a ingestão (`infra/repositorio.py`), o índice de flexões (`dominio/indice_flexoes.py`) e a renderização (`dominio/renderizacao.py`) sem alterá-los, e acrescenta três peças. A primeira é uma função de domínio pura que decide, para cada palavra pesquisável, quais artigos a página mostra e em que ordem. A segunda é um escritor StarDict próprio, em stdlib mais o `python-idzip` já pinado, porque o PyGlossary não grava índice na ordem do Readest nem entradas que apontam para um trecho de página já gravada. A terceira é um gate de duas etapas: a validação independente em Python e a conferência com o código de busca do próprio Readest, em versão fixada, executado no Node.js. O artefato nasce num diretório de preparo e só é promovido para `dist/readest/` quando as duas etapas aprovam. O alvo KOReader, com PyGlossary, segue intocado e continua sendo o padrão da CLI.

## 2. Princípios aplicados

`.reversa/principles.md` não existe neste projeto. Valem os mesmos princípios operacionais adotados no roadmap da feature 002, já incorporados como requisitos não funcionais:

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Estabilidade > novidade | Nenhuma biblioteca Python nova; o escritor usa stdlib e o `python-idzip==0.3.9` já pinado. A conferência introduz dependência de execução nova (Node.js, rede na primeira obtenção), aceita pelo usuário em 2026-10-15 (`requirements.md#9`) e contida por versão fixada do Readest, SHA-256 de cada arquivo baixado e `package-lock.json` versionado | respeita, com tensão registrada |
| Erros barulhentos > performance | Erros nomeados para ambiente ausente, download divergente e artefato reprovado; tolerância zero nas duas etapas do gate; nenhum descarte silencioso (as 261 formas sem letra saem contadas no relatório) | respeita |
| Retomabilidade (mantenedor intermitente) | README com geração, números esperados, importação e atualização no Readest; versões e hashes no repositório; relatórios JSON por execução | respeita |
| Rigor de aplicação (camadas, domínio testado) | Agrupamento puro em `dominio/`, escrita isolada em `infra/`, validação sem PyGlossary nem código do agrupamento; testes com dados sintéticos | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Escritor StarDict próprio para o alvo Readest em `infra/escrita_readest.py` (stdlib + `idzip.compressor.compress`); PyGlossary continua restrito ao alvo KOReader | O artefato exige índices na ordem de comparação do Readest (RN-05) e entradas de forma apontando para um sub-trecho de página combinada (RF-03); o PyGlossary grava um corpo por entrada e ordena pelo critério do formato | Pós-processar o artefato do PyGlossary (reescreve todos os arquivos de qualquer modo e acopla a detalhe interno da biblioteca); PyGlossary com chave de ordenação alternativa (não resolve as páginas compostas) | 🟢 |
| D-02 | Agrupamento como função pura em `dominio/agrupamento_readest.py`: recebe headwords, o mapa de `construir_mapa` e o conjunto de lemas frequentes; devolve o plano de páginas (chave → sequência ordenada de lemas) e o relatório de agrupamento | RF-02 exige domínio puro testável sem banco; o mapa de flexões já validado no alvo KOReader é a única fonte de formas | Agrupar dentro do escritor (mistura regra de domínio com I/O); agrupar em SQL (regra fora do domínio, contra a spec `ingestao-aurelio`) | 🟢 |
| D-03 | Chave de comparação = `s.lower()`, ordenada por unidades UTF-16 (`encode("utf-16-be")`), espelho exato de `cmpAscii` do Readest; `.idx` e `.syn` estritamente crescentes nessa comparação | É a comparação que a busca binária do Readest usa nos dois índices (`stardictReader.ts`, v0.12.16); a ordem canônica do StarDict deixou «à», «à clef», «à clé» e «Å» inalcançáveis | Ordem canônica do formato (é a causa das quatro entradas inalcançáveis) | 🟢 |
| D-04 | Formas sem nenhuma letra (`[^\W\d_]` ausente) são descartadas e contadas no relatório; lemas nunca são descartados | RN-06; a medição de 2026-10-15 achou só as 261 «/» de verbos defectivos | Descartar também lemas sem letra (não pedido; o KOReader os mantém) | 🟢 |
| D-05 | Ordem na página: (1) lemas que coincidem com a chave, com o grafado exatamente como a chave à frente das variantes de caixa; (2) demais lemas com vocabulário frequente (`entries.most_used = 1`) à frente; (3) desempate alfabético | RN-04 e decisão do usuário de 2026-10-15 (`requirements.md#9`) | Alfabética pura, extensão do verbete, combinação extensão + marca (avaliadas e descartadas no esclarecimento) | 🟢 |
| D-06 | Entre lemas coincidentes que diferem só na caixa («a» e «A»), o grafado em minúsculas vem primeiro | A consulta em texto corrido chega quase sempre em minúsculas; as variantes maiúsculas são letras, símbolos e siglas (132 casos) | Ordem de código (poria a letra «A» antes do artigo e preposição «a») | 🟡 |
| D-07 | «Alfabética» no desempate = comparação com diacríticos e caixa dobrados (NFD sem marcas, minúsculas), desempatada pela grafia exata | Aproxima a ordem de dicionário sem dependência nova e é determinística em qualquer plataforma | Ordem de código pura (põe «é» depois de «z»); collation do sistema ou ICU (resultado dependente da plataforma, dependência nova) | 🟡 |
| D-08 | Leiaute do corpo: primeiro a página de cada chave de lema, em ordem de índice (artigo isolado se a página é simples; página combinada se não, com o próprio lema no primeiro trecho); depois cada sequência distinta de artigos das demais páginas combinadas, gravada uma única vez | Toda forma de um só lema aponta para o trecho do artigo dentro de uma página já gravada, sem cópia (RF-03); páginas com a mesma sequência compartilham trecho (16.910 sequências para 22.913 páginas) | Copiar o artigo para cada chave (corpo cresce cerca de 36 MB a mais); trecho isolado separado para cada lema (duplica 13.944 artigos) | 🟢 |
| D-09 | Distribuição das chaves: o `.idx` recebe as chaves de lema, as chaves de forma com página combinada e as formas de um só lema cujo lema abre página combinada; o `.syn` recebe as demais formas de um só lema, apontando para a entrada do lema. Cada chave aparece uma única vez em `.idx ∪ .syn` | O Readest consulta o `.idx` antes do `.syn` e devolve uma única entrada; chave única elimina o sombreamento medido hoje (14.428 formas abertas pelo verbete errado); o `.syn` só serve quando o alvo é a página inteira de uma entrada do `.idx` | Tudo no `.idx`, sem `.syn` (contraria RF-01, que pede os quatro arquivos); `.syn` apontando para a página combinada (traria artigo alheio, contra RN-03) | 🟢 |
| D-10 | Página combinada = artigos de `renderizar_artigo` sem alteração, unidos pelo divisor `<hr>`; cada artigo já abre com `<b>lema</b>` | RN-01 (mesmo conteúdo do KOReader) e RN-04 (lema em destaque, divisor visível); nem o vocabulário do renderizador nem o HTML do banco (RB-03) contêm `<hr>`, o que faz do divisor também a fronteira que a validação usa para recortar artigos | Cabeçalhos com classes do Tailwind do Readest (dependem do CSS interno do aplicativo); reescrever o cabeçalho do artigo (mudaria o conteúdo em relação ao KOReader) | 🟢 |
| D-11 | `.ifo` determinístico: `bookname=Aurélio (uso pessoal, Readest)`, `sametypesequence=h`, `version=3.0.0`, `date` = data de referência do manifesto de integridade, e `description` com a impressão digital do conteúdo (SHA-256 truncado de `.idx`, `.syn` e `.dict` descomprimido); `.dict.dz` com `mtime` e nome base fixos | O Readest identifica o dicionário por hash do `.ifo` e dos nomes de arquivo (`contentId.ts`): mesmo conteúdo mantém a identidade e a reimportação substitui o registro; conteúdo novo ganha identidade nova; RN-09 pede determinismo do corpo, que o cabeçalho gzip com data de build quebraria | Data do build no `.ifo` (cada rebuild viraria dicionário novo no Readest e na nuvem, mesmo sem mudança de conteúdo) | 🟡 |
| D-12 | Validação independente em `validacao/paridade_readest.py`: reaproveita `LeitorStarDict`; recalcula conjunto e ordem esperados por chave a partir de headwords, mapa e lemas frequentes, sem importar o agrupamento; simula a busca do Readest em Python (`.idx`, depois `.syn`) para todas as chaves; recorta cada página no divisor e lê o lema de abertura de cada artigo; confere ordem estrita, unicidade cruzada, metadados, NFC das chaves, ausência de cópia nos acessos isolados e a amostra de 500 lemas (seed fixa) | RF-05 com tolerância zero; recalcular o esperado de forma independente evita que um defeito do agrupamento passe despercebido pelo gate | Usar o plano do agrupamento como esperado (circular); validar só com o código do Readest (perde o diagnóstico nominal por artigo) | 🟢 |
| D-13 | Conferência com o código do Readest em `pipeline/conferencia_readest/`: tag `v0.12.16` (commit `3cc39ad7a558e6612e1a8135058fbd6f3c90b3e3`); baixa `stardictReader.ts` e `dictZip.ts` do repositório público, confere SHA-256 versionado, aplica uma única reescrita mecânica (especificador `./dictZip` → `./dictZip.ts`); instala `fflate@0.8.3`, a versão travada no lockfile do Readest nessa tag, por `npm ci`; executa o roteiro próprio `conferir.ts` no Node com remoção nativa de tipos | RF-06; o roteiro reproduz a ordem de busca do provedor (`lookup`, depois `resolveSynonym`) porque o módulo do provedor depende de DOM e de aliases do aplicativo; hashes e lockfile tornam a conferência reprodutível | `tsx` para executar TypeScript (dependência extra com binário nativo); vendorizar o código do Readest no repositório (redistribuição de código AGPL-3.0 sem necessidade); `fflate@0.8.2` do arnês de medição (difere da versão travada pelo Readest) | 🟢 |
| D-14 | Pré-verificação antes do build do alvo Readest: `node` ≥ 22.18 e `npm` presentes, cache completo ou rede disponível; falha com `AmbienteConferenciaError` e mensagem acionável | RF-06 exige erro nomeado sem entregar artefato não conferido; checar antes evita gastar o build para reprovar no fim | Descobrir a falta do Node só na etapa final | 🟢 |
| D-15 | Promoção condicionada: o alvo Readest grava em diretório de preparo dentro de `dist/`; aprovado nas duas etapas, sobe por rename atômico para `dist/readest/`; reprovado, vai para `dist/readest.reprovado/` com relatórios e expectativa, e a versão aprovada anterior fica intacta | RN-07 proíbe entregar artefato sem as duas aprovações; o alvo KOReader segue validando no lugar, sem mudança (RN-01) | Validar no lugar como o alvo KOReader (deixaria artefato reprovado no caminho de importação) | 🟢 |
| D-16 | Pasta entregue com só os quatro arquivos importáveis em `dist/readest/aurelio-readest/`; relatórios em `dist/readest/relatorios/` | A importação do Readest agrupa arquivos por nome base; pasta só com os quatro evita arquivo órfão na seleção | Relatórios ao lado dos arquivos, como no alvo KOReader | 🟢 |
| D-17 | CLI com `--alvo {koreader,readest,ambos}`, padrão `koreader`; ingestão e índice de flexões rodam uma vez por execução; cada alvo emite bloco final de log (totais, duração, relatório); exit code final é o pior entre os alvos (0, 2 erro nomeado, 3 reprovação) | RF-07 preserva o comportamento atual sem argumento; uma só execução evita dessincronia banco↔artefatos | Comando separado para o Readest (duplicaria ingestão e romperia o comando único) | 🟢 |
| D-18 | Renderização do alvo Readest em memória (lema → HTML) a partir de uma passada de `repositorio.artigos()`; a nova consulta `lemas_frequentes()` fica no repositório, e `entries.most_used` entra no esquema requerido | O leiaute de D-08 precisa de acesso aleatório aos artigos; o protótipo do agrupamento mediu 0,55 GB de pico, e o texto dos artigos soma 54,6 MB, abaixo do teto de 2 GB | Duas passadas com reescrita do corpo (complexidade sem ganho dentro do teto de memória) | 🟢 |
| D-19 | `[regen]` do Harness continua só com o alvo KOReader | O encerramento de sessão não deve depender de Node nem de rede | Regenerar os dois alvos a cada encerramento | 🟢 |
| D-20 | Testes com dados sintéticos: homônimos, lema que é forma de outro, forma de dois lemas, colisão de caixa, «à» diante de «a», forma sem letra, lema frequente diante de raro; teste de ordem contra a comparação do Readest; escritor lido pelo `LeitorStarDict`; teste de integração da conferência marcado e pulado quando falta o Node | RNF de testabilidade e RN-08 (repositório público sem conteúdo do Aurélio) | Testar com o banco real (lento e com conteúdo protegido) | 🟢 |

## 4. Premissas

Nenhuma. A única `[DÚVIDA]` do requirements foi resolvida na sessão de esclarecimentos de 2026-10-15 (RN-04, `requirements.md#9`).

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| — | — | — |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `ingestao-aurelio` (P-01) | `_reversa_sdd/architecture.md#2-componentes`; código em `pipeline/src/aurelio_pipeline/infra/repositorio.py` | contrato-alterado | Nova consulta `lemas_frequentes()`; `entries.most_used` entra em `COLUNAS_REQUERIDAS` |
| `indice-de-flexoes` (P-02) | `_reversa_sdd/architecture.md#2-componentes`; `dominio/indice_flexoes.py` | inalterado | O mapa de `construir_mapa` alimenta os dois alvos |
| `agrupamento-readest` | n/a (novo) | componente-novo | `dominio/agrupamento_readest.py`: chaves, páginas, ordem e relatório (RF-02, RF-03) |
| `conversao-formato` (P-03) | `_reversa_sdd/architecture.md#2-componentes`; `dominio/renderizacao.py`, `infra/escrita_stardict.py` | componente-novo (adaptador) | `renderizar_artigo` e o adaptador PyGlossary inalterados; nasce `infra/escrita_readest.py` com leiaute de páginas, índices na ordem do Readest e dictzip determinístico |
| `validacao-paridade` (P-04) | `_reversa_sdd/architecture.md#2-componentes`; `validacao/` | componente-novo (validador) | Nasce `validacao/paridade_readest.py`; `LeitorStarDict` reaproveitado sem mudança; `paridade.py` intocado |
| `conferencia-readest` | n/a (novo) | componente-novo + contrato-novo | `pipeline/conferencia_readest/` (roteiro Node, hashes, lockfile) e `infra/conferencia_readest.py` (obtenção, cache, subprocesso) |
| CLI do pipeline | `pipeline/src/aurelio_pipeline/cli.py` | regra-alterada | `--alvo`, pré-verificação do ambiente, promoção condicionada do alvo Readest |
| `governanca-operacional` (C-02) | `_reversa_sdd/architecture.md#2-componentes` | contrato-alterado | `.gitignore` ganha o cache e o `node_modules/` da conferência; `pipeline/README.md` ganha a seção do Readest |
| `banco-lexical` (C-01) | `_reversa_sdd/architecture.md#2-componentes` | inalterado | Somente leitura; uma coluna a mais lida (`most_used`) |
| `distribuicao-webdav` (P-05) | `_reversa_sdd/architecture.md#2-componentes` | fora do escopo | No Readest a cópia entre aparelhos é a nuvem privada do próprio aplicativo (RN-08) |

## 6. Delta no modelo de dados

- Resumo das mudanças: o banco não muda; o pipeline passa a ler `entries.most_used`. Nascem o artefato do Readest (quatro arquivos), três relatórios JSON por execução (agrupamento, validação, conferência), a expectativa transitória da conferência, o cache local do código do Readest e, versionados, os hashes e o lockfile da conferência.
- Detalhe completo em: `_reversa_forward/003-dicionario-readest/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Artefato StarDict consumido pelo Readest | arquivo | `_reversa_forward/003-dicionario-readest/interfaces/artefato-readest.md` |
| Obtenção e execução do código de busca do Readest | HTTP (GitHub e registro npm) + subprocesso | `_reversa_forward/003-dicionario-readest/interfaces/conferencia-readest.md` |
| Artefato StarDict consumido pelo KOReader | arquivo | inalterado: `_reversa_forward/002-build-completo-de-producao/interfaces/artefato-stardict.md` |

## 8. Plano de migração

Não há migração de dados nem troca de artefato instalado no KOReader. Há uma instalação nova:

1. Gerar o alvo Readest até a promoção para `dist/readest/` (exit code 0).
2. No Readest do Mac, ligar a sincronização de dicionários e importar os quatro arquivos de `dist/readest/aurelio-readest/` pela tela de dicionários.
3. Conferir «era», «foi», «fosse», «vieram», «cantávamos» e «à» num livro em português (RF-08).
4. Em atualizações futuras: se o conteúdo mudou, o `.ifo` muda e o Readest o trata como dicionário novo; remover o anterior antes de importar o novo (D-11), conforme o README.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Minúsculas do Python divergirem das do JavaScript em algum caractere raro, quebrando a ordem para a busca do Readest | alto | baixo | Zero chaves fora do plano multilíngue básico e zero chaves fora de NFC no banco atual; a conferência com o código real reprova qualquer divergência |
| Versão futura do Readest mudar a busca ou a leitura do dictzip | médio | médio | Versão fixada na conferência; o README manda, ao atualizar o Readest, subir a tag e os hashes e regenerar; código idêntico de 0.12.12 a 0.12.16 |
| Reimportação criar dicionário duplicado no Readest e na nuvem | baixo | médio | `.ifo` como função do conteúdo (D-11); passo de remoção no README |
| GitHub ou registro npm indisponíveis na primeira obtenção | baixo | baixo | Cache local; `AmbienteConferenciaError` nomeia o que faltou; com cache presente, a geração funciona sem rede |
| HTML de algum artigo conter `<hr>`, confundindo o recorte da validação | médio | baixo | RB-03 limita as tags do banco; a validação compara o número de divisores com o número de artigos esperado e reprova com o nome da chave |
| Peculiaridades do banco aparecerem nas páginas (o banco registra «a» como forma de «bretão», e a página de «a» mostra «bretão») | baixo | certo | É o comportamento que RN-02 exige; o mesmo ocorre no KOReader; corrigir o dado foge ao escopo (banco somente leitura) |
| Cota da nuvem do Readest | baixo | baixo | Artefato estimado em cerca de 34 MB; conferir a sincronização em outro aparelho no smoke de RF-08 |
| Pico de memória com renderização integral em memória | baixo | baixo | Estimativa abaixo de 1,5 GB; medir com `/usr/bin/time -l` no primeiro build |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] Alvo Readest aprovado nas duas etapas e promovido, com os números do banco atual: 887.546 chaves pesquisáveis, 160.302 entradas no `.idx`, 727.244 no `.syn`, 22.913 páginas combinadas, 261 formas descartadas por falta de letra, artefato até 50 MB
- [ ] Alvo KOReader sem argumento novo aprovado como antes: 137.784 verbetes e 774.003 formas
- [ ] Suíte verde, com cobertura de pelo menos 60% no domínio e na validação, sem conteúdo do Aurélio nos testes
- [ ] `pipeline/README.md` cobre geração, números esperados, importação e atualização no Readest
- [ ] Dicionário importado e conferido no Readest do Mac com «era», «foi», «fosse», «vieram», «cantávamos» e «à»
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-15 | Versão inicial gerada por `/reversa-plan` | reversa |
