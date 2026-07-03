# C4 Nível 3 — Componentes do pipeline StarDict (planejado)

> Gerado pelo reversa-architect em 2026-07-03. Todo o nível é 🟡 PLANEJADO (specs SDD §8 de cada componente); as fronteiras vêm dos decision logs, não de código.

```mermaid
C4Component
    title Componentes — pipeline StarDict (alvo pós-spike)
    ContainerDb(db, "aurelio_normalized.db", "SQLite", "somente-leitura")

    Container_Boundary(p, "pipeline StarDict") {
        Component(ing, "ingestao-aurelio", "leitura/borda", "Agregados Verbete + iteradores de pares (flexions, conjugations)")
        Component(mapa, "indice-de-flexoes", "domínio puro, sem I/O", "MapaFlexoes + RelatorioCobertura (descartes: órfã/duplicada/idêntica)")
        Component(rend, "renderizador HTML", "domínio puro", "Verbete → artigo HTML autocontido (em conversao-formato)")
        Component(adapt, "adaptador PyGlossary", "infraestrutura", "Único ponto de acoplamento à biblioteca; escreve .ifo/.idx/.dict.dz/.syn")
        Component(orq, "orquestrador de build", "aplicação", "Streaming, escrita atômica em dist/, log estruturado")
        Component(val, "validacao-paridade", "verificação independente", "Parser StarDict próprio (stdlib); compara banco ↔ artefato")
    }

    Rel(ing, db, "SELECT mode=ro")
    Rel(ing, mapa, "pares (forma, lema)")
    Rel(ing, rend, "agregados Verbete")
    Rel(mapa, orq, "MapaFlexoes")
    Rel(rend, orq, "ArtigoStarDict")
    Rel(orq, adapt, "entradas + alternates")
    Rel(val, db, "releitura independente")
```

## Contratos entre componentes (das specs)

| Produtor → Consumidor         | Estrutura                                                                                         | Spec                             |
| ----------------------------- | ------------------------------------------------------------------------------------------------- | -------------------------------- |
| ingestao → indice-de-flexoes  | iteradores `(entry_head, flexion)` e `(infinitive, conjugation)`                                  | `sdd/indice-de-flexoes.md` RF-01 |
| indice-de-flexoes → conversao | `MapaFlexoes {entradas: [(forma, headword)]}` + `RelatorioCobertura`                              | `sdd/indice-de-flexoes.md` §9    |
| conversao → validacao         | `ResultadoBuild {headwords, sinonimos, duracao_s, arquivos}` + diretório `dist/aurelio-stardict/` | `sdd/conversao-formato.md` §9    |

## Relação com o spike (S-01)

O spike implementa versões **inline e descartáveis** de `ing`+`mapa`+`adapt` num único script, sem criar estes componentes — deliberado (D-04 do roadmap da feature 001) para não investir antes do gate.
