# Regression watch — 002-build-completo-de-producao

> Gerado por `/reversa-coding` em 2026-07-03.
> A re-extração (`/reversa`, step-04) verifica cada item e registra o veredito no histórico abaixo.

## Watch items

| ID   | Origem (arquivo, seção)                        | Regra esperada após mudança                                                                                                                                                                                 | Tipo de verificação | Sinal de violação                                                                                             |
| ---- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------- |
| W001 | `_reversa_sdd/domain.md` §4 (invariantes)      | Baseline quantitativa vigente: 137.784 lemas únicos (`wordcount`) e 774.003 pares válidos (`synwordcount`), com 22 lemas órfãos / 748 formas                                                                | presença            | Extração reportar contagens diferentes **sem** commit correspondente de `pipeline/manifesto-integridade.json` |
| W002 | `_reversa_sdd/domain.md` §6 (RB-14)            | Split de `,` e `" ou "` em `flexions.flexion` documentado no domain e implementado em `pipeline/src/aurelio_pipeline/dominio/indice_flexoes.py` com teste                                                   | presença            | Regra sumir do domain.md, do código ou da suíte                                                               |
| W003 | `_reversa_sdd/domain.md` §3 (RB-10)            | Banco somente-leitura em todo o pipeline: abertura exclusivamente via URI `mode=ro` em `infra/repositorio.py`                                                                                               | redação             | Qualquer caminho de escrita no `.db` dentro de `pipeline/`                                                    |
| W004 | `_reversa_sdd/domain.md` §3 (RB-11)            | Artefatos derivados fora do git (`dist/` no `.gitignore`) e marcados "(uso pessoal)" no `bookname`                                                                                                          | presença            | `dist/` versionado, artefato publicado ou marca de uso pessoal removida                                       |
| W005 | `_reversa_sdd/domain.md` §3 (RB-12)            | Build determinístico e auditável: `relatorio-cobertura.json` com invariante `entrada = gravadas + descartes` e `parity-report.json` com seeds registradas, gravados a cada build                            | presença            | Build sem relatórios, invariante aberta ou seeds ausentes                                                     |
| W006 | `_reversa_sdd/architecture.md` §2 (P-01..P-04) | Os quatro componentes do pipeline existem como código em `pipeline/src/aurelio_pipeline/` com as fronteiras das specs (SQL só na infra; domínio puro; PyGlossary só no adaptador; validação sem PyGlossary) | presença            | Re-extração não encontrar os módulos ou encontrar SQL/PyGlossary fora da camada contratada                    |

## Observações (origem 🟡, sem peso de regressão)

- **O-01** — Gate de paridade (RN-04, spec `validacao-paridade` 🟡): nenhum artefato instalado/distribuído sem exit code 0; tolerância zero. Vigiar quando a feature de distribuição nascer.
- **O-02** — Manifesto de integridade (spec `ingestao-aurelio` 🟡): só contagens, sem hash (decisão em requirements §9); atualização sempre em commit próprio.
- **O-03** — `[regen]` do `harness.toml` habilitado: encerramento de sessão roda o build (~12 s) e pressupõe o `.db` presente; se virar incômodo, desabilitar é reversão de uma linha.
- **O-04** — Latência no e-ink permanece presumida (GO presumido do spike): a condição de monitoramento transfere-se ao artefato de produção instalado no Boox; fallback `--cobertura flexions-somente` disponível na CLI.

## Histórico de re-extrações

### Re-extração 2026-10-15 11:30

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | `domain.md` §4 mantém 137.784 e 774.003, com 22 órfãos e 748 formas; manifesto sem commit novo desde d6efb26 |
| W002 | 🟢 verde | RB-14 em `domain.md` §3 (promovida de §6, com ponteiro); `dividir_formas` em `dominio/indice_flexoes.py:20` e testes em `pipeline/tests/test_indice_flexoes.py` |
| W003 | 🟢 verde | RB-10 em `domain.md` §3; abertura só por URI `mode=ro` em `infra/repositorio.py:122`; nenhum INSERT, UPDATE, DELETE, CREATE ou commit em `pipeline/` |
| W004 | 🟢 verde | `dist/` ignorado (`.gitignore:28`); `bookname` «Aurélio (uso pessoal)» e «Aurélio (uso pessoal, Readest)»; a nuvem privada do Readest não é publicação (ADR-0009) |
| W005 | 🟢 verde | RB-12 em `domain.md` §3; `assert` da invariante em `dominio/indice_flexoes.py:78`; sementes gravadas no `parity-report.json` (`validacao/paridade.py:160`) |
| W006 | 🟢 verde | P-01..P-04 existem em `architecture.md` §2 com as fronteiras: SQL só em `infra/repositorio.py`, PyGlossary só em `infra/escrita_stardict.py`, validação sem PyGlossary (teste dedicado) |

## Arquivadas

_(vazio)_
