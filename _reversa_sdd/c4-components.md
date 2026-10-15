# C4 Nível 3 — Componentes do `aurelio-pipeline`

> Gerado pelo reversa-architect em 2026-07-03 (então planejado); re-extraído em 2026-10-15, agora a partir do código. Todo o nível é 🟢.

```mermaid
C4Component
    title Componentes — aurelio-pipeline
    ContainerDb(db, "aurelio_normalized.db", "SQLite", "somente-leitura")
    Container(conf, "conferencia_readest", "Node.js", "conferir.ts + código do Readest")

    Container_Boundary(p, "aurelio-pipeline") {
        Component(cli, "orquestracao (O-01)", "cli.py, erros.py", "Pré-verificação, alvos, exit code = pior entre alvos")
        Component(ing, "ingestao-aurelio (P-01)", "infra/repositorio.py", "Único dono do SQL; esquema + contagens vs manifesto; agregados Verbete")
        Component(idx, "indice-de-flexoes (P-02)", "dominio/indice_flexoes.py, puro", "Mapa forma→headword + RelatorioCobertura")
        Component(rend, "renderizacao (P-03 pura)", "dominio/renderizacao.py, puro", "Verbete → artigo HTML aberto por <b>lema</b>")
        Component(wk, "escrita KOReader (P-03 infra)", "infra/escrita_stardict.py", "Único acoplamento ao PyGlossary")
        Component(agr, "agrupamento-readest (R-01)", "dominio/agrupamento_readest.py, puro", "Chave → página, ordem, destino .idx/.syn")
        Component(wr, "escrita Readest (P-03 infra)", "infra/escrita_readest.py", "Escritor próprio, trechos compartilhados, promoção condicionada")
        Component(lei, "leitor StarDict (P-04)", "validacao/leitor_stardict.py, stdlib", "Leitura e validação estrutural")
        Component(par, "paridade KOReader (P-04)", "validacao/paridade.py", "Tolerância zero, amostras com sementes")
        Component(val, "validação Readest (P-04)", "validacao/paridade_readest.py", "Recálculo independente + busca simulada, 9 checks")
        Component(cr, "conferencia-readest (R-02)", "infra/conferencia_readest.py", "Ambiente, cache por hash, npm ci, subprocesso")
    }

    Rel(cli, ing, "validar, headwords, flexoes, artigos")
    Rel(ing, db, "SELECT mode=ro")
    Rel(cli, idx, "pares de formas")
    Rel(cli, rend, "agregados por lema")
    Rel(cli, wk, "headword, html, formas")
    Rel(wk, lei, "artefato em dist/aurelio-stardict/")
    Rel(par, lei, "usa")
    Rel(cli, agr, "headwords, mapa, frequentes")
    Rel(agr, wr, "PlanoPaginas")
    Rel(wr, val, "artefato no preparo")
    Rel(val, lei, "usa")
    Rel(cli, cr, "preparar / conferir")
    Rel(cr, conf, "node conferir.ts")
```

## Contratos entre componentes

| Produtor → Consumidor | Estrutura | Origem |
|-----------------------|-----------|--------|
| ingestão → índice | iteradores `(id, head, forma_bruta)` de `flexions` e `conjugations` | `infra/repositorio.py` |
| ingestão → renderização | `(lema, list[Verbete])` na ordem de fusão | idem |
| índice → escritas e validações | `dict[lema, list[forma]]` + `RelatorioCobertura` | `dominio/indice_flexoes.py` |
| renderização → escritas | `str` HTML por lema (em memória quando o Readest está no alvo) | `dominio/renderizacao.py` |
| escrita KOReader → paridade | diretório `dist/aurelio-stardict/` + `ResultadoBuild` | `infra/escrita_stardict.py` |
| agrupamento → escrita Readest | `PlanoPaginas` + `RelatorioAgrupamento` | `dominio/agrupamento_readest.py` |
| escrita Readest → validação e conferência | `ResultadoEscritaReadest` (preparo, artefato, expectativa TSV, impressão digital) | `infra/escrita_readest.py` |
| conferência → orquestração | JSON do roteiro com `veredito` normalizado | `infra/conferencia_readest.py` |
| validações → orquestração | `ParityReport` | `validacao/` |

## Independências deliberadas

- 🟢 A validação do Readest **não** importa o agrupamento nem o escritor: recalcula as páginas por conta própria.
- 🟢 O leitor StarDict não importa o PyGlossary.
- 🟢 A conferência só fala com o Node por subprocesso e por arquivos (artefato e expectativa); o código do Readest nunca entra no processo Python.
