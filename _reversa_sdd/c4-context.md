# C4 Nível 1 — Contexto

> Gerado pelo reversa-architect em 2026-07-03; re-extraído em 2026-10-15. 🟢 existente, 🟡 planejado.

```mermaid
C4Context
    title Contexto — inculto-e-belo
    Person(iago_m, "iago (mantenedor)", "Mantém o ativo, roda o pipeline, faz backup")
    Person(iago_l, "iago (leitor)", "Lê no KOReader e no Readest e consulta palavras")
    System(ieb, "inculto-e-belo", "Léxico Aurélio em SQLite + pipeline que gera os dicionários StarDict do KOReader e do Readest")
    System_Ext(gdrive, "Google Drive", "Backup do .db via rclone")
    System_Ext(harness, "Harness (upstream ~/dev/harness)", "Governança de sessão e [regen]")
    System_Ext(koreader, "KOReader (macOS, Boox Air 4C)", "Consome o StarDict com um artigo por lema")
    System_Ext(readest, "Readest (Mac + nuvem da conta)", "Consome o StarDict com uma página por palavra")
    System_Ext(github, "GitHub readest/readest", "Código de busca fixado por commit, para a conferência")
    System_Ext(npm, "Registro npm", "fflate 0.8.3")
    System_Ext(origem, "JailBrake Aurelio", "Origem da extração (one-shot, concluída)")

    Rel(iago_m, ieb, "uv run aurelio-pipeline; sqlite3; backup")
    Rel(iago_l, koreader, "toca palavra em leitura")
    Rel(iago_l, readest, "consulta palavra em leitura")
    Rel(ieb, gdrive, "rclone copy (bidirecional)")
    Rel(ieb, harness, "exec do core via shim")
    Rel(ieb, koreader, "dist/aurelio-stardict/ (cópia manual)")
    Rel(ieb, readest, "dist/readest/aurelio-readest/ (importação manual)")
    Rel(ieb, github, "HTTPS, só na primeira obtenção")
    Rel(ieb, npm, "npm ci, só na primeira preparação")
    Rel(origem, ieb, "sqlite3 .backup (2026-07-03)")
```

## Leitura

- 🟢 O sistema não expõe serviço algum: é local e roda sob demanda. As fronteiras externas são o armazenamento (Drive), a governança (Harness), os dois leitores e, só na primeira conferência, o GitHub e o npm.
- 🟢 A nuvem do Readest guarda o dicionário importado na conta privada do usuário, o que não constitui publicação (ADR-0009).
- 🟡 A distribuição WebDAV (`sdd/distribuicao-webdav.md`) segue planejada e não implementada.
