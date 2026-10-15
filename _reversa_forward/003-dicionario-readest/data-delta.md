# Data delta: 003-dicionario-readest

> Data: 2026-10-15 · Diff conceitual sobre o modelo extraído em `_reversa_sdd/`
> Referências: `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/domain.md#4`, `_reversa_forward/002-build-completo-de-producao/data-delta.md`

## 1. Banco de origem: nenhuma mudança

O `aurelio_normalized.db` segue somente leitura (RB-10), sem campo novo, removido ou alterado, e sem migração. Muda apenas o que o pipeline lê:

| Tabela | Coluna | Mudança | Uso |
|--------|--------|---------|-----|
| `entries` | `most_used` | passa a ser lida e entra em `COLUNAS_REQUERIDAS` do repositório | Marca de vocabulário frequente que ordena os artigos não coincidentes da página (RN-04); 3.039 entradas com valor 1; critério editorial inferido (L-04, 🟡) |

Um lema é frequente quando **alguma** de suas entradas homônimas tem `most_used = 1` (exemplo: `ver` homônimo 1 marcado, homônimo 2 não; o lema `ver` conta como frequente). A consulta nova é `SELECT DISTINCT lemma FROM entries WHERE most_used = 1`, exposta como `lemas_frequentes()`.

O `manifesto-integridade.json` não muda: as contagens das 12 tabelas continuam as mesmas.

## 2. Dados derivados novos (todos fora do git)

### 2.1 `dist/readest/aurelio-readest/`: artefato importável 🟢

Quatro arquivos com o nome base `aurelio-readest` (`.ifo`, `.idx`, `.syn`, `.dict.dz`). Contrato em `interfaces/artefato-readest.md`. Invariantes no banco atual:

| Invariante | Valor |
|------------|-------|
| `wordcount` (`.idx`) | 160.302 |
| `synwordcount` (`.syn`) | 727.244 |
| Chaves pesquisáveis = `wordcount + synwordcount` | 887.546 |
| Chaves repetidas na comparação do Readest, dentro de cada índice e entre os dois | 0 |
| Tamanho total | até 50 MB (estimado em cerca de 34 MB) |

### 2.2 `dist/readest/relatorios/relatorio-agrupamento.json` 🟢

Produzido pelo agrupamento (RF-02):

```
chaves                     int    chaves pesquisáveis (887.546)
paginas_simples            int    chaves com um artigo
paginas_combinadas         int    chaves com dois ou mais artigos (22.913)
sequencias_distintas       int    sequências de artigos das páginas combinadas (16.910)
descartes_sem_letra        int    formas descartadas (261)
formas_descartadas         [str]  as formas descartadas, nominalmente, com o lema de cada uma
artigos_por_pagina         {n: int}  distribuição (1, 2, 3, ... )
indice                     {idx: int, syn: int, idx_lemas: int, idx_formas_combinadas: int, idx_formas_diretas: int}
```

Invariante: `chaves = paginas_simples + paginas_combinadas = indice.idx + indice.syn`.

### 2.3 `dist/readest/relatorios/validacao-readest.json` 🟡

Esquema análogo ao `ParityReport` da feature 002 (veredito, gerado_em, seeds, contagens, amostras, divergências), com checks próprios: `ordem-idx`, `ordem-syn`, `unicidade-cruzada`, `nfc`, `pagina-artigos` (faltam, sobram, ordem), `acesso-isolado-sem-copia`, `metadados-ifo`, `amostra-conteudo`. Fica fora do git porque cita lemas e trechos de definição.

### 2.4 `dist/readest/relatorios/conferencia-readest.json` 🟡

Saída do roteiro Node: versão do Readest e do `fflate`, hashes conferidos, contagens (`chaves_ok`, `chaves_falha`, `trechos_ok`, `trechos_falha`), até 50 falhas nominais, duração e veredito.

### 2.5 Expectativa da conferência (transitória) 🟢

Arquivo TSV `chave<TAB>offset<TAB>tamanho`, uma linha por chave pesquisável, gerado pelo escritor no diretório de preparo. Sai com a promoção; permanece em `dist/readest.reprovado/` quando o artefato é reprovado, para diagnóstico.

### 2.6 Cache da conferência: `pipeline/conferencia_readest/.cache/` e `pipeline/conferencia_readest/node_modules/`

Código do Readest baixado (já com a reescrita do especificador) e `fflate` instalado por `npm ci`. Regeneráveis; fora do git.

## 3. Dados versionados novos

| Arquivo | Conteúdo | Motivo |
|---------|----------|--------|
| `pipeline/conferencia_readest/fonte-readest.json` | tag, commit, caminhos e SHA-256 dos arquivos do Readest | Reprodutibilidade (RB-12) e detecção de download divergente |
| `pipeline/conferencia_readest/package.json` e `package-lock.json` | `fflate` em `0.8.3` exato, com integridade | Instalação reprodutível por `npm ci` |
| `pipeline/conferencia_readest/conferir.ts` | roteiro próprio que carrega o leitor do Readest e confere a expectativa | RF-06 |

Nenhum deles contém conteúdo do Aurélio (RN-08).

## 4. Estruturas em memória (contratos internos entre camadas)

| Estrutura | Produtor → Consumidor | Conteúdo |
|-----------|-----------------------|----------|
| `frozenset[str]` de lemas frequentes | `infra/repositorio` → `dominio/agrupamento_readest` | Saída de `lemas_frequentes()` |
| `PlanoPaginas` | `dominio/agrupamento_readest` → `infra/escrita_readest` | Por chave: grafia gravada e sequência ordenada de lemas; páginas de lema e sequências distintas |
| `RelatorioAgrupamento` | `dominio/agrupamento_readest` → `cli` (JSON) | Ver §2.2 |
| `dict[str, str]` lema → HTML | `cli` (via `renderizar_artigo`) → `infra/escrita_readest` | Artigos integrais, idênticos aos do KOReader (RN-01) |
| `ResultadoEscritaReadest` | `infra/escrita_readest` → `cli`, `validacao`, `conferencia` | Totais, bytes por arquivo, caminho do preparo e da expectativa |

## 5. Mudanças em arquivos de governança

| Arquivo | Mudança | Motivo |
|---------|---------|--------|
| `.gitignore` | + `pipeline/conferencia_readest/.cache/`, + `pipeline/conferencia_readest/node_modules/` | Cache regenerável e código de terceiros fora do git; `dist/` já está ignorado |
| `pipeline/README.md` | + seção do Readest | RF-09 |
| `pipeline/pyproject.toml` | descrição atualizada; nenhuma dependência nova | D-01 |

## 6. Migrações

Não se aplica. Nenhum dado existente muda de forma ou de lugar; o artefato do KOReader em `dist/aurelio-stardict/` não é tocado.
