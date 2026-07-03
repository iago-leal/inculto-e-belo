# User story — Retomada fria após meses de pausa

> Gerado pelo reversa-writer em 2026-07-03. 🟢 fluxo operacional existente.

**Como** iago-mantenedor-futuro, voltando ao projeto após meses,
**quero** restaurar o ambiente completo guiado só pelo README e pelos artefatos do Reversa/Harness
**para** continuar de onde parei sem arqueologia.

## Cenários

```gherkin
Dado um clone limpo sem o .db
Quando executo o comando de restauração do README
Então o banco chega íntegro (integrity_check ok) e as contagens-baseline conferem

Dado a sessão anterior encerrada pelo Harness
Quando abro nova sessão
Então .harness/estado-da-sessao.md e o plan.md do Reversa me dizem o próximo passo

Dado o pipeline forward em andamento
Quando leio _reversa_forward/001-spike-de-flexoes/onboarding.md
Então consigo executar o spike de ponta a ponta sem contexto além dos documentos
```

## Estado

- Runbook de restauração: 🟢 (README).
- Verificação automática pós-restauração: 🟡 proposta em `governanca-operacional/tasks.md` T-03.
