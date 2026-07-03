# Legacy impact — 002-build-completo-de-producao

> Data: 2026-07-03 · Gerado por `/reversa-coding`
> Âncora: `_reversa_sdd/architecture.md` (componentes) e `_reversa_sdd/domain.md` (regras 🟢)

## 1. Arquivos afetados

| Arquivo afetado                                                               | Componente                                            | Tipo                      | Severidade | Justificativa                                                                                                                      |
| ----------------------------------------------------------------------------- | ----------------------------------------------------- | ------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `pipeline/pyproject.toml`, `pipeline/uv.lock`                                 | `ingestao-aurelio`..`validacao-paridade` (P-01..P-04) | componente-novo           | MEDIUM     | Manifesto e lock do pacote de produção; primeira dependência de runtime do projeto (PyGlossary 5.4.1, python-idzip 0.3.9, pinadas) |
| `pipeline/manifesto-integridade.json`                                         | `ingestao-aurelio` (P-01)                             | delta-de-dados            | MEDIUM     | Novo contrato versionado: contagens esperadas das 12 tabelas; muda apenas por commit deliberado                                    |
| `pipeline/src/aurelio_pipeline/infra/repositorio.py`                          | `ingestao-aurelio` (P-01)                             | componente-novo           | MEDIUM     | Materializa a spec: mode=ro, smoke tests, agregados `Verbete`, pares brutos                                                        |
| `pipeline/src/aurelio_pipeline/dominio/indice_flexoes.py`                     | `indice-de-flexoes` (P-02)                            | componente-novo           | MEDIUM     | Materializa a spec: split RB-14, descartes auditados, invariante                                                                   |
| `pipeline/src/aurelio_pipeline/dominio/renderizacao.py`, `dominio/modelos.py` | `conversao-formato` (P-03, metade pura)               | componente-novo           | MEDIUM     | Verbete → HTML integral; homônimos fundidos (consumidor aplica a fusão, RB-02 preservada no banco)                                 |
| `pipeline/src/aurelio_pipeline/infra/escrita_stardict.py`                     | `conversao-formato` (P-03, adaptador)                 | componente-novo           | MEDIUM     | Único ponto de acoplamento ao PyGlossary; escrita atômica sem retenção                                                             |
| `pipeline/src/aurelio_pipeline/validacao/`                                    | `validacao-paridade` (P-04)                           | componente-novo           | MEDIUM     | Parser StarDict próprio em stdlib + checks de tolerância zero; gate por exit code                                                  |
| `pipeline/src/aurelio_pipeline/cli.py`                                        | pipeline (orquestração)                               | componente-novo           | MEDIUM     | Comando único `aurelio-pipeline`; exit codes 0/2/3                                                                                 |
| `pipeline/tests/` (5 arquivos)                                                | todos os anteriores                                   | componente-novo           | LOW        | 50 testes, cobertura 96% em domínio+validação+repositório                                                                          |
| `pipeline/README.md`                                                          | `governanca-operacional` (C-02)                       | regra-nova                | LOW        | Runbook de reprodução do zero (RB-13)                                                                                              |
| `.gitignore`                                                                  | `governanca-operacional` (C-02)                       | contrato-alterado         | LOW        | `dist/` e `pipeline/.venv/` fora do git (estende a política de RB-09 aos derivados)                                                |
| `README.md` (raiz)                                                            | `governanca-operacional` (C-02)                       | contrato-alterado         | LOW        | Nova seção apontando o pipeline; nenhum conteúdo pré-existente removido                                                            |
| `harness.toml`                                                                | `governanca-operacional` (C-02)                       | contrato-alterado         | MEDIUM     | `[regen]` habilitado: o encerramento de sessão passa a rodar o build (~12 s) e exige o `.db` presente                              |
| `dist/aurelio-stardict/` (fora do git)                                        | artefato derivado                                     | delta-de-dados            | LOW        | Novo dado derivado regenerável; substitui o papel do artefato do spike                                                             |
| `~/Library/.../koreader/data/dict/` (fora do repo)                            | consumidor KOReader                                   | delta-de-contrato-externo | LOW        | `aurelio-spike/` removido; `aurelio-stardict/` instalado (roadmap §8)                                                              |

**Não tocados:** `aurelio_normalized.db` (zero escritas — mode=ro por construção), `spike/001-flexoes/` (congelado como registro, RN-08), `_reversa_sdd/` (extração intacta).

## 2. Diff conceitual por componente

Os quatro componentes P-01..P-04, que em `_reversa_sdd/architecture.md#2` existiam apenas como specs 🟡 PLANEJADO, agora têm código de produção — a mudança central desta feature é essa transição de planejado para existente, sem alterar nenhum comportamento do legado. O `banco-lexical` (C-01) permanece intocado na forma e no conteúdo: o pipeline o consome em somente-leitura e reporta as 22 órfãs sem corrigi-las, exatamente como RB-05/RB-10 contratam. A `governanca-operacional` (C-02) foi estendida em três pontos: a política de exclusão do git agora cobre os artefatos derivados (`dist/`), o README raiz ganhou a porta de entrada para o runbook do pipeline, e o `[regen]` do Harness passou a regenerar o dicionário a cada encerramento de sessão — este último é a única mudança de comportamento operacional pré-existente, e falha barulhenta se o banco estiver ausente. O spike S-01 perdeu o papel de artefato instalado (removido do KOReader) mas mantém o de registro histórico do gate.

## 3. Preservadas (regras 🟢 do domain.md intactas)

- **RB-01..RB-08** (schema): intocadas — o banco não sofreu nenhuma escrita; o pipeline respeita a ordem editorial (`position`) e a distinção editor/citation (RB-07) na renderização.
- **RB-02**: homonímia continua preservada no banco; a fusão por lema acontece só no consumidor (renderização), como a regra prescreve.
- **RB-05**: ligação por texto e as 22 órfãs continuam no banco; o pipeline as reporta nominalmente no `relatorio-cobertura.json`.
- **RB-09**: `.db` segue fora do git; a política foi _estendida_ (não alterada) para cobrir `dist/`.
- **RB-10**: banco somente-leitura em todo o ciclo — garantido por construção (`mode=ro`) e por teste.
- **RB-11**: uso estritamente pessoal — `bookname` explicita "(uso pessoal)", artefato fora do git.
- **RB-12**: regeneração determinística e auditável — relatórios JSON por build, seeds registradas.
- **RB-14**: split de `,`/`" ou "` implementado no domínio e coberto por teste.

## 4. Modificadas

Nenhuma regra 🟢 do `_reversa_sdd/domain.md` foi alterada ou removida. As únicas atualizações de contrato foram sobre artefatos 🟡 PLANEJADO das specs SDD, já previstas no requirements da feature:

- Métrica de `synwordcount` das specs `indice-de-flexoes`/`conversao-formato`: estimativa "≥ 900.000" substituída pelo alvo exato **774.003** (RN-03, herdado do spike e confirmado neste build).
- Specs P-01..P-04 deixam de ser "sem código": a próxima re-extração deve reclassificá-las de 🟡 PLANEJADO para 🟢 CONFIRMADO e apontar `pipeline/` como módulo.
