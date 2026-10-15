# C4 Nível 2 — Containers

> Gerado pelo reversa-architect em 2026-07-03; re-extraído em 2026-10-15. 🟢 existente, 🟡 planejado.

```mermaid
C4Container
    title Containers — inculto-e-belo
    Person(iago, "iago", "mantenedor e leitor")

    System_Boundary(ieb, "inculto-e-belo") {
        ContainerDb(db, "aurelio_normalized.db", "SQLite + FTS5, 189 MiB", "🟢 Fonte única: 14 tabelas de domínio")
        Container(gov, "governanca-operacional", "Bash + rclone + git + Harness", "🟢 Shim, [regen], backup, runbooks")
        Container(pipeline, "aurelio-pipeline", "Python 3.12+, uv, PyGlossary 5.4.1, python-idzip 0.3.9", "🟢 CLI: ingestão → índice → alvos KOReader e Readest com gates")
        Container(conf, "conferencia_readest", "Node.js ≥ 22.18, TypeScript apagável, fflate 0.8.3", "🟢 Roteiro conferir.ts com o código de busca do Readest")
        ContainerDb(dist, "dist/", "arquivos StarDict + relatórios JSON", "🟢 aurelio-stardict/, readest/, readest.reprovado/ (fora do git)")
        Container(spike, "spike/001-flexoes", "Python + uv + PyGlossary 5.4.1", "🟢 Gate concluído; descartável e reprodutível")
        Container(webdav, "distribuicao-webdav", "—", "🟡 Planejado (P-05)")
    }

    System_Ext(gdrive, "Google Drive", "backup")
    System_Ext(kor, "KOReader", "consumidor")
    System_Ext(rea, "Readest", "consumidor")
    System_Ext(gh, "GitHub + npm", "primeira obtenção da conferência")

    Rel(iago, gov, "opera runbooks")
    Rel(iago, pipeline, "uv run aurelio-pipeline --alvo")
    Rel(gov, gdrive, "rclone copy")
    Rel(gov, pipeline, "[regen] (só KOReader)")
    Rel(pipeline, db, "leitura mode=ro")
    Rel(spike, db, "leitura mode=ro")
    Rel(pipeline, conf, "subprocesso node conferir.ts")
    Rel(conf, gh, "HTTPS / npm ci, com cache")
    Rel(pipeline, dist, "escrita atômica; promoção condicionada no Readest")
    Rel(dist, kor, "cópia manual")
    Rel(dist, rea, "importação manual")
```

## Notas

- 🟢 Não há serviço residente: todos os containers são processos sob demanda do mantenedor.
- 🟢 `conferencia_readest` não tem estado próprio além do cache local (`.cache/<tag>/`) e de `node_modules/`, ambos fora do git e regeneráveis.
- 🟢 O spike não é mais exigido pelo fluxo de produção; fica como evidência reprodutível do veredito.
