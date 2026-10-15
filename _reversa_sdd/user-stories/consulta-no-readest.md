# User story — Consulta de palavra no Readest

> Gerado pelo reversa-writer em 2026-10-15. Entregue pela feature 003 (🟢 importado no Readest do Mac em 2026-10-15, com sync pela conta do usuário).

**Como** iago-leitor, lendo no Readest do Mac ou do iPhone,
**quero** selecionar uma palavra como ela aparece no texto (flexionada, conjugada, capitalizada)
**para** ver numa única página todos os verbetes do Aurélio a que ela pode corresponder.

## Cenários

```gherkin
Dado o dicionário «Aurélio (uso pessoal, Readest)» importado e habilitado
Quando seleciono "cantávamos"
Então a página abre o verbete "cantar"

Dado uma palavra que é lema e também forma de outro lema, como "a"
Quando a seleciono
Então a página mostra primeiro o artigo do próprio lema e depois os demais, separados por uma linha horizontal

Dado uma palavra que só difere de outro lema pela caixa, como "A" e "a"
Quando seleciono qualquer das duas
Então a mesma página abre, com o lema grafado em minúsculas à frente

Dado uma forma sem nenhuma letra, como "/"
Quando a seleciono
Então não há resultado, comportamento aceito e listado no relatório de agrupamento (RB-21)
```

## Estado

- Página única por palavra: 🟢 887.546 chaves conferidas com o código real do Readest v0.12.16.
- Importação e sync: 🟢 feitos pelo usuário em 2026-10-15; arquivos no disco com hash idêntico ao do artefato.
- Aparência do divisor no tema escuro: 🟡 sem conferência visual explícita (O-05 da 003).
- iPhone: 🟡 chega pelo sync da conta; não houve verificação no aparelho registrada.
