# Flowchart — módulo `governanca-operacional`

> Gerado pelo reversa-archaeologist em 2026-07-03; revisto em 2026-10-15 (seção `[regen]` ativa e artefatos derivados fora do git).

## 1. Ciclo de vida do ativo de dados e dos artefatos derivados

```mermaid
flowchart TD
    O[JailBrake Aurelio<br/>extraction/aurelio_normalized.db] -- "sqlite3 .backup (2026-07-03)" --> L[Cópia local<br/>fonte de verdade]
    L -- "rclone copy ... gdrive:" --> G[(Google Drive<br/>gdrive:inculto-e-belo/)]
    G -- "rclone copy gdrive:... ." --> L
    L -. "*.db no .gitignore" .-> GIT[git/GitHub<br/>docs, meta e código]
    L -- "uv run aurelio-pipeline (mode=ro)" --> D[dist/<br/>aurelio-stardict/ e readest/]
    D -. "dist/ no .gitignore" .-> GIT
    D -- "cópia manual" --> K[KOReader<br/>macOS e Boox]
    D -- "importação na tela de dicionários" --> R[Readest do Mac<br/>sincroniza na nuvem privada da conta]
```

## 2. Shim do Harness e regeneração

```mermaid
flowchart TD
    H[./harness cmd] --> S[lê upstream_path de harness.toml via sed]
    S --> V{core existe no upstream?}
    V -- sim --> X[exec python main.py do core<br/>em ~/dev/harness]
    V -- não --> E[erro claro no stderr, exit 1]
    X -- "cmd = regen" --> RG["[regen]: cd pipeline && uv run aurelio-pipeline<br/>(só o alvo KOReader)"]
```

## 3. Banco mudado (atualização deliberada)

```mermaid
flowchart TD
    N[Banco regenerado] --> B[build]
    B --> C{contagens = manifesto?}
    C -- não --> F[ContagemDivergenteError, exit 2]
    F --> M[conferir proveniência e atualizar<br/>manifesto-integridade.json em commit próprio]
    M --> B
    C -- sim --> OK[segue o build]
```

Riscos mapeados: backup único no Drive; sem verificação automática de integridade logo após a restauração, embora o primeiro build confira esquema e contagens.
