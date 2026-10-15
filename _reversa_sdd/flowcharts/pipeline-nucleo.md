# Flowchart — módulo `pipeline-nucleo`

> Gerado pelo reversa-archaeologist em 2026-10-15.

## 1. Orquestração da CLI (`executar`)

```mermaid
flowchart TD
    A[aurelio-pipeline --alvo X --cobertura Y] --> P{readest no alvo?}
    P -- sim --> PV[ConferenciaReadest.preparar<br/>Node, cache, npm ci]
    P -- não --> I
    PV --> I[RepositorioAurelio.validar<br/>esquema + contagens vs manifesto]
    I --> IX[construir_mapa<br/>flexions + conjugations se total]
    IX --> R{readest no alvo?}
    R -- sim --> RM[renderizar todos os artigos em memória]
    R -- não --> K
    RM --> K{koreader no alvo?}
    K -- sim --> AK[_alvo_koreader]
    K -- não --> AR
    AK --> AR{readest no alvo?}
    AR -- sim --> ARD[_alvo_readest]
    AR -- não --> FIM
    ARD --> FIM[exit = max dos códigos dos alvos]
    I -. ErroPipeline .-> E2[exit 2]
    PV -. AmbienteConferenciaError .-> E2
```

## 2. Ingestão e validação do banco

```mermaid
flowchart TD
    O[_abrir] --> X{arquivo existe?}
    X -- não --> BA[BancoAusenteError<br/>com comando rclone]
    X -- sim --> C[connect file:...?mode=ro, timeout 5 s]
    C --> Q{SELECT 1 FROM sqlite_schema}
    Q -- locked/busy --> BI[BancoIndisponivelError]
    Q -- outro erro --> BC[BancoCorrompidoError]
    Q -- ok --> V[validar]
    V --> ES{12 tabelas e colunas requeridas?}
    ES -- não --> EI[EsquemaInvalidoError<br/>lista todas as divergências]
    ES -- sim --> CT{contagens = manifesto?}
    CT -- não --> CD[ContagemDivergenteError]
    CT -- sim --> OK[smoke_tests_ok]
```

## 3. Classificação de cada forma (`construir_mapa`)

```mermaid
flowchart TD
    L[linha id, head, forma_bruta] --> D[dividir_formas: split por , e ou]
    D --> V{forma ou fragmento vazio?}
    V -- sim --> FA[FormaAnomalaError com tabela e id]
    V -- não --> O{head é headword?}
    O -- não --> OR[descarte órfã]
    O -- sim --> ID{forma == head?}
    ID -- sim --> IDE[descarte idêntica]
    ID -- não --> DU{par já visto?}
    DU -- sim --> DUP[descarte duplicada]
    DU -- não --> G[gravada em mapa head → formas]
    G --> INV[assert: entrada = gravadas + descartes]
```

## 4. Renderização de um artigo

```mermaid
flowchart LR
    V[lema + verbetes homônimos] --> B["&lt;b&gt;lema&lt;/b&gt;"]
    B --> S{mais de um verbete?}
    S -- sim --> N[seções numeradas 1., 2., ...]
    S -- não --> U[seção única]
    N --> C[cabeçalho, etimologia, blocos e acepções,<br/>exemplos, notas, locuções, regência]
    U --> C
    C --> T{artigo > 1 MB?}
    T -- sim --> W[advertência no log]
    T -- não --> H[HTML do artigo]
    W --> H
```
