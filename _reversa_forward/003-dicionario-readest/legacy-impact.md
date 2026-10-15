# Legacy impact — 003-dicionario-readest

> Data: 2026-10-15 · Gerado por `/reversa-coding` (modo autônomo)
> Âncora: `_reversa_sdd/architecture.md` (componentes) e `_reversa_sdd/domain.md` (regras 🟢)
> Execução: 22 de 23 ações concluídas; T021 (importação no Readest do Mac) pendente, ver `actions.md#notas-de-execução`.

## 1. Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `pipeline/src/aurelio_pipeline/dominio/agrupamento_readest.py` | `agrupamento-readest` (novo) | componente-novo | MEDIUM | Função pura palavra → página: artigos, ordem (RN-04), descarte de formas sem letra (RN-06) e destino no índice (D-09) |
| `pipeline/src/aurelio_pipeline/infra/escrita_readest.py` | `conversao-formato` (P-03, adaptador novo) | componente-novo | MEDIUM | Escritor StarDict próprio, sem PyGlossary: índices na ordem do Readest, páginas compostas com trechos compartilhados, `.ifo` determinístico, promoção condicionada |
| `pipeline/src/aurelio_pipeline/validacao/paridade_readest.py` | `validacao-paridade` (P-04, validador novo) | componente-novo | MEDIUM | Recalcula as páginas sem importar o agrupamento e simula a busca do Readest para todas as chaves; tolerância zero |
| `pipeline/src/aurelio_pipeline/infra/conferencia_readest.py`, `pipeline/conferencia_readest/` | `conferencia-readest` (novo) | delta-de-contrato-externo | HIGH | Primeira dependência de rede e de Node do projeto: obtém o código de busca do Readest pelo commit fixado, confere SHA-256, instala `fflate` 0.8.3 por `npm ci` e executa `conferir.ts` como etapa obrigatória do gate |
| `pipeline/src/aurelio_pipeline/infra/repositorio.py` | `ingestao-aurelio` (P-01) | delta-de-dados | MEDIUM | `entries.most_used` passa a ser coluna requerida; nova consulta `lemas_frequentes()`; banco segue somente-leitura |
| `pipeline/src/aurelio_pipeline/cli.py` | pipeline (orquestração) | regra-alterada | MEDIUM | `--alvo {koreader,readest,ambos}`, padrão `koreader` com comportamento anterior intacto; pré-verificação da conferência; exit code = pior entre os alvos |
| `pipeline/src/aurelio_pipeline/dominio/modelos.py`, `erros.py` | contratos internos | componente-novo | LOW | `PaginaReadest`, `PlanoPaginas`, `RelatorioAgrupamento`, `ResultadoEscritaReadest`; `AmbienteConferenciaError` (exit 2) |
| `pipeline/tests/` (4 arquivos novos, 2 alterados) | todos os anteriores | componente-novo | LOW | 145 testes (eram 50), dados sintéticos; integração com o código real do Readest pulada sem Node ou cache |
| `pipeline/README.md` | `governanca-operacional` (C-02) | regra-nova | LOW | Seção do Readest: geração, números esperados, importação, atualização, versão fixada, limitações, erros novos (RB-13) |
| `pipeline/pyproject.toml` | `governanca-operacional` (C-02) | contrato-alterado | LOW | Descrição cita os dois alvos; marcador `integracao` do pytest; nenhuma dependência Python nova |
| `.gitignore` | `governanca-operacional` (C-02) | contrato-alterado | LOW | Cache do código do Readest (AGPL-3.0, não redistribuído) e `node_modules/` fora do git |
| `dist/readest/` (fora do git) | artefato derivado | delta-de-dados | LOW | Novo artefato de cerca de 30 MB, aprovado nas duas etapas; impressão digital `d4bc5db7f94992ba` |
| `dist/aurelio-stardict/` (fora do git) | artefato derivado | delta-de-dados | LOW | Regenerado pelo `--alvo ambos` com o mesmo conteúdo e as mesmas contagens (137.784 e 774.003); só a data do `.ifo` muda, como em todo build |

