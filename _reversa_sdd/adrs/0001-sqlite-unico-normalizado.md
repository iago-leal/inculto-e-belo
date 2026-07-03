# ADR-0001 — Um único arquivo SQLite normalizado como formato canônico do léxico

> Retroativo, gerado pelo reversa-detective em 2026-07-03. Status: **aceita** (em vigor). Confidência: 🟢 (evidência em commit f431607 e README §Proveniência)

## Contexto

O léxico do Aurélio foi extraído do app Android (projeto `JailBrake Aurelio`) e precisava de um formato de longa duração, consultável por qualquer ferramenta, para servir de base a aplicações de gramática normativa.

## Decisão

Consolidar tudo num único arquivo SQLite normalizado (`aurelio_normalized.db`, ~189 MB, 14 tabelas de domínio + FTS5), importado por `sqlite3 .backup` com WAL consolidado e integridade conferida contra a origem.

## Justificativa

- SQLite é estável, ubíquo, sem servidor e legível daqui a décadas — alinhado ao perfil de mantenedor único intermitente.
- Normalização preserva a estrutura editorial (blocos de classe, acepções, rubricas) que o formato do app original escondia.
- Arquivo único simplifica backup, restauração e proveniência.

## Consequências

- Todo consumidor (pipeline StarDict, futuras aplicações) lê o mesmo ativo; nenhuma cópia derivada é fonte de verdade.
- O arquivo é grande demais para o GitHub → exige a decisão complementar ADR-0002.
- As ligações textuais lemma↔formas (sem FK) herdam-se da origem e viram contrato dos consumidores (RB-05).
