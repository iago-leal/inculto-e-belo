# ADR-0009 — Guardar o artefato na nuvem privada do Readest não constitui publicação

> Retroativo, gerado pelo reversa-detective em 2026-10-15. Status: **aceita** (em vigor). Confidência: 🟢 (RN-08 de `_reversa_forward/003-dicionario-readest/requirements.md`, decisão do usuário em 2026-10-15; T021 do `actions.md`)

## Contexto

RB-11 proíbe publicar qualquer artefato derivado do Aurélio, e a privacidade da feature 002 previa que nenhum dado saísse do processo local. O Readest sincroniza dicionários importados entre os dispositivos da conta, guardando o pacote na nuvem dele. Sem uma decisão explícita, usar a sincronização pareceria violar RB-11.

## Decisão

Armazenar o artefato do Readest na nuvem privada vinculada à conta do próprio usuário, para uso nos dispositivos dele, **não constitui publicação**. Continuam proibidos:
- compartilhar o artefato com terceiros;
- versioná-lo no git;
- pôr conteúdo do Aurélio no repositório público, nem como dado de teste.

## Consequências

- RB-11 ganhou redação mais precisa, sem perda de substância.
- A importação de 2026-10-15 deixou o dicionário sincronizado na conta. Os arquivos importados têm hash idêntico ao do artefato aprovado.
- Uma futura distribuição por outro canal, como o WebDAV planejado em P-05, precisa reavaliar esta fronteira.
