# Interface: artefato StarDict de produção

> Contrato do arquivo consumido pelo KOReader (sdcv embutido). Tipo: arquivo.
> Produtor: `infra/escrita_stardict.py` (adaptador PyGlossary 5.4.1). Consumidores: KOReader (macOS, Boox Air 4C); `validacao/leitor_stardict.py` (parser próprio).
> Evolui o contrato do spike (`_reversa_forward/001-spike-de-flexoes/`): mesmo formato, corpo integral e basename definitivo.

## 1. Layout

```
dist/aurelio-stardict/
├── aurelio-stardict.ifo        # metadados (texto UTF-8)
├── aurelio-stardict.idx        # índice de headwords (binário)
├── aurelio-stardict.dict.dz    # corpos HTML comprimidos (dictzip)
├── aurelio-stardict.syn        # formas flexionadas → headword (binário)
├── relatorio-cobertura.json    # auditoria do índice de flexões (não lido pelo KOReader)
└── parity-report.json          # veredito da validação (não lido pelo KOReader)
```

## 2. Campos do `.ifo` (contrato de metadados)

| Campo              | Valor                           | Regra                                                                    |
| ------------------ | ------------------------------- | ------------------------------------------------------------------------ |
| `version`          | `2.4.2`                         | fixado pelo writer                                                       |
| `bookname`         | `Aurélio (uso pessoal)`         | RF-05; a restrição RN-05 (direitos autorais) fica visível no nome        |
| `wordcount`        | `137784`                        | = lemas únicos (homônimos fundidos, RB-02); recalculado se o banco mudar |
| `synwordcount`     | `774003`                        | = pares únicos válidos (RN-03); recalculado se o banco mudar             |
| `idxfilesize`      | tamanho real do `.idx` em bytes | verificado pela paridade                                                 |
| `sametypesequence` | `h`                             | corpo é HTML puro, sem byte de tipo por entrada                          |
| `date`             | data da geração (`YYYY-MM-DD`)  | rastreabilidade do build                                                 |

## 3. Semântica das entradas

- **Headword (`.idx`):** um por lema canônico, com diacríticos, grafado como em `entries.lemma`. Artigo único funde os homônimos em seções numeradas (ordem `homonym` → `sort_key`).
- **Corpo (`.dict.dz`):** HTML autocontido por artigo — sem CSS externo, sem imagens, sem scripts; vocabulário de tags: `<b> <i> <u> <p> <ul> <li> <small>` + as tags embutidas do banco (`<em> <u> <strong>`, RB-03). Conteúdo integral: cabeçalho (lema estilizado, classes, IPA), etimologia, definições numeradas com rubrica, exemplos (editor e citation), locuções com definições, regência (Luft) e notas.
- **Forma flexionada (`.syn`):** aponta ao índice do headword no `.idx`. Grafada exatamente como no banco após o split de RB-14 — minúsculas, com diacríticos, sem variantes capitalizadas (RN-07). Forma ambígua = N registros, um por headword de destino.

## 4. Comportamento esperado no consumidor (validado no spike)

| Gesto                                                | Resultado                                                                                                  |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Toque em lema exato (`coração`)                      | Artigo único com os 3 homônimos                                                                            |
| Toque em forma flexionada (`cantávamos`)             | Verbete de `cantar`                                                                                        |
| Toque em forma ambígua (`belas`)                     | Popup lista `bela` e `belo`; escolha do leitor (NG-03 do índice)                                           |
| Toque em capitalizada em início de frase (`Árvores`) | Lookup exato falha; o fuzzy do sdcv/KOReader resgata (`árvore`) — comportamento do leitor, não do artefato |
| Forma que também é headword (`papéis`)               | Lookup exato do headword tem precedência; popup lista os demais destinos                                   |

## 5. Idempotência, atomicidade e erros

- **Determinismo (RN-06):** duas execuções sobre o mesmo banco produzem o mesmo conjunto de headwords, artigos e registros do `.syn` (ordenação estável em todas as camadas).
- **Escrita atômica (RF-05):** geração em diretório temporário + rename; interrupção nunca deixa `dist/aurelio-stardict/` parcial. Substituição sem retenção — rollback = rebuild.
- **Timeouts:** n/a (arquivo local, sem rede).
- **Erros do produtor:** `FalhaGeracaoError` (PyGlossary), falha nomeada de dictzip ausente, `FormaAnomalaError`/EC-04 — em todos, o diretório final permanece na versão anterior.
- **Erros do consumidor-validador:** `ArtefatoAusenteError` (arquivo faltando), `ArtefatoCorrompidoError` (offsets inválidos, gzip truncado) — exit code ≠ 0 bloqueia a instalação.

## 6. Instalação (consumo)

| Destino        | Caminho                                                              | Via                                                  |
| -------------- | -------------------------------------------------------------------- | ---------------------------------------------------- |
| KOReader macOS | `~/Library/Application Support/koreader/data/dict/aurelio-stardict/` | `cp -R`                                              |
| Boox Air 4C    | `koreader/data/dict/aurelio-stardict/`                               | USB/MTP (WebDAV fica para a feature de distribuição) |

Ao instalar, remover o `aurelio-spike/` do mesmo diretório (roadmap §8). O KOReader detecta o dicionário após reinício.
