# Spec Impact Matrix — inculto-e-belo

> Gerado pelo reversa-architect em 2026-07-03; re-extraído em 2026-10-15.
> Lê-se: mudança na LINHA impacta as COLUNAS marcadas. ● impacto direto, ○ impacto indireto.

## 1. Matriz componente × componente

| Mudança em ↓ / impacta → | C-01 banco | C-02 governança | P-01 ingestão | P-02 índice | P-03 conversão (render + escritas) | P-04 validação | R-01 agrupamento | R-02 conferência | O-01 orquestração | P-05 distribuição | S-01 spike |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **C-01 banco** (schema, conteúdo, contagens) | — | ● manifesto | ● | ● | ● | ● | ● (`most_used`) | ○ | ○ | ○ | ● |
| **C-02 governança** (backup, `[regen]`, `.gitignore`) | ○ | — | ○ | | | | | ○ (cache fora do git) | ● (`[regen]`) | ○ | ○ |
| **P-01 ingestão** (colunas requeridas, ordem de fusão) | | | — | ● | ● | ● (textos das definições) | ● (headwords, frequentes) | | ● | | |
| **P-02 índice** (split, descartes) | | | | — | ● (`.syn`) | ● (contagem e destinos) | ● (formas por chave) | ○ (expectativa) | | | ● (regras espelhadas) |
| **P-03 conversão** (HTML, formato, escritores) | | | | | — | ● (formato lido; `<b>lema</b>` e `<hr>`) | ○ | ● (bytes conferidos) | | ● (artefato) | ● (mesma ferramenta no KOReader) |
| **P-04 validação** (critérios) | | | | | ○ | — | | | ● (gate) | ● (gate de publicação) | |
| **R-01 agrupamento** (página, ordem, destino) | | | | | ● (leiaute do corpo) | ● (deve concordar com o recálculo independente) | — | ● (expectativa) | | | |
| **R-02 conferência** (versão fixada, Node) | | ○ (runbook) | | | | | | — | ● (pré-verificação, exit 2) | | |
| **O-01 orquestração** (alvos, exit codes) | | ● (`[regen]`) | ○ | | ○ | | | ○ | — | ● | |
| **Readest externo** (nova versão da busca) | | | | | ● (ordem/formato) | ● (simulação) | ● (comparação) | ● (fonte fixada) | | | |

## 2. Pontos de acoplamento mais sensíveis

1. **`entries.lemma` como chave textual universal:** toda mudança de normalização do lema repercute em formas, headwords, chaves do Readest e nos dois `.syn` (RB-05).
2. **Abertura `<b>lema</b>` e divisor `<hr>`:** a validação do Readest identifica artigos por essas marcas. Mudar o renderizador ou admitir `<hr>` no HTML do banco quebra o recorte (RB-03, D-10 da 003).
3. **Comparação do Readest:** `chave_readest` e `ordem_readest` (R-01) e `_comparacao` (P-04) precisam espelhar o `cmpAscii`. Uma versão do Readest que mude a comparação afeta escrita, validação e conferência ao mesmo tempo.
4. **`entries.most_used`:** de semântica 🟡, ordena os artigos não coincidentes; uma mudança de sentido no banco altera as páginas sem erro.
5. **PyGlossary 5.4.1 pinado:** afeta só o alvo KOReader e o spike; trocá-lo exige reexecutar a paridade.
6. **Manifesto de integridade:** é a única porta de entrada para um banco novo, e a atualização vale para os dois alvos.

## 3. Rastreabilidade feature → specs e código

| Feature | Ancora em | Código resultante |
|---------|-----------|-------------------|
| `001-spike-de-flexoes` | `sdd/indice-de-flexoes.md`, `sdd/conversao-formato.md`, `prd.md` | `spike/001-flexoes/` |
| `002-build-completo-de-producao` | `sdd/ingestao-aurelio.md`, `sdd/indice-de-flexoes.md`, `sdd/conversao-formato.md`, `sdd/validacao-paridade.md` | `pipeline/` (P-01..P-04, O-01) |
| `003-dicionario-readest` | `architecture.md` §2, `domain.md` RB-02/RB-11/RB-12, `sdd/conversao-formato.md` (decision log), `sdd/validacao-paridade.md` | R-01, R-02, `infra/escrita_readest.py`, `validacao/paridade_readest.py`, `--alvo` em O-01 |

## 4. Componente → unit de spec

> Acrescentado pelo reversa-reviewer em 2026-10-15, para ligar os IDs de componente às pastas geradas pelo Redator.

| Componente (`architecture.md` §2) | Unit |
|-----------------------------------|------|
| C-01 banco | `banco-lexical/` |
| C-02 governança | `governanca-operacional/` (`decisions.md` traz o delta de 2026-10-15) |
| P-01 ingestão, P-02 índice, O-01 orquestração, renderização de P-03 | `pipeline-nucleo/` |
| Escrita do KOReader (P-03) e paridade do KOReader (P-04) | `pipeline-koreader/` |
| Escrita do Readest (P-03), validação do Readest (P-04), R-01 agrupamento, R-02 conferência | `pipeline-readest/` |
| S-01 spike | `spike-001-flexoes/` |
| P-05 distribuição (planejado) | sem unit; spec greenfield em `sdd/distribuicao-webdav.md` |
