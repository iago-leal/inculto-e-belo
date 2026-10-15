# ADR-0006 — Pipeline de produção em camadas, com banco validado por manifesto e gate de paridade independente

> Retroativo, gerado pelo reversa-detective em 2026-10-15. Status: **aceita** (em vigor). Confidência: 🟢 (commit d6efb26; `_reversa_forward/002-build-completo-de-producao/roadmap.md` D-01 a D-14; código em `pipeline/`)

## Contexto

Com o GO do spike (ADR-0005), era preciso um build de produção que gerasse o Aurélio completo para o KOReader e fosse retomável por um mantenedor intermitente. As specs SDD já fixavam quatro componentes (ingestão, índice de flexões, conversão, validação) e o PyGlossary 5.4.1. Ficavam em aberto três questões: como impedir que um banco trocado gerasse um artefato silenciosamente errado, como impedir que um defeito do PyGlossary passasse despercebido e como manter a biblioteca substituível.

## Decisão

1. Pacote uv em `pipeline/`, com console script `aurelio-pipeline` e dependências pinadas em `uv.lock`.
2. Camadas com fronteiras rígidas:
   - `infra/repositorio.py` é o único dono do SQL e abre o banco em `mode=ro`;
   - `dominio/` é puro: modelos, índice de flexões e renderização;
   - `infra/escrita_stardict.py` é o único acoplamento ao PyGlossary;
   - `validacao/` lê o artefato com um parser próprio em stdlib.
3. A ingestão confere esquema e contagens contra `manifesto-integridade.json`, versionado, antes de expor qualquer dado. O manifesto só muda em commit próprio.
4. A paridade tem tolerância zero e relatório integral:
   - confere contagens e metadados do `.ifo`;
   - tira duas amostras de 500, com sementes fixas registradas;
   - o exit code é o gate: 0 aprovado, 2 erro nomeado, 3 reprovado.
5. Os relatórios de cobertura e de paridade são gravados a cada build, junto do artefato, fora do git.

## Justificativa

- Um validador que não compartilha código com o escritor detecta defeitos do escritor; validar com o próprio PyGlossary seria circular.
- O manifesto transforma «banco trocado» em erro nomeado com instrução, em vez de um artefato com números diferentes.
- O domínio puro permite testes rápidos com dados sintéticos: 50 testes na feature 002, 145 hoje.

## Consequências

- A primeira rodada de paridade reprovou e revelou um defeito real na extração de texto, corrigido antes da entrega.
- A troca do artefato acontece antes do veredito, então um reprovado fica em `dist/` com exit 3. O alvo Readest corrigiu isso com a promoção condicionada (ADR-0008); o KOReader manteve o comportamento original.
- O `[regen]` do Harness passou a rodar o build no encerramento de sessão.
