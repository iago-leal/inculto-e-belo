# Investigation: 003-dicionario-readest

> Data: 2026-10-15 · Pesquisa de fundo do `/reversa-plan`
> Fontes primárias: código do Readest na tag `v0.12.16` (commit `3cc39ad7a558e6612e1a8135058fbd6f3c90b3e3`), a medição de 2026-10-15 com esse código sobre `dist/aurelio-stardict/` e um protótipo do agrupamento rodado sobre o mesmo artefato e o banco.

## 1. Como o Readest busca uma palavra (🟢, código lido)

| Arquivo (`apps/readest-app/src/services/dictionaries/`) | Comportamento | Consequência para o plano |
|------|---------------|---------------------------|
| `stardictReader.ts` | `cmpAscii(a, b)`: `toLowerCase()` dos dois lados e comparação de strings do JavaScript (unidades UTF-16); busca binária preguiçosa sobre os offsets do `.idx` e do `.syn` | A ordem dos dois índices tem de ser a dessa comparação (D-03); chaves iguais nela são uma só chave |
| `stardictReader.ts` | `resolveSynonym` devolve a entrada do `.idx` apontada pelo `.syn`, com o `word` dessa entrada | A forma resolvida pelo `.syn` herda a página inteira da entrada; daí só usar `.syn` quando a página do lema é simples (D-09) |
| `providers/starDictProvider.ts` | `lookup` no `.idx`; se falhar, `resolveSynonym`; renderiza um único resultado, com `<h1>` da palavra da entrada e o corpo por `innerHTML` | Um resultado por consulta é a razão da feature; o título mostra a chave do índice; HTML arbitrário é aceito |
| `providers/starDictProvider.ts` | `sametypesequence` precisa ter um caractere em `{m, h, x, t}` | `sametypesequence=h` |
| `lookupCandidates.ts` | Tenta a grafia original, minúsculas, capitalizada, maiúsculas, NFC e NFD, lemas por idioma e, por último, sem diacríticos; fica com o primeiro acerto | Chaves em NFC (o banco atual não tem nenhuma fora de NFC); como toda palavra pesquisável está no índice, o primeiro candidato acerta |
| `dictZip.ts` | Lê o `.dict.dz` por blocos, usando o campo RA do dictzip, com `fflate`; se o campo faltar, descomprime tudo | O dictzip do `python-idzip` foi lido íntegro na medição (137.784 de 137.784 artigos); o escritor próprio usa o mesmo compressor (D-01) |
| `dictionaryService.ts` | Agrupa arquivos por nome base; um pacote StarDict é `.ifo` + `.idx` + `.dict` ou `.dict.dz`, com `.syn` opcional; grava *sidecars* de offsets na importação | Os quatro arquivos com o mesmo nome base `aurelio-readest`; pasta só com eles (D-16) |
| `contentId.ts`, `dictionaryDedup.ts` | Identidade do dicionário = MD5 parcial do `.ifo` + tamanho + nomes dos arquivos; reimportar com a mesma identidade substitui o registro; identidade nova cria outro registro | `.ifo` como função do conteúdo (D-11) e passo de remoção no README |

O código de busca é idêntico de 0.12.12 a 0.12.16. Hashes SHA-256 dos arquivos no commit fixado, conferidos em 2026-10-15:

| Arquivo | SHA-256 |
|---------|---------|
| `stardictReader.ts` | `affa164d360f285988d6dbf2816c9e217193c3ce6ff3f733a265d891fbfd1418` |
| `dictZip.ts` | `2e8f5448adbf9f9456201e4afb83a6c20209f6bba37cf4539ad51b3f7e691b33` |
| `providers/starDictProvider.ts` (referência, não executado) | `5f9c558fedb8a08d48048c78aadec66c8dcbe35a7e0be792cbdec7e17a00b3e1` |

`dictZip.ts` importa `gunzipSync` e `Inflate` de `fflate`; o `pnpm-lock.yaml` da tag trava `fflate@0.8.3`. `stardictReader.ts` importa `./dictZip` sem extensão, o que a execução nativa de TypeScript no Node não resolve; daí a única reescrita mecânica de D-13.

## 2. O que a medição de 2026-10-15 mostrou (🟢)

Roteiro executado com `stardictReader.ts` e `dictZip.ts` reais sobre o artefato do KOReader:

- 137.648 de 137.784 verbetes abrem; 132 colidem por caixa; 4 ficam inalcançáveis («Å», «à», «à clef», «à clé») porque a ordem canônica do StarDict não é a de `cmpAscii`.
- 749.895 de 774.003 formas abrem o verbete certo; 14.428 são sombreadas por um verbete de mesma grafia; 9.680 são ambíguas e abrem só um dos destinos.
- 100% dos artigos são lidos íntegros pelo leitor por blocos.
- Carga do dicionário em 10 ms; varredura integral em cerca de 9 s.

## 3. Protótipo do agrupamento (🟢, rodado nesta sessão)

Regras de D-02 a D-09 aplicadas ao mapa de formas e aos lemas do artefato atual, com `entries.most_used` do banco:

