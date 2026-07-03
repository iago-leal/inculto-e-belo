# C4 Nível 2 — Containers

> Gerado pelo reversa-architect em 2026-07-03. 🟢 existente, 🟡 planejado pelas specs SDD.

```mermaid
C4Container
    title Containers — inculto-e-belo
    Person(iago, "iago", "mantenedor e leitor")

    System_Boundary(ieb, "inculto-e-belo") {
        ContainerDb(db, "aurelio_normalized.db", "SQLite + FTS5, ~189 MB", "🟢 Fonte única: 14 tabelas de domínio")
        Container(gov, "governanca-operacional", "Bash + rclone + git", "🟢 Shim Harness, backup, runbook")
        Container(spike, "spike/001-flexoes", "Python + uv + PyGlossary 5.4.1", "🟡 Gate: artefato de spike em escala real")
        Container(pipeline, "pipeline StarDict", "Python (P-01..P-04)", "🟡 ingestão → índice de flexões + conversão → validação de paridade")
        Container(dist, "distribuicao-webdav", "Python/rclone/HTTP", "🟡 Publica artefato nos dispositivos")
    }

    System_Ext(gdrive, "Google Drive", "backup")
    System_Ext(kor, "KOReader (Boox Air 4C)", "consumidor")

    Rel(iago, gov, "opera runbook")
    Rel(gov, gdrive, "rclone copy")
    Rel(spike, db, "leitura mode=ro")
    Rel(pipeline, db, "leitura mode=ro")
    Rel(spike, kor, "instalação manual USB/MTP")
    Rel(pipeline, dist, "artefato validado")
    Rel(dist, kor, "WebDAV")
```

## Notas

- 🟡 O container `pipeline` só nasce após veredito GO do spike (ADR-0005); suas fronteiras internas estão no nível 3 (`c4-components.md`).
- 🟢 Não há serviço residente: todos os containers são processos sob demanda do mantenedor.
