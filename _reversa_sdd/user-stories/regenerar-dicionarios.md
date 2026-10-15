# User story — Regenerar os dicionários depois de uma pausa

> Gerado pelo reversa-writer em 2026-10-15. Entregue pelas features 002 e 003 (🟢).

**Como** iago-mantenedor, voltando ao projeto depois de meses,
**quero** regenerar os dicionários com um comando e saber, pelo código de saída, se posso instalá-los
**para** nunca levar ao Boox ou ao Readest um artefato que diverge do banco.

## Cenários

```gherkin
Dado um clone limpo com o banco restaurado do Google Drive
Quando executo "cd pipeline && uv sync && uv run aurelio-pipeline --alvo ambos"
Então os dois artefatos são gerados, os relatórios dizem "aprovado" e o processo termina com exit 0

Dado que o banco mudou e o manifesto não foi atualizado
Quando executo o build
Então ele para com ContagemDivergenteError e exit 2, antes de escrever qualquer artefato
E a mensagem manda atualizar o manifesto em commit próprio

Dado que o artefato do Readest reprovou na conferência
Quando o build termina com exit 3
Então a versão aprovada anterior segue em dist/readest/ e o reprovado está em dist/readest.reprovado/ para diagnóstico

Dado que encerro a sessão pelo Harness
Quando o [regen] roda
Então só o alvo KOReader é regenerado, sem precisar de Node nem de rede
```

## Estado

- Build e gates: 🟢 145 testes; último build com os dois alvos aprovado (68 s).
- Runbook: 🟢 `pipeline/README.md`, com reprodução do zero, números esperados e 13 sintomas de troubleshooting.
- Instalação no Boox: 🟡 manual, por cópia; a distribuição por WebDAV (P-05) segue planejada.
