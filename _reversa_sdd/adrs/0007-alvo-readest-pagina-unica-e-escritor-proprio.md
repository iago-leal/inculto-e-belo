# ADR-0007 — Alvo Readest com uma página por palavra e escritor StarDict próprio

> Retroativo, gerado pelo reversa-detective em 2026-10-15. Status: **aceita** (em vigor). Confidência: 🟢 (commits 522fb77 e cc5ab10; `_reversa_forward/003-dicionario-readest/requirements.md` RN-01 a RN-06 e `roadmap.md` D-01 a D-11, D-17, D-18)

## Contexto

O Readest lê StarDict, mas devolve **um único** resultado por consulta e compara as palavras em minúsculas, por unidades UTF-16. Com o artefato do KOReader, a medição de 2026-10-15 mostrou três perdas:
- 132 verbetes colidiam por caixa;
- 4 ficavam inalcançáveis pela ordem do índice («à», «à clef», «à clé», «Å»);
- cerca de 24 mil formas abriam um verbete errado ou incompleto, entre elas «era», «foi» e «fosse».

O PyGlossary não grava índices na ordem do `cmpAscii` nem entradas que apontam para trechos de páginas já gravadas.

## Decisão

1. Criar um segundo alvo do mesmo pipeline (`--alvo readest` ou `ambos`), com o KOReader intacto como padrão.
2. Cada chave pesquisável abre uma página com **exatamente** os artigos de todos os lemas a que corresponde. Os artigos são os mesmos do KOReader (`renderizar_artigo`), unidos por `<hr>`.
3. A ordem dos artigos põe primeiro os lemas coincidentes com a chave, com a grafia exata à frente. Depois vem o vocabulário frequente (`entries.most_used`), com desempate alfabético sem diacríticos nem caixa.
4. As formas sem letra são descartadas; os lemas, nunca.
5. Um escritor próprio (stdlib e python-idzip) segue duas regras:
   - grava os índices na ordem do `cmpAscii` e cada sequência distinta de artigos uma única vez;
   - faz a forma de um só lema apontar para o artigo do lema dentro da página dele.
6. O `.ifo` é determinístico, com a data do manifesto e a impressão digital do conteúdo, e o gzip tem `mtime=0`.

## Alternativas descartadas (registradas no roadmap)

- Reaproveitar o artefato do KOReader: perde sentidos no Readest, por causa do resultado único.
- Estender o PyGlossary: não oferece a ordem nem os trechos compartilhados.
- Ordenar por código Unicode: diverge do `cmpAscii` fora do plano básico.

## Consequências

- O artefato do Readest tem 887.546 chaves, 160.302 entradas no `.idx`, 727.244 no `.syn` e cerca de 30 MB.
- `entries.most_used`, de semântica 🟡, passou a ter efeito na ordem das páginas.
- Peculiaridades do banco ficam visíveis, como «a» registrado como forma de «bretão», porque a regra de completude as exige.
- O build com os dois alvos sobe de cerca de 12 s para cerca de 68 s, com 1,4 GB de pico, porque o alvo Readest renderiza todos os artigos em memória.
