# pipeline-readest, Design Técnico

> Gerado pelo reversa-writer em 2026-10-15.

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `chave_readest` | `(texto: str)` | `str` | `texto.lower()` 🟢 |
| `ordem_readest` | `(texto: str)` | `bytes` | `texto.lower().encode("utf-16-be")` 🟢 |
| `tem_letra` | `(texto: str)` | `bool` | Regex `[^\W\d_]` 🟢 |
| `agrupar` | `(headwords, mapa, frequentes)` | `(PlanoPaginas, RelatorioAgrupamento)` | Função pura; `assert chaves == idx + syn` 🟢 |
| `EscritorReadest` | `(dist_dir: Path, ...)` | instância | Grava em `dist/.readest-preparo-*` 🟢 |
| `.escrever` | `(plano: PlanoPaginas, artigos: Mapping[str, str], data: str)` | `ResultadoEscritaReadest` | `preparo`, `artefato`, `expectativa`, `idx`, `syn`, `impressao_digital` 🟢 |
| `promover` / `reprovar` | `(resultado, dist_dir)` | `Path` do destino | Troca atômica por renomeação 🟢 |
| `descartar` | `(resultado)` | `None` | Apaga o preparo 🟢 |
| `paginas_esperadas` | `(headwords, mapa, frequentes)` | `dict[chave, list[lema]]` | Recálculo independente do agrupamento 🟢 |
| `executar_validacao_readest` | `(artefato, headwords, mapa, frequentes, textos_definicoes, data, ...)` | `ParityReport` | Semente 20261015, amostra 500, 50 detalhes por check 🟢 |
| `ConferenciaReadest` | `(diretorio=pipeline/conferencia_readest, *, baixar, executar)` | instância | Rede e subprocesso injetáveis nos testes 🟢 |
| `.preparar` | `()` | `Path` do cache | Idempotente 🟢 |
| `.conferir` | `(artefato, basename, expectativa, timeout=600)` | `dict` (JSON do roteiro + veredito final) | 🟢 |

## Fluxo Principal

1. **Pré-verificação** (antes da ingestão, `cli.py:200`): `ConferenciaReadest.preparar()`:
   - `verificar_ambiente`: `node --version` ≥ 22.18 (maior e menor) e `npm --version`;
   - se o cache `pipeline/conferencia_readest/.cache/v0.12.16/` não vale, `_obter`: baixa `stardictReader.ts` e `dictZip.ts` de `raw.githubusercontent.com` pelo commit, confere o SHA-256 dos originais, aplica as três reescritas (cada uma com exatamente uma ocorrência), confere o SHA-256 dos reescritos e grava os arquivos e o marcador `.pronto`;
   - se o `fflate` 0.8.3 não está em `node_modules`, roda `npm ci --no-audit --no-fund`.
   🟢
2. **Agrupamento** (`dominio/agrupamento_readest.py:62`):
   - cada lema entra na sua chave; cada forma com letra entra na chave da forma, apontando para o lema;
   - a sequência de cada chave é ordenada por `_ordem_na_pagina` (RB-20);
   - o destino de cada chave segue a tabela de `code-analysis.md` §pipeline-readest (`idx-lema`, `idx-forma-combinada`, `idx-forma-direta`, `syn`);
   - a grafia gravada de uma forma é a própria chave, se for uma das grafias, ou a menor delas (`_grafia_de_forma`).
   🟢
3. **Escrita** (`infra/escrita_readest.py:56`):
   - `_conferir_entrada` recusa grafias com tabulação, quebra de linha, retorno de carro ou NUL e lemas do plano sem artigo (`infra/escrita_readest.py:85`);
   - grava as páginas de lema na ordem do índice, registrando a posição de cada artigo; depois, uma vez por sequência combinada distinta, as páginas de forma ainda não gravadas;
   - monta `.idx` (`grafia\0` + offset e tamanho de 32 bits big-endian) e `.syn` (`grafia\0` + índice de 32 bits), com o `.syn` apontando só para entradas do `.idx` de sequência idêntica;
   - comprime o corpo por dictzip com `mtime=0`;
   - grava o `.ifo` determinístico e `expectativa-conferencia.tsv`.
   🟢
