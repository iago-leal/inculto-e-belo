# pipeline-readest, Tarefas de Implementação

> Gerado pelo reversa-writer em 2026-10-15.

## Pré-requisitos
- [ ] `pipeline-nucleo` com `lemas_frequentes()` e a data `gerado_em` no manifesto
- [ ] `LeitorStarDict` e `gravar_relatorio` do `pipeline-koreader`
- [ ] Node.js ≥ 22.18 e npm para a conferência; rede só na primeira obtenção

## Tarefas

- [ ] T-01, Modelos `PaginaReadest`, `PlanoPaginas`, `RelatorioAgrupamento`, `ResultadoEscritaReadest` e o erro `AmbienteConferenciaError`
  - Origem no legado: `pipeline/src/aurelio_pipeline/dominio/modelos.py`, `erros.py`
  - Critério de pronto: dataclasses imutáveis; relatório serializável
  - Confiança: 🟢
- [ ] T-02, Primitivas `chave_readest`, `ordem_readest`, `tem_letra` e `_dobrar`
  - Origem no legado: `pipeline/src/aurelio_pipeline/dominio/agrupamento_readest.py:26`–`:44`
  - Critério de pronto: ordem por unidades UTF-16, não por ponto de código
  - Confiança: 🟢
- [ ] T-03, `agrupar`, com ordem de página, descarte sem letra e destinos no índice
  - Origem no legado: `pipeline/src/aurelio_pipeline/dominio/agrupamento_readest.py:50`–`:133`
  - Critério de pronto: 887.546 chaves, 160.302 no `.idx` e 727.244 no `.syn` no banco atual; plano independente da ordem de entrada
  - Confiança: 🟢
- [ ] T-04, `EscritorReadest`, com páginas, trechos compartilhados, `.ifo` determinístico, dictzip `mtime=0` e expectativa
  - Origem no legado: `pipeline/src/aurelio_pipeline/infra/escrita_readest.py:43`–`:215`
  - Critério de pronto: duas escritas com bytes idênticos; impressão `d4bc5db7f94992ba` no banco atual
  - Confiança: 🟢
- [ ] T-05, Promoção condicionada (`promover`, `reprovar`, `descartar`)
  - Origem no legado: `pipeline/src/aurelio_pipeline/infra/escrita_readest.py:218`–`:245`
  - Critério de pronto: a versão aprovada anterior sobrevive a uma reprovação
  - Confiança: 🟢
- [ ] T-06, Validação independente com os nove checks
  - Origem no legado: `pipeline/src/aurelio_pipeline/validacao/paridade_readest.py:68`–`:294`
  - Critério de pronto: não importa agrupamento, escritor nem PyGlossary; aprova o artefato correto
  - Confiança: 🟢
- [ ] T-07, `ConferenciaReadest` (ambiente, cache por hash, reescritas, `npm ci`, execução)
  - Origem no legado: `pipeline/src/aurelio_pipeline/infra/conferencia_readest.py:59`–`:284`, `pipeline/conferencia_readest/fonte-readest.json`
  - Critério de pronto: cada falha de ambiente é `AmbienteConferenciaError` acionável; cache pronto dispensa a rede
  - Confiança: 🟢
- [ ] T-08, Roteiro `conferir.ts`, com `package.json` e `package-lock.json` fixando o `fflate`
  - Origem no legado: `pipeline/conferencia_readest/conferir.ts:1`
  - Critério de pronto: contrato de `contracts.md` §3
  - Confiança: 🟢
- [ ] T-09, Integração na CLI (`_alvo_readest`), na ordem do gate
  - Origem no legado: `pipeline/src/aurelio_pipeline/cli.py:118`
  - Critério de pronto: exceção depois da escrita descarta o preparo; exit 0 ou 3
  - Confiança: 🟢
- [ ] T-10, Runbook do Readest no `pipeline/README.md` e exclusões do cache e de `node_modules/` no `.gitignore`
  - Origem no legado: `pipeline/README.md`, `.gitignore`
  - Critério de pronto: geração, números esperados, importação, atualização da versão fixada e erros novos documentados
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Agrupamento: chave, ordem, páginas, destinos, relatório e determinismo (`pipeline/tests/test_agrupamento_readest.py`, 17 testes)
- [ ] TT-02, Escritor: artefato, `.ifo`, corpo, expectativa, erros e promoção (`pipeline/tests/test_escrita_readest.py`, 18 testes)
- [ ] TT-03, Validação: aprovação, páginas, índices, metadados, amostra e isolamento (`pipeline/tests/test_paridade_readest.py`, 11 testes)
- [ ] TT-04, Conferência com rede e subprocesso falsos: ambiente, cache e execução (`pipeline/tests/test_conferencia_readest.py`)
- [ ] TT-05, Integração com o código real do Readest, marcador `integracao`, pulada sem Node ou sem cache (`TestIntegracaoComReadest`)

## Ordem Sugerida
1. T-01 e T-02, depois T-03.
2. T-04 e T-05 em seguida; T-06 pode correr em paralelo, por ser independente por construção.
3. T-07 e T-08, depois T-09 e, por fim, T-10.

## Lacunas Pendentes (🔴)
Nenhuma.
