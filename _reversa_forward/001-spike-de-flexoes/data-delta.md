# Data delta: Spike de flexões

> Identificador: `001-spike-de-flexoes`
> Data: `2026-07-03`
> Modelo de referência: tabelas reais de `aurelio_normalized.db` (não há `_reversa_sdd/data-model.md`; o projeto nasceu greenfield e o banco é o modelo)

## 1. Mudanças no banco

**Nenhuma.** RN-02 fixa o banco como somente-leitura durante todo o spike: sem tabela nova, sem coluna nova, sem migração, sem correção de órfãs. A conexão SQLite deve ser aberta em modo read-only (`file:aurelio_normalized.db?mode=ro`) para que a regra seja estrutural, não disciplinar.

## 2. Leituras realizadas pelo spike

| Consulta (conceitual)                                                                        | Tabelas                                                                    | Uso                                          |
| -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------- |
| Lemas únicos + entries por lema (fusão de homônimos, ordem por `homonym`, depois `sort_key`) | `entries`                                                                  | Headwords do `.idx` (137.784 esperados)      |
| Pares (`entry_head`, `flexion`)                                                              | `flexions`                                                                 | Entrada do mapeamento do `.syn` (175.259)    |
| Pares (`infinitive`, `conjugation`)                                                          | `conjugations`                                                             | Entrada do mapeamento do `.syn` (869.119)    |
| Verbete completo dos 20 lemas do roteiro (definições, exemplos, locuções, notas, regência)   | `entries`, `definitions`, `examples`, `locutions`, `notes`, `verb_rection` | Corpo completo apenas dos lemas-alvo (RF-01) |
| Seleção auditável das 20 palavras do roteiro (D-08)                                          | `flexions`, `conjugations`, `entries`                                      | Roteiro fixo com query registrada            |

## 3. Estruturas em memória (efêmeras, sem persistência)

Versão mínima das entidades da spec `indice-de-flexoes.md#9-modelo-de-dados`, inline no script:

```
mapa_flexoes: dict[headword] -> set[forma]     // deduplicado; ambíguas viram entradas em N headwords
descartes:    {orfa: int, duplicada: int, identica: int}
orfas:        list[str]                         // lemas sem verbete, nominalmente
```

## 4. Artefatos novos produzidos (todos regeneráveis, fora do banco)

| Artefato                   | Local                                                   | Conteúdo                                                            | Versionado?                                       |
| -------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------- |
| Artefato StarDict do spike | `spike/001-flexoes/dist/`                               | `.ifo`, `.idx`, `.dict.dz`, `.syn`                                  | Não (gerado; ~dezenas de MB; uso pessoal — RN-03) |
| Relatório de cobertura     | `spike/001-flexoes/dist/relatorio-cobertura.json`       | entradas por tabela, gravadas, descartes por motivo, órfãs nominais | Sim (pequeno, é a auditoria do `.syn`)            |
| Roteiro de 20 palavras     | `_reversa_forward/001-spike-de-flexoes/roteiro.md`      | forma → lema esperado → resultado observado → latência              | Sim (instrumento de medida, RF-02)                |
| Relatório do spike         | `_reversa_forward/001-spike-de-flexoes/spike-report.md` | veredito GO/NO-GO, respostas às OQs, dados brutos                   | Sim (entregável do gate, RF-06)                   |

## 5. Contrato de integridade

- Entrada = gravadas + órfãs + duplicadas + idênticas (invariante do relatório JSON, herdada de RF-06 da spec `indice-de-flexoes`).
- Órfãs esperadas pelo levantamento de 2026-07-03: as formas de 11 infinitivos e 11 cabeças de flexão sem verbete correspondente. Desvio grande dessa ordem de grandeza indica erro no join, não no banco.
- Forma vazia ou só espaços em qualquer tabela de origem: geração aborta com o `id` do registro (EC-04); nenhum artefato parcial vale para o roteiro.