| Medida | Valor |
|--------|-------|
| Chaves pesquisáveis | 887.546 |
| Páginas combinadas | 22.913 (16.910 sequências distintas de artigos) |
| Formas descartadas por falta de letra | 261 |
| Entradas no `.idx` | 160.302 = 137.652 chaves de lema + 9.101 formas com página combinada + 13.549 formas de lema com página combinada |
| Entradas no `.syn` | 727.244 |
| Corpo descomprimido | cerca de 73,7 MB (54,6 MB no KOReader), cerca de 18 MB comprimido pela razão observada de 4:1 |
| Artefato estimado | cerca de 34 MB (`.dict.dz` + `.idx` de cerca de 3 MB + `.syn` de cerca de 12 MB) |
| Maior página | «ponto» (ponto, pontar), 32 KB; maior artigo «ácido», 52 KB |
| Chaves fora de NFC ou fora do plano multilíngue básico | 0 e 0 |
| Pico de memória do protótipo | 0,55 GB |

Exemplos: «era» → era, ser, erar; «foi» → ir, ser; «fosse» → ir, ser, fossar; «boa» → boa, bom, boar; «vieram» → vir; «vir» → vir, ver; «a» → a, A, bretão; «à» → à.

## 4. Ordem dos artigos (resolvida no esclarecimento)

Das 22.913 páginas combinadas, 9.787 têm dois ou mais artigos de lemas que não coincidem com a chave. A marca de vocabulário frequente muda a ordem alfabética em 866 delas e não distingue nada em 8.225. A ordem por extensão do verbete mudaria 4.191 páginas, com erros visíveis («esposa» → esposar antes de esposo). Numa amostra de 20 páginas sem marca distintiva, extensão e alfabética acertaram em proporções parecidas. A decisão do usuário (vocabulário frequente, depois alfabética) está em `requirements.md#9`.

## 5. Alternativas avaliadas e descartadas

| Alternativa | Por que foi descartada |
|-------------|------------------------|
| Gerar o artefato do Readest com o PyGlossary | Grava um corpo por entrada e ordena pelo critério do formato; não produz páginas compostas por chave nem entradas que compartilham trecho (D-01) |
| Só `.idx`, sem `.syn` | Título sempre igual à palavra consultada, mas contraria RF-01 (quatro arquivos) e engorda o índice principal, que o Readest varre inteiro ao importar |
| `.syn` apontando para páginas combinadas | Formas de um só lema trariam artigo alheio («vieram» abriria «ver»), contra RN-03 |
| Copiar artigos em vez de apontar sub-trechos | Corpo cerca de 36 MB maior antes da compressão, e duplicação que RF-03 proíbe |
| `tsx` para executar o TypeScript do Readest | Dependência extra com binário nativo; o Node instalado (26.10.0) remove tipos nativamente |
| Vendorizar o código do Readest no repositório | O Readest é AGPL-3.0; cache local fora do git evita redistribuir e mantém o repositório limpo |
| Conferir só com o código do Readest | O roteiro Node diz se a busca acha a entrada, mas não nomeia o artigo faltante ou sobrando; a validação Python dá o diagnóstico nominal (RF-05) |
| Validação usando o próprio plano do agrupamento como esperado | Circular: um defeito do agrupamento passaria pelo gate |

## 6. Pontos que a implementação ainda deve confirmar (🟡, baratos)

1. **Versão mínima do Node:** a remoção nativa de tipos vem ligada por padrão a partir de 22.18 e 23.6; confirmar que o roteiro roda sem flags e fixar o mínimo na pré-verificação (D-14).
2. **Determinismo do `.dict.dz`:** confirmar que `idzip.compressor.compress` com `mtime` e nome base fixos produz bytes idênticos em duas execuções (RN-09).
3. **Paridade entre `str.lower()` e `toLowerCase()`:** a conferência com o código real é o juiz; se divergir, a chave de ordenação passa a ser calculada pelo próprio Node na conferência e devolvida ao escritor (plano B, não previsto como caminho normal).
4. **Rótulos da interface do Readest:** registrar no README os nomes exatos da tela de dicionários e da opção de sincronização ao fazer a importação de RF-08.
5. **Pico de memória:** medir com `/usr/bin/time -l` na primeira geração com `--alvo ambos`.
6. **Divisor visível no tema escuro:** conferir que o `<hr>` aparece com `liftDarkTextColors` ligado.

## 7. Fontes externas

- Readest, repositório público: https://github.com/readest/readest (tag `v0.12.16`)
- Arquivos brutos no commit fixado: `https://raw.githubusercontent.com/readest/readest/3cc39ad7a558e6612e1a8135058fbd6f3c90b3e3/apps/readest-app/src/services/dictionaries/<arquivo>`
- fflate 0.8.3: https://www.npmjs.com/package/fflate
- Remoção nativa de tipos no Node.js: https://nodejs.org/api/typescript.html
- python-idzip 0.3.9: https://pypi.org/project/python-idzip/
- Formato StarDict: `doc/p/stardict.md` no repositório do PyGlossary (https://github.com/ilius/pyglossary)
