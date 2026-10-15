# Flowchart — módulo `pipeline-readest`

> Gerado pelo reversa-archaeologist em 2026-10-15.

## 1. Alvo Readest com gate de duas etapas (`_alvo_readest`)

```mermaid
flowchart TD
    H[headwords + mapa + lemas_frequentes] --> AG[agrupar: página de cada chave]
    AG --> EW[EscritorReadest.escrever<br/>dist/.readest-preparo-*]
    EW --> RA[relatorio-agrupamento.json]
    RA --> VA[executar_validacao_readest<br/>9 checks, independente]
    VA --> VJ[validacao-readest.json]
    VJ --> CF[ConferenciaReadest.conferir<br/>node conferir.ts]
    CF --> CJ[conferencia-readest.json]
    CJ --> D{validação E conferência aprovadas?}
    D -- sim --> PR[promover: remove a expectativa,<br/>troca dist/readest/ atomicamente, exit 0]
    D -- não --> RP[reprovar: preparo vai para dist/readest.reprovado/<br/>a versão aprovada fica intacta, exit 3]
    EW -. exceção depois da escrita .-> DS[descartar o preparo e relançar]
```

## 2. Destino de cada chave no índice (`agrupar`)

```mermaid
flowchart TD
    K[chave = texto.lower] --> L{é chave de lema?}
    L -- sim --> IL[idx-lema<br/>grafia = primeiro lema da sequência]
    L -- não --> M{forma de 2+ lemas?}
    M -- sim --> IC[idx-forma-combinada<br/>página própria com todos os artigos]
    M -- não --> S{página do lema é combinada?}
    S -- sim --> ID[idx-forma-direta<br/>aponta só para o artigo do lema dentro da página]
    S -- não --> SY[syn<br/>aponta para a entrada do lema no .idx]
```

Ordem dos artigos numa página: lemas coincidentes com a chave (grafia exata primeiro), depois vocabulário frequente, desempate alfabético sem diacríticos e pela grafia. Formas sem letra são descartadas antes.

## 3. Montagem do corpo (`_gravar`)

```mermaid
flowchart TD
    P1[páginas idx-lema, em ordem de índice] --> G1[grava artigos separados por hr<br/>e anota a posição do artigo do próprio lema]
    G1 --> P2[sequências idx-forma-combinada ainda não gravadas]
    P2 --> G2[grava cada sequência distinta uma vez]
    G2 --> IDX[.idx: grafia, offset, tamanho<br/>forma direta usa o trecho do artigo]
    IDX --> SYN[.syn: aponta só para entrada com a mesma sequência]
    SYN --> FP[impressão = sha256 idx+syn+corpo, 16 hex]
    FP --> OUT[.idx, .syn, .dict.dz mtime=0, .ifo com data do manifesto,<br/>expectativa-conferencia.tsv]
```

## 4. Preparação e execução da conferência

```mermaid
flowchart TD
    A[preparar] --> N{Node >= 22.18 e npm?}
    N -- não --> E1[AmbienteConferenciaError]
    N -- sim --> C{cache .pronto e SHA-256 dos reescritos ok?}
    C -- não --> DL[baixar 2 arquivos do commit fixado]
    DL --> H1{SHA-256 dos originais ok?}
    H1 -- não --> E1
    H1 -- sim --> RW[3 reescritas, exatamente 1 ocorrência cada]
    RW --> H2{SHA-256 dos reescritos ok?}
    H2 -- não --> E1
    H2 -- sim --> GC[grava cache e marcador]
    C -- sim --> NM
    GC --> NM{fflate 0.8.3 em node_modules?}
    NM -- não --> CI[npm ci] --> NM2{instalou?}
    NM2 -- não --> E1
    NM2 -- sim --> PRONTO
    NM -- sim --> PRONTO[pronto]
    PRONTO --> X[conferir: node conferir.ts, timeout 600 s]
    X --> T{resultado}
    T -- timeout --> REP[veredito reprovado]
    T -- código 0/1 + JSON --> V[veredito do roteiro]
    T -- outro código ou saída não JSON --> E1
```

## 5. Roteiro `conferir.ts`

```mermaid
flowchart LR
    S[StarDictReader real do Readest] --> K[para cada chave da expectativa:<br/>lookup, senão resolveSynonym]
    K --> C1{offset e tamanho = esperados?}
    S --> T[para cada trecho distinto:<br/>leitura por blocos vs gunzip integral]
    T --> C2{bytes idênticos?}
    C1 & C2 --> V[aprovado se nenhuma falha e expectativa não vazia]
```
