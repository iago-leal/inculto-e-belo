# ADR-0008 — Gate de duas etapas no alvo Readest, com conferência pelo código real do leitor

> Retroativo, gerado pelo reversa-detective em 2026-10-15. Status: **aceita** (em vigor). Confidência: 🟢 (commits cc5ab10 e 314cd01; `roadmap.md` D-12 a D-16 e D-19 da feature 003; `interfaces/conferencia-readest.md`)

## Contexto

A validação em Python simula a busca do Readest, mas a simulação pode errar exatamente onde o artefato também erra: na comparação, na ordem ou na leitura por blocos do `.dict.dz`. O produto só vale se o Readest real abrir a página certa. Além disso, o alvo KOReader deixava um artefato reprovado em `dist/`.

## Decisão

1. **Etapa 1, validação independente:** `validacao/paridade_readest.py` não importa o agrupamento nem o escritor. Recalcula a página esperada de cada chave e simula a busca, com 9 checks e tolerância zero.
2. **Etapa 2, conferência:** obtém `stardictReader.ts` e `dictZip.ts` do Readest `v0.12.16`, pelo commit `3cc39ad7…`. Os hashes e o processo de execução seguem estas regras:
   - confere o SHA-256 dos originais;
   - aplica reescritas mecânicas mínimas e confere o SHA-256 do resultado;
   - executa `conferir.ts` no Node com `fflate` 0.8.3 travado;
   - testa todas as chaves e todos os trechos.
3. **Pré-verificação** do ambiente (Node ≥ 22.18, npm, cache ou rede) antes de gastar o build; a falha é `AmbienteConferenciaError` (exit 2).
4. **Promoção condicionada:**
   - o artefato nasce num diretório de preparo;
   - aprovado nas duas etapas, sobe por rename atômico para `dist/readest/`;
   - reprovado, vai para `dist/readest.reprovado/`, e a versão aprovada anterior fica intacta.
5. O `[regen]` do Harness continua só com o KOReader, para que o encerramento de sessão não dependa de Node nem de rede.

## Justificativa

- Executar o código real do leitor é a evidência mais forte possível sem abrir o aplicativo, e cobre o leitor por blocos do `.dict.dz`, que a simulação Python não reproduz.
- Fixar por commit e hash torna a conferência reprodutível e à prova de alteração silenciosa; o código AGPL-3.0 fica só em cache local, sem redistribuição.

## Consequências

- O projeto passou a depender de Node.js e, na primeira obtenção, de rede.
- O Node 26 recusou propriedades de parâmetro do `dictZip.ts` e removeu o modo de transformação de tipos. A solução passou de uma para três reescritas, cada uma com exatamente uma ocorrência e hash do resultado versionado, sem dependência nova.
- Último build: validação com 887.546 de 887.546 páginas certas; conferência com 887.546 chaves e 147.263 trechos íntegros.
- Uma versão nova do Readest que mude a busca exige atualizar `fonte-readest.json`, conforme o procedimento do README.
