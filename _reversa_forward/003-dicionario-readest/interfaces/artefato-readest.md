# Interface: artefato StarDict para o Readest

> Contrato do arquivo consumido pelo leitor StarDict do Readest. Tipo: arquivo.
> Produtor: `infra/escrita_readest.py` (escritor próprio, stdlib + `python-idzip`). Consumidores: Readest 0.12.12 ou posterior (Mac e, pela nuvem privada, os demais aparelhos do usuário); `validacao/paridade_readest.py`; `conferencia_readest/conferir.ts`.
> Mesmo formato do artefato do KOReader (`_reversa_forward/002-build-completo-de-producao/interfaces/artefato-stardict.md`), com semântica de chaves diferente. Não deve ser instalado no KOReader.

## 1. Layout

```
dist/readest/
├── aurelio-readest/                 # só os quatro arquivos importáveis (D-16)
│   ├── aurelio-readest.ifo
│   ├── aurelio-readest.idx
│   ├── aurelio-readest.syn
│   └── aurelio-readest.dict.dz
└── relatorios/
    ├── relatorio-agrupamento.json
    ├── validacao-readest.json
    └── conferencia-readest.json
```

## 2. Campos do `.ifo`

| Campo | Valor | Regra |
|-------|-------|-------|
| `version` | `3.0.0` | offsets de 32 bits, sem `idxoffsetbits` |
| `bookname` | `Aurélio (uso pessoal, Readest)` | distingue do dicionário do KOReader; RB-11 visível no nome |
| `wordcount` | número de entradas do `.idx` (160.302 no banco atual) | não é o número de lemas; validado contra o real |
| `synwordcount` | número de entradas do `.syn` (727.244) | validado contra o real |
| `idxfilesize` | tamanho do `.idx` em bytes | validado contra o real |
| `sametypesequence` | `h` | corpo em HTML, sem byte de tipo |
| `date` | data de referência do banco no manifesto de integridade | estável enquanto o banco não muda (D-11) |
| `description` | texto de uso pessoal + `conteúdo <SHA-256 truncado em 16 hexadecimais>` | muda se e só se o conteúdo dos índices ou do corpo mudar (D-11) |

## 3. Semântica das chaves

- **Chave pesquisável:** cada lema e cada forma com ao menos uma letra; duas grafias iguais em minúsculas são uma só chave.
- **Comparação e ordem:** `s.lower()` comparado por unidades UTF-16, como o `cmpAscii` do Readest. `.idx` e `.syn` estritamente crescentes; nenhuma chave aparece duas vezes, nem dentro de um índice nem entre os dois.
- **Grafia gravada:** chave de lema, a grafia do primeiro artigo da página; chave de forma, a grafia da forma no banco. Todas em NFC.
- **`.idx`:** (a) chaves de lema; (b) chaves de forma cuja página é combinada; (c) chaves de forma de um só lema cujo lema abre página combinada, apontando para o trecho do artigo dentro dessa página.
- **`.syn`:** chaves de forma de um só lema cujo lema abre página simples; o índice aponta para a entrada do lema no `.idx`.

## 4. Semântica do corpo (`.dict.dz`)

- **Página simples:** um artigo de `renderizar_artigo`, idêntico ao do KOReader.
- **Página combinada:** artigos na ordem de RN-04, unidos por `<hr>`; cada artigo abre com `<b>lema</b>`.
- **Compartilhamento de trechos:** entradas diferentes podem apontar para o mesmo trecho ou para um sub-trecho de outra página; os offsets não são monotônicos. O formato permite isso e o leitor do Readest não exige ordem de offsets.
- **Compressão:** dictzip com campo RA, gerado por `idzip.compressor.compress`, com `mtime` e nome base fixos.

## 5. Comportamento esperado no Readest

| Consulta | Título exibido | Página |
|----------|----------------|--------|
| «cantávamos» (forma de um só lema, página do lema simples) | cantar | artigo de cantar |
| «vieram» (forma de um só lema, página do lema combinada) | vieram | só o artigo de vir |
| «vir» | vir | vir, ver |
| «foi» | foi | ir, ser |
| «era» | era | era, ser, erar |
| «fosse» | fosse | ir, ser, fossar |
| «à» | à | à (antes inalcançável) |
| «Foi» em início de frase | foi | ir, ser (a comparação ignora caixa) |
| «/» | sem resultado | forma descartada (RN-06) |

## 6. Idempotência, atomicidade e erros

- **Determinismo (RN-09):** mesmo banco, mesmos bytes em `.idx`, `.syn` e `.dict.dz`; o `.ifo` também, porque a data vem do manifesto.
- **Promoção atômica (D-15):** escrita em diretório de preparo dentro de `dist/`; rename para `dist/readest/` só depois das duas aprovações; a versão aprovada anterior só é substituída nesse rename.
- **Reprovação:** o artefato reprovado vai para `dist/readest.reprovado/` com relatórios e expectativa; exit code 3.
- **Erros do produtor:** `FalhaGeracaoError` (escrita ou compressão), `FormaAnomalaError` (herdado do índice); o destino final permanece na versão anterior.
- **Erros do validador:** `ArtefatoAusenteError`, `ArtefatoCorrompidoError` (reaproveitados do leitor).
- **Timeouts:** não se aplica (arquivo local).

## 7. Instalação e atualização (consumo)

| Passo | Como |
|-------|------|
| Importar | Tela de dicionários do Readest do Mac, selecionando os quatro arquivos de `dist/readest/aurelio-readest/` |
| Sincronizar | Com a sincronização de dicionários ligada, o Readest guarda o pacote na nuvem privada da conta do usuário (RN-08: não é publicação) |
| Atualizar com conteúdo novo | Remover o dicionário anterior no Readest e importar o novo; identidade nova pelo `.ifo` (D-11) |
| Reimportar o mesmo conteúdo | O Readest reconhece a mesma identidade e substitui o registro |
