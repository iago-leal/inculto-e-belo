# pipeline-readest, Contratos externos

> Gerado pelo reversa-writer em 2026-10-15. Três contratos: o artefato com o Readest, a expectativa com o roteiro e o roteiro com o Python.

## 1. Artefato StarDict para o Readest 🟢

Diretório `dist/readest/aurelio-readest/`, só com os quatro arquivos importáveis:

| Arquivo | Formato |
|---------|---------|
| `aurelio-readest.ifo` | `StarDict's dict ifo file`, `version=3.0.0`, `bookname=Aurélio (uso pessoal, Readest)`, `wordcount`, `synwordcount`, `idxfilesize`, `sametypesequence=h`, `date=<gerado_em do manifesto>`, `description=… Versão do conteúdo <16 hex>` |
| `aurelio-readest.idx` | Registros `grafia UTF-8\0` + offset (u32 BE) + tamanho (u32 BE), em ordem estritamente crescente de `lower().encode("utf-16-be")` |
| `aurelio-readest.syn` | Registros `grafia UTF-8\0` + índice no `.idx` (u32 BE), na mesma ordem; nenhuma grafia presente também no `.idx` |
| `aurelio-readest.dict.dz` | dictzip (gzip com campo `RA`), `mtime=0`; páginas HTML com artigos separados por `<hr>` |

Números do banco de 2026-07-03: 160.302 entradas no `.idx`, 727.244 no `.syn`, 140.750 trechos, corpo de 73.747.274 B e impressão `d4bc5db7f94992ba`.

## 2. Expectativa da conferência 🟢

`expectativa-conferencia.tsv`, no diretório de preparo, UTF-8, uma linha por chave do `.idx` e do `.syn`:

```
<grafia>\t<offset>\t<tamanho>\n
```

O offset e o tamanho são os do trecho que a chave deve abrir. A expectativa sai do escritor, não da validação, e é removida na promoção.

## 3. Roteiro `conferir.ts` 🟢

```
node conferir.ts <dir-artefato> <basename> <expectativa.tsv>
```

- Executado no diretório `pipeline/conferencia_readest/`; importa `stardictReader.ts` de `.cache/<tag>/` e usa o `fflate` de `node_modules/`.
- Para cada linha, `lookup(chave)` e, se falhar, `resolveSynonym(chave)`, na mesma ordem do provedor do Readest; compara offset e tamanho.
- Cada trecho distinto é relido pelo leitor por blocos e comparado com a descompressão integral do `fflate`.

| Exit | Significado para o Python |
|------|---------------------------|
| 0 | Aprovado |
| 1 | Reprovado |
| 2 | Uso incorreto (argumentos faltando) → `AmbienteConferenciaError` |
| outro, ou stdout que não é JSON | `AmbienteConferenciaError` |
| tempo acima de 600 s | Reprovado, com `causa` |

Saída em stdout, uma linha JSON:

```json
{
  "readest": {"tag": "v0.12.16", "commit": "3cc39ad7…"},
  "fflate": "0.8.3",
  "node": "v26.10.0",
  "chaves_ok": 887546,
  "chaves_falha": 0,
  "trechos_ok": 147263,
  "trechos_falha": 0,
  "falhas": [],
  "duracao_s": 41.6,
  "veredito": "aprovado"
}
```

`falhas` traz até 50 itens `{chave, esperado: [offset, tamanho], obtido: [offset, tamanho] | null}`. O Python recalcula o veredito final: aprovado só com exit 0 **e** `veredito == "aprovado"`.

## 4. Fonte fixada 🟢

`pipeline/conferencia_readest/fonte-readest.json` (versionado): repositório `readest/readest`, tag `v0.12.16`, commit `3cc39ad7a558e6612e1a8135058fbd6f3c90b3e3`, base `apps/readest-app/src/services/dictionaries/`, SHA-256 de `stardictReader.ts` e `dictZip.ts` originais e reescritos, as três reescritas (`de`, `para`, `motivo`), `fflate` 0.8.3 e `node_minimo` 22.18. Atualizar a versão fixada segue o `pipeline/README.md`, seção «Atualizar a versão fixada do Readest».

## 5. Relatórios 🟢

Em `dist/readest/relatorios/` (aprovado) ou `dist/readest.reprovado/relatorios/`:

| Arquivo | Produtor | Conteúdo |
|---------|----------|----------|
| `relatorio-agrupamento.json` | `RelatorioAgrupamento.to_dict` | Chaves, páginas simples e combinadas, sequências distintas, descartes sem letra com a lista das formas descartadas, artigos por página e contagens por destino no índice |
| `validacao-readest.json` | `gravar_relatorio(ParityReport)` | Os nove checks, com veredito, contagens e até 50 detalhes cada |
| `conferencia-readest.json` | `ConferenciaReadest.conferir` | O JSON do roteiro com o veredito final |