4. **Relatório de agrupamento:** `relatorios/relatorio-agrupamento.json` no preparo. 🟢
5. **Validação** (`validacao/paridade_readest.py:118`): lê o artefato com o `LeitorStarDict`, recalcula as páginas, simula a busca (bisseção no `.idx` e depois no `.syn`), recorta cada página em `<hr>`, identifica cada artigo pelo `<b>…</b>` de abertura e roda os nove checks. Grava `validacao-readest.json`. 🟢
6. **Conferência:** `node conferir.ts <artefato> aurelio-readest <expectativa>` no diretório da conferência; grava `conferencia-readest.json`. 🟢
7. **Decisão:** aprovado nas duas etapas → `promover` (remove a expectativa e troca `dist/readest/`); senão `reprovar` (move o preparo para `dist/readest.reprovado/`). Exit 0 ou 3. 🟢

## Fluxos Alternativos

- **Node ausente, abaixo de 22.18, ou npm ausente:** `AmbienteConferenciaError` antes da ingestão, com «instale com `brew install node`». 🟢
- **Rede indisponível na primeira obtenção:** `AmbienteConferenciaError` acionável; com o cache válido, a rede não é usada. 🟢
- **SHA-256 divergente (original ou reescrito):** `AmbienteConferenciaError`; o cache não é gravado. 🟢
- **Reescrita sem exatamente uma ocorrência:** `AmbienteConferenciaError`, sinal de que a versão fixada mudou. 🟢
- **Exceção depois da escrita:** `descartar(resultado)` e a exceção é relançada; nada é promovido nem guardado. 🟢
- **Conferência acima de 600 s:** veredito reprovado com `causa`. 🟢
- **Roteiro com código fora de 0 e 1, ou saída que não é JSON:** `AmbienteConferenciaError`. 🟢

## Dependências

- `pipeline-nucleo`: headwords, mapa, artigos renderizados, `lemas_frequentes`, `textos_definicoes` e a data do manifesto.
- `pipeline-koreader`: `LeitorStarDict` e `gravar_relatorio`, reaproveitados pela validação.
- python-idzip (compressão dictzip).
- Node.js ≥ 22.18, npm e `fflate` 0.8.3, só na conferência.
- Código do Readest v0.12.16 (AGPL-3.0), em cache local não versionado.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Página única por palavra, com fusão de homógrafos | ADR-0007; `dominio/agrupamento_readest.py` | 🟢 |
| Escritor próprio, sem PyGlossary | ADR-0007; `infra/escrita_readest.py` | 🟢 |
| Gate em duas etapas, com o código real do leitor | ADR-0008; `cli.py:118` | 🟢 |
| Divisor `<hr>` entre artigos, ausente do vocabulário do banco | `infra/escrita_readest.py:35`; RB-03 | 🟢 |
| Validação sem importar agrupamento nem escritor | `pipeline/tests/test_paridade_readest.py:219` | 🟢 |
| Subprocesso só na conferência | `grep subprocess` no pacote | 🟢 |
| Impressão digital = 16 hex do SHA-256 de `idx + syn + corpo` | `infra/escrita_readest.py` | 🟢 |

## Estado Interno

- Preparo temporário em `dist/.readest-preparo-*`, removido em qualquer desfecho.
- `dist/readest/` (aprovado) e `dist/readest.reprovado/` (último reprovado).
- Cache da conferência em `pipeline/conferencia_readest/.cache/<tag>/` com marcador `.pronto`, e `node_modules/`; ambos fora do git.
🟢

## Observabilidade

- `etapa=pre-verificacao alvo=readest`, `etapa=agrupamento`, `agrupamento_ok chaves=… paginas_combinadas=… sequencias_distintas=… descartes_sem_letra=… idx=… syn=…`;
- `etapa=conversao alvo=readest … data=…`, `etapa=validacao`, `etapa=conferencia … readest=v0.12.16`;
- `conferencia veredito=… chaves_ok=… chaves_falha=… trechos_ok=… trechos_falha=… duracao_s=…`;
- `alvo_fim alvo=readest validacao=… conferencia=… … conteudo=<impressão> …`;
- três relatórios JSON em `relatorios/`.
🟢

## Riscos e Lacunas

- 🟡 L-04 de `domain.md`: o sentido editorial de `entries.most_used` é inferido; se mudar, a ordem das páginas combinadas muda sem erro.
- 🟡 O divisor `<hr>` no tema escuro do Readest não teve conferência visual explícita (O-05 da 003).
- 🟡 Uma versão nova do Readest que mude a busca exige atualizar `fonte-readest.json`; o procedimento está no `pipeline/README.md`.
- 🟡 Pico de 1,4 GB com os dois alvos, por causa dos artigos renderizados em memória (D-18 da 003).