**Não tocados:** `aurelio_normalized.db` (zero escritas), `pipeline/manifesto-integridade.json`, `harness.toml` (`[regen]` segue só com o KOReader, D-19), `dominio/indice_flexoes.py`, `dominio/renderizacao.py`, `infra/escrita_stardict.py`, `validacao/leitor_stardict.py`, `validacao/paridade.py`, `_reversa_sdd/`. Nenhum arquivo pré-existente foi apagado.

## 2. Diff conceitual por componente

O pipeline ganhou um segundo consumidor do mesmo núcleo. Ingestão, índice de flexões e renderização seguem idênticos e alimentam os dois alvos numa única execução; o alvo KOReader continua sendo o padrão e gera o mesmo artefato de antes. O alvo Readest acrescenta três peças: o agrupamento, que estende a fusão de homônimos por lema (RB-02, decisão do consumidor) à fusão de homógrafos entre lemas e formas, porque o Readest mostra um único resultado por consulta; um escritor próprio, porque o PyGlossary não grava índices na ordem do `cmpAscii` nem entradas que apontam para trechos de páginas já gravadas; e um gate de duas etapas, com validação independente em Python e conferência com o código real do Readest.

A conferência é a mudança de maior alcance operacional. Pela primeira vez a geração de um artefato depende de Node.js e, na primeira obtenção, de rede (GitHub e registro npm). A dependência é contida por versão fixada pelo commit, SHA-256 dos originais e dos arquivos reescritos, `package-lock.json` versionado e cache local. Na implementação, o Node 26 recusou as propriedades de parâmetro do `dictZip.ts`; a solução foi passar de uma para três reescritas mecânicas verificadas por hash, sem dependência nova (`interfaces/conferencia-readest.md#3`).

O `banco-lexical` (C-01) permanece somente-leitura; a única novidade é a leitura de `entries.most_used`, marca editorial de vocabulário frequente (🟡 L-04 no domain), usada só para ordenar artigos não coincidentes nas páginas combinadas. A `governanca-operacional` (C-02) ganhou o runbook do Readest e duas exclusões no `.gitignore`.

## 3. Preservadas (regras 🟢 do domain.md intactas)

- **RB-01, RB-04, RB-07, RB-08** (schema e ordem editorial): o artigo de cada lema é o mesmo `renderizar_artigo` do KOReader, sem alteração (RN-01 da 003).
- **RB-02**: homonímia continua preservada no banco; a fusão acontece só no consumidor, agora também entre lemas homógrafos na página do Readest.
- **RB-03**: o vocabulário de tags do banco segue limitado; o divisor `<hr>` das páginas combinadas não colide com ele, e a validação usa essa fronteira para recortar artigos.
- **RB-05**: as 22 órfãs continuam reportadas e fora dos índices, nos dois alvos.
- **RB-09**: `.db` fora do git; política estendida ao cache da conferência.
- **RB-10**: banco somente-leitura por construção (`mode=ro`); a coluna nova é só lida.
- **RB-12**: regeneração determinística e auditável, agora também no `.ifo` do Readest (data do manifesto e impressão digital do conteúdo); duas gerações produziram bytes idênticos; três relatórios JSON por execução.
- **RB-14**: split de `,` e `" ou "` inalterado, herdado do índice de flexões.

## 4. Modificadas

- **RB-11** (redação, sem perda de substância): o artefato do Readest continua de uso estritamente pessoal e nunca publicado; por decisão do usuário em 2026-10-15 (RN-08 da 003), guardá-lo na nuvem privada do Readest, vinculada à conta dele, não constitui publicação. Altera o requisito de privacidade da feature 002, segundo o qual nenhum dado saía do processo local. O repositório público segue sem conteúdo do Aurélio, nem em testes.
- **Baseline de §4 do domain (invariantes quantitativas)**: ganha os números do alvo Readest sobre o banco de 2026-07-03: 887.546 chaves pesquisáveis, 160.302 entradas no `.idx`, 727.244 no `.syn`, 22.913 páginas combinadas, 16.910 sequências distintas e 261 formas sem letra descartadas.
