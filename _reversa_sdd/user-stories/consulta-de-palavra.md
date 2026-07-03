# User story — Consulta de palavra em leitura

> Gerado pelo reversa-writer em 2026-07-03. Fluxo-alvo do produto (🟡 parcialmente futuro; o banco já suporta, o artefato StarDict ainda não existe).

**Como** iago-leitor, lendo literatura no KOReader do Boox,
**quero** tocar numa palavra como ela aparece no texto (flexionada, conjugada, capitalizada)
**para** ver o verbete completo do Aurélio em menos de 1 segundo, offline.

## Cenários

```gherkin
Dado o dicionário instalado no KOReader
Quando toco em "cantávamos" num romance
Então o popup abre o verbete "cantar" em < 1 s

Dado uma forma ambígua que flexiona dois lemas
Quando a toco
Então o popup lista as duas correspondências e eu escolho

Dado uma das 22 formas órfãs conhecidas
Quando a toco
Então não há resultado — comportamento aceito e documentado (RB-05)
```

## Estado

- Resolução forma→lema: 🟢 suportada pelo banco (`flexions`, `conjugations` indexadas).
- Entrega no dispositivo: 🟡 aguardando o pipeline StarDict; premissa de latência sob validação na feature `001-spike-de-flexoes` (RN-05).
