# C4 Nível 1 — Contexto

> Gerado pelo reversa-architect em 2026-07-03. 🟢 existente, 🟡 planejado.

```mermaid
C4Context
    title Contexto — inculto-e-belo
    Person(iago_m, "iago (mantenedor)", "Mantém o ativo, roda o pipeline, faz backup")
    Person(iago_l, "iago (leitor)", "Lê no KOReader e toca palavras para consultar")
    System(ieb, "inculto-e-belo", "Léxico Aurélio normalizado em SQLite + pipeline StarDict (planejado)")
    System_Ext(gdrive, "Google Drive", "Backup do .db via rclone")
    System_Ext(harness, "Harness (upstream ~/dev/harness)", "Governança de sessão")
    System_Ext(koreader, "KOReader (Boox Air 4C)", "Leitor e-ink; consome dicionários StarDict")
    System_Ext(origem, "JailBrake Aurelio", "Origem da extração (one-shot, concluída)")

    Rel(iago_m, ieb, "consulta sqlite3, gera artefatos, backup")
    Rel(iago_l, koreader, "toca palavra em leitura")
    Rel(ieb, gdrive, "rclone copy (bidirecional)")
    Rel(ieb, harness, "exec do core via shim")
    Rel(ieb, koreader, "artefato StarDict (USB no spike; WebDAV no alvo)", "🟡")
    Rel(origem, ieb, "sqlite3 .backup (2026-07-03)")
```

## Leitura

- O sistema não expõe serviço algum: tudo é local e offline; as fronteiras externas são armazenamento (Drive), governança (Harness) e o consumidor final (KOReader).
- A única integração nova prevista pelas specs é a distribuição WebDAV (`sdd/distribuicao-webdav.md`), que reutiliza infraestrutura já existente do ecossistema `koreader-notas` do mantenedor. 🟡
