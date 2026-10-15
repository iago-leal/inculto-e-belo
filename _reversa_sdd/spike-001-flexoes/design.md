# spike-001-flexoes, Design Técnico

> Gerado pelo reversa-writer em 2026-10-15.

## Interface

```
uv run python gerar_spike.py [--piloto] [--db PATH] [--cobertura {total,flexions-somente}]
```

Exit 0 em sucesso; 2 em `FormaAnomalaError` (EC-04). Outras exceções não são tratadas e terminam com o traceback do Python. 🟢

## Fluxo Principal (`gerar_spike.py:314`)

1. `conectar`: URI `mode=ro`. 🟢
2. `carregar_headwords`: lema → ids de `entries`. 🟢
3. `construir_mapa`: split por `SEPARADORES`, classificação e relatório; com `--piloto`, restrito a `ROTEIRO_LEMAS`. 🟢
4. Import tardio do PyGlossary; glossário com `bookname` «Aurélio spike (uso pessoal)», com o sufixo « [piloto]» quando for o caso. 🟢
5. Para cada lema, `verbete_completo` se estiver no roteiro, senão `corpo_trivial` (título, classe e a frase «corpo de teste do spike»); `newEntry([lema, *formas], html, defiFormat="h")`. 🟢
6. Escrita num temporário, com `dictzip=True` e `sametypesequence="h"`, e substituição do artefato anterior do próprio spike. 🟢
7. `relatorio-cobertura.json` e impressão do `.ifo` no stdout. 🟢

## Dependências

- `banco-lexical`, só leitura.
- PyGlossary e python-idzip, no ambiente próprio do spike.

## Decisões de Design Identificadas

| Decisão | Evidência | Confiança |
|---------|-----------|-----------|
| Spike como gate antes da produção | ADR-0005 | 🟢 |
| Corpo trivial para isolar o custo do índice | Docstring do módulo | 🟢 |
| Código não reaproveitado pela produção | Ausência de import cruzado | 🟢 |

## Observabilidade

Logs `headwords …`, `mapa gravadas=… descartes=… orfas=…`, `progresso verbetes_adicionados=…` e `build_ok duracao_s=… headwords=… sinonimos=…`. Saídas de medição em `geracao-stdout.txt` e `medicao-geracao.txt`, ambas fora do git. 🟢

## Riscos e Lacunas

- 🟡 A medição no Boox prevista pela feature 001 não foi feita; o GO é presumido. O risco de latência migrou para o artefato de produção, que tem o mesmo `.syn`.
