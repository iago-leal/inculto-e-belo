# Flowchart — módulo `spike-001-flexoes`

> Gerado pelo reversa-archaeologist em 2026-10-15. Código descartável, mas reprodutível; veredito GO presumido.

```mermaid
flowchart TD
    A[gerar_spike.py --piloto ou escala real<br/>--cobertura total ou flexions-somente] --> C[conectar mode=ro]
    C --> H[carregar headwords]
    H --> M[construir_mapa: split RB-14,<br/>descartes órfã, duplicada, idêntica]
    M --> B{lema de ROTEIRO_LEMAS (22)?}
    B -- sim --> VC[verbete completo]
    B -- não --> CT[corpo trivial]
    VC & CT --> G[PyGlossary: headword + formas como chaves alternativas]
    G --> W[escrita atômica em spike/001-flexoes/dist/aurelio-spike/]
    W --> R[relatorio-cobertura.json]
    R --> K[instalação manual no KOReader e roteiro de medição]
```
