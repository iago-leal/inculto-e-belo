# Regression watch — 001-spike-de-flexoes

> Criado por `/reversa-coding` em 2026-07-03. Regras que precisam continuar verdadeiras nas próximas extrações reversas. Nenhuma regra 🟢 do legado foi modificada nesta feature; os watch items abaixo são do tipo `presença`: fatos 🟢 dos quais o veredito do spike depende — se uma re-extração os contradisser, o veredito precisa ser reavaliado.

## Watch items

| ID   | Origem (arquivo, seção)                         | Regra esperada após mudança                                                                                                         | Tipo de verificação | Sinal de violação                                                                   |
| ---- | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ----------------------------------------------------------------------------------- |
| W001 | `_reversa_sdd/domain.md` §3 RB-05               | Ligações lemma↔formas continuam textuais com exatamente 22 lemas órfãos (11 infinitivos + 11 cabeças)                               | presença            | Contagem de órfãs ≠ 22 no relatório de cobertura de uma regeneração                 |
| W002 | `_reversa_sdd/domain.md` §6 RB-14               | `flexions.flexion` mantém o fenômeno de formas múltiplas por linha (separadores `,` e `" ou "`), tratado por split nos consumidores | presença            | Re-extração deixa de documentar RB-14, ou novo separador aparece sem tratamento     |
| W003 | `_reversa_sdd/domain.md` §4                     | Baseline: 143.376 entries / 137.784 lemas únicos / 175.259 flexions / 869.119 conjugations                                          | presença            | Qualquer contagem divergente sem regeneração deliberada do banco                    |
| W004 | `_reversa_sdd/domain.md` §3 RB-10               | Banco somente-leitura para todo o ciclo forward (conexões `mode=ro`)                                                                | presença            | Qualquer código do pipeline abrindo o banco sem `mode=ro`                           |
| W005 | `_reversa_sdd/domain.md` §3 RB-11               | Artefatos derivados do Aurélio nunca publicados (uso pessoal)                                                                       | presença            | Artefato StarDict versionado no git ou distribuído fora dos dispositivos do usuário |
| W006 | `_reversa_sdd/data-dictionary.md` §conjugations | Mapa dos tempos 1–13 permanece válido (1=pres. ind. … 13=particípio)                                                                | redação             | Re-extração renomear/reordenar o mapa sem nova evidência                            |

## Observações (sem peso de regressão — origem 🟡 ou descoberta desta rodada)

- O-01: pares (forma, headword) únicos e válidos = **774.003** (não ~1M como estimado). Baseline para `synwordcount` das futuras implementações de `indice-de-flexoes`/`conversao-formato`; recalcular após qualquer regeneração do banco.
- O-02: geração em escala real: 4,9 s e 462 MB de pico no MacBook do mantenedor — margens folgadas contra RNF-01/RNF-02 da spec `conversao-formato` (dados oportunistas de RF-07, corpo trivial; corpo completo será maior).
- O-03: `python-idzip==0.3.9` é exigência prática para `.dict.dz` com PyGlossary 5.4.1 (sem ele o writer degrada silenciosamente para `.dict`); as futuras specs de `conversao-formato` devem pinar também essa dependência.

## Histórico de re-extrações

<!-- preenchido pelo /reversa (step-04) nas próximas extrações -->

## Arquivadas

<!-- itens com 3 vereditos verdes consecutivos, movidos conforme setup.json#watch.archive-after -->
