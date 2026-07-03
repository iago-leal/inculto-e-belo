# Legacy impact — 001-spike-de-flexoes

> Gerado por `/reversa-coding` em 2026-07-03 (rodada T001–T008 + T011). Atualizado na mesma data: T009/T010 dispensadas por decisão do usuário (medição no Boox presumida), T012/T013 concluídas — feature encerrada com as 13 ações fechadas e veredito **GO presumido** no `spike-report.md`.
> Âncora: `_reversa_sdd/architecture.md` (componentes) e `_reversa_sdd/domain.md` (regras).

## 1. Arquivos afetados

| Arquivo afetado                                | Componente (`architecture.md`) | Tipo                      | Severidade | Justificativa                                                                                                      |
| ---------------------------------------------- | ------------------------------ | ------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------ |
| `spike/001-flexoes/pyproject.toml` + `uv.lock` | S-01 `spike/001-flexoes`       | componente-novo           | LOW        | Ambiente pinado (PyGlossary 5.4.1 + python-idzip 0.3.9)                                                            |
| `spike/001-flexoes/gerar_spike.py`             | S-01                           | componente-novo           | MEDIUM     | Único código executável do repositório; implementa inline versões descartáveis de P-01/P-02/P-03 (D-04 do roadmap) |
| `spike/001-flexoes/README.md`                  | S-01                           | componente-novo           | LOW        | Reprodutibilidade exigida por RN-04                                                                                |
| `spike/001-flexoes/dist/aurelio-spike*/`       | S-01 → KOReader                | delta-de-contrato-externo | MEDIUM     | Novo contrato de arquivo (StarDict) consumido pelo KOReader; detalhado em `interfaces/artefato-stardict-spike.md`  |
| `aurelio_normalized.db`                        | C-01 `banco-lexical`           | — (leitura pura)          | —          | Aberto exclusivamente com `mode=ro`; zero escrita (RN-02/RB-10)                                                    |

Nenhum arquivo pré-existente do legado foi modificado, movido ou removido.

## 2. Diff conceitual por componente

- **C-01 `banco-lexical`:** intocado. O spike consome as consultas canônicas descritas em `_reversa_sdd/banco-lexical/design.md` e confirmou na prática duas caracterizações da extração: RB-14 (1.364 formas multi-valor divididas → 176.623 formas de flexão após split) e a ausência de formas vazias (EC-04 nunca disparou).
- **C-02 `governanca-operacional`:** intocado.
- **S-01 `spike/001-flexoes` (novo):** materializa o Fluxo Alternativo A da spec `indice-de-flexoes`. Descoberta relevante para as specs planejadas: os pares (forma, headword) únicos e válidos do banco somam **774.003**, não ~1M — a estimativa de `synwordcount ≥ 900.000` (RF-01 da feature) ignorava ~220 mil repetições legítimas de forma superficial entre pessoas/tempos. As specs `indice-de-flexoes` e `conversao-formato` devem herdar esse número como baseline quando forem implementadas.
- **P-01..P-05 (planejados):** nenhum código criado — conforme D-04 do roadmap, o investimento espera o veredito.

## 3. Preservadas (regras 🟢 do `domain.md` verificadas nesta rodada)

- RB-02 — homonímia preservada no banco; fusão por lema feita pelo consumidor (o spike funde: 143.376 entries → 137.784 headwords).
- RB-05 — ligações textuais lemma↔formas; exatamente 22 lemas órfãos detectados e listados nominalmente, banco não corrigido.
- RB-09 — `.db` fora do git; artefatos `dist/` também não versionados (ver nota abaixo).
- RB-10 — banco somente-leitura (conexão `mode=ro` estrutural).
- RB-11 — artefato de uso pessoal, sem publicação.
- RB-12 — regeneração determinística com relatório JSON auditável.
- RB-14 — separadores em `flexions.flexion` tratados por split.

## 4. Modificadas

Nenhuma regra 🟢 do legado foi alterada ou removida.

**Desvio de critério de aceite (nível feature, não legado):** RF-01 da feature fixava `synwordcount ≥ 900.000`; o valor real e correto é 774.003 (100% dos pares válidos). Documentado em `actions.md` §Notas de execução e a ser refletido no `spike-report.md` (T012).

**Nota de governança:** `dist/`, `.venv/` e `medicao-geracao.txt` do spike ainda não estão no `.gitignore` (que pertence ao legado e o Reversa não modifica). Recomendação ao mantenedor: adicionar `spike/001-flexoes/dist/`, `spike/001-flexoes/.venv/` e `spike/001-flexoes/*-stdout.txt`/`medicao-geracao.txt` antes do próximo commit, preservando RB-09/RB-11 (o artefato contém conteúdo do Aurélio).
