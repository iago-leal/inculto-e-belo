# pipeline-koreader, Tarefas de Implementação

> Gerado pelo reversa-writer em 2026-10-15.

## Pré-requisitos
- [ ] `pipeline-nucleo` entregando artigos, mapa e headwords
- [ ] PyGlossary 5.4.1 e python-idzip instalados pelo `uv sync`

## Tarefas

- [ ] T-01, Adaptador `EscritorStarDict` sobre o PyGlossary, com troca atômica e conferência dos 4 arquivos
  - Origem no legado: `pipeline/src/aurelio_pipeline/infra/escrita_stardict.py:31`
  - Critério de pronto: `.idx` com 137.784 entradas e `.syn` com 774.003; `FalhaGeracaoError` sem `.dict.dz`
  - Confiança: 🟢
- [ ] T-02, `LeitorStarDict` com validação estrutural
  - Origem no legado: `pipeline/src/aurelio_pipeline/validacao/leitor_stardict.py:18`, `:43`
  - Critério de pronto: cada defeito estrutural de `requirements.md` RF-04 detectado
  - Confiança: 🟢
- [ ] T-03, `executar_paridade` com os cinco checks e `ParityReport`
  - Origem no legado: `pipeline/src/aurelio_pipeline/validacao/paridade.py:41`, `:60`
  - Critério de pronto: amostras com sementes 20260703 e 20260704; veredito aprovado no banco atual
  - Confiança: 🟢
- [ ] T-04, Integração na CLI (`_alvo_koreader`) com os dois relatórios e o exit code
  - Origem no legado: `pipeline/src/aurelio_pipeline/cli.py:78`
  - Critério de pronto: exit 0 aprovado, 3 reprovado; mensagem «não instale»
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Leitor contra artefatos binários montados à mão, íntegros e corrompidos (`pipeline/tests/test_validacao.py`, `TestLeitor`)
- [ ] TT-02, Normalização de texto e extração do HTML (`TestNormalizacao`)
- [ ] TT-03, Paridade aprovada e reprovada por check (`TestParidade`)
- [ ] TT-04, Isolamento: a validação não importa o PyGlossary (`test_validacao_nao_importa_pyglossary`)
- [ ] TT-05, 🟡 O `EscritorStarDict` não tem teste unitário; é exercido só pelo build real, cuja paridade o verifica de ponta a ponta

## Ordem Sugerida
1. T-02 antes de T-01, para ter o oráculo independente pronto.
2. T-01, depois T-03 e, por último, T-04.

## Lacunas Pendentes (🔴)
Nenhuma.
