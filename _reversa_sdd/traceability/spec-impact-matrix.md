# Spec Impact Matrix — inculto-e-belo

> Gerado pelo reversa-architect em 2026-07-03.
> Lê-se: mudança na LINHA impacta as COLUNAS marcadas. ● impacto direto, ○ impacto indireto.

## 1. Matriz componente × componente

| Mudança em ↓ / impacta →                                | banco-lexical | governanca  | ingestao (P-01) |          indice-flexoes (P-02)          |       conversao (P-03)       |     validacao (P-04)      |   distribuicao (P-05)   |     spike (S-01)      |
| ------------------------------------------------------- | :-----------: | :---------: | :-------------: | :-------------------------------------: | :--------------------------: | :-----------------------: | :---------------------: | :-------------------: |
| **banco-lexical (C-01)** — schema/conteúdo              |       —       | ○ (runbook) |        ●        |                    ●                    |              ●               |             ●             |            ○            |           ●           |
| **governanca (C-02)** — backup/paths                    |       ○       |      —      |        ○        |                                         |                              |                           |            ○            |           ○           |
| **ingestao-aurelio (P-01)** — contratos de leitura      |               |             |        —        |             ● (iteradores)              |        ● (agregados)         |             ○             |                         |                       |
| **indice-de-flexoes (P-02)** — regras de descarte       |               |             |                 |                    —                    |           ● (.syn)           | ● (paridade de sinônimos) |                         | ● (regras espelhadas) |
| **conversao-formato (P-03)** — HTML/StarDict/ferramenta |               |             |                 |       ○ (headwords p/ resolução)        |              —               |     ● (formato lido)      | ● (artefato publicado)  | ● (mesma ferramenta)  |
| **validacao-paridade (P-04)** — critérios               |               |             |                 |                                         |              ○               |             —             | ● (gate de publicação)  |                       |
| **distribuicao-webdav (P-05)** — destino/fluxo          |               |             |                 |                                         |                              |                           |            —            |                       |
| **spike (S-01)** — veredito RN-05                       |               |             |        ○        | ● (OQ-01/OQ-02 fecham ou reabrem specs) | ● (OQ-01/OQ-02 oportunistas) |                           | ○ (D-09: USB vs WebDAV) |           —           |

## 2. Pontos de acoplamento mais sensíveis

1. **`entries.lemma` como chave textual universal** — qualquer mudança de normalização do lema repercute em flexions, conjugations, headwords do StarDict e no `.syn` inteiro (RB-05).
2. **Fusão de homônimos por lema** — definida em `conversao-formato` (RF-01) mas consumida por `indice-de-flexoes` (RF-02) e pelo spike (RF-01 da feature): os três precisam da mesma regra.
3. **PyGlossary 5.4.1 pinado** — trocar a versão invalida o veredito do spike (D-02) e exige revalidação de paridade (P-04).
4. **Critério RN-05 do spike** — NO-GO propaga: 1º fallback altera P-02 (cobertura do `.syn`), 2º altera P-03 (dois dicionários), 3º reabre o decision log de P-03.

## 3. Rastreabilidade feature → specs

| Artefato forward                             | Ancora em                                                                                                                              |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `001-spike-de-flexoes/requirements.md`       | `sdd/indice-de-flexoes.md` (OQ-01/02, EC-05, fluxo alt. A), `sdd/conversao-formato.md` (OQ-01/02, decision log), `prd.md` (§3, §6, §8) |
| `001-spike-de-flexoes/roadmap.md`            | decision logs das duas specs + princípios do mantenedor                                                                                |
| `001-spike-de-flexoes/actions.md` (13 ações) | roadmap D-01..D-10                                                                                                                     |
