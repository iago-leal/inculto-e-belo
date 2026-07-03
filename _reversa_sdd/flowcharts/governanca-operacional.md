# Flowchart — módulo `governanca-operacional`

> Gerado pelo reversa-archaeologist em 2026-07-03.

## 1. Ciclo de vida do ativo de dados

```mermaid
flowchart TD
    O[JailBrake Aurelio<br/>extraction/aurelio_normalized.db] -- "sqlite3 .backup (2026-07-03)" --> L[Cópia local<br/>fonte de verdade]
    L -- "rclone copy ... gdrive:" --> G[(Google Drive<br/>gdrive:inculto-e-belo/)]
    G -- "rclone copy gdrive:... ." --> L
    L -. "*.db no .gitignore" .-> GIT[git/GitHub<br/>só docs e meta]
```

## 2. Shim do Harness

```mermaid
flowchart TD
    H[./harness cmd] --> S[lê upstream_path de harness.toml via sed]
    S --> V{core existe no upstream?}
    V -- sim --> X[exec python main.py do core<br/>em ~/dev/harness]
    V -- não --> E[erro claro no stderr, exit 1]
```

Risco operacional mapeado: backup único no Drive; sem verificação automática de integridade pós-restauração (runbook manual no README).
