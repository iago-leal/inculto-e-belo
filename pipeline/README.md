# pipeline — build do dicionário StarDict do Aurélio

Converte o `aurelio_normalized.db` (raiz do repo) num dicionário StarDict
completo para o KOReader: **137.784 verbetes integrais** (definições, exemplos,
locuções, notas e regência) mais **774.003 formas flexionadas** no índice
`.syn` (tocar em "cantávamos" abre "cantar"). Todo build passa por validação de
paridade independente antes de valer: exit code 0 é a única evidência necessária
de que o artefato está íntegro.

> Conteúdo sob direitos autorais do Aurélio — **uso estritamente pessoal, jamais
> publicar o artefato** (nem commitar: `dist/` está no `.gitignore`).

## Reprodução do zero

Pré-requisitos: [uv](https://docs.astral.sh/uv/) (`brew install uv`) e o banco
restaurado na raiz do repo:

```zsh
cd ~/dev/inculto-e-belo
rclone copy gdrive:inculto-e-belo/aurelio_normalized.db .   # se o .db não existir
cd pipeline
uv sync          # instala PyGlossary 5.4.1 + python-idzip 0.3.9 (pinados no uv.lock)
uv run pytest    # 50 testes, < 5 s
uv run aurelio-pipeline
```

O comando único encadeia: smoke tests do banco → índice de flexões →
renderização + escrita StarDict → validação de paridade. Saída em
`../dist/aurelio-stardict/` com os 4 arquivos do formato mais
`relatorio-cobertura.json` e `parity-report.json`.

**Números esperados** (banco de 2026-07-03): `wordcount=137784`,
`synwordcount=774003`, 22 lemas órfãos (748 formas) reportados, veredito
`aprovado`, ~12 s de build, ~0,6 GB de pico, ~29 MB de artefato.

**Exit codes:** `0` aprovado · `2` erro nomeado (banco/manifesto/geração) ·
`3` paridade reprovada — **não instale um artefato reprovado**.

## Instalar no KOReader

- **macOS:** `cp -R ../dist/aurelio-stardict "$HOME/Library/Application Support/koreader/data/dict/"`
- **Boox / e-ink:** copiar `dist/aurelio-stardict/` por USB/MTP para `koreader/data/dict/`.

Remova o dicionário antigo (`aurelio-spike/`, se ainda existir) para evitar
resultados duplicados, e reinicie o KOReader. Nas primeiras leituras no e-ink,
observe a latência do toque (condição de monitoramento do spike 001): se o
típico passar de 1 s, gere o artefato reduzido e reinstale:

```zsh
uv run aurelio-pipeline --cobertura flexions-somente   # corta as 869k conjugações do .syn
```

## Quando o banco mudar (atualização deliberada)

Os smoke tests comparam as contagens do banco com `manifesto-integridade.json`.
Após regenerar o banco, o build falha com `ContagemDivergenteError` — é o
comportamento desejado. Para aceitar o banco novo:

1. Confira que a mudança era esperada (proveniência no README da raiz).
2. Atualize as contagens: `sqlite3 ../aurelio_normalized.db "SELECT COUNT(*) FROM <tabela>"` para cada tabela do manifesto.
3. Commite o `manifesto-integridade.json` novo **em commit próprio** (mudança explícita e auditável).
4. Rode o build; os números de `wordcount`/`synwordcount` esperados também mudam.

## Arquitetura (para o eu de daqui a 12 meses)

```
src/aurelio_pipeline/
├── cli.py                       orquestração + exit codes
├── erros.py                     erros nomeados (falha barulhenta é contrato)
├── infra/repositorio.py         ÚNICO dono do SQL; banco somente-leitura (mode=ro)
├── dominio/indice_flexoes.py    forma→headword, puro (split RB-14, descartes auditados)
├── dominio/renderizacao.py      Verbete→HTML integral, puro
├── infra/escrita_stardict.py    adaptador PyGlossary (único acoplamento à lib)
└── validacao/                   parser StarDict próprio (stdlib) + checks de paridade
```

Specs completas em `../_reversa_sdd/sdd/`; decisões e medições da feature em
`../_reversa_forward/002-build-completo-de-producao/`.

## Troubleshooting

| Sintoma                                | Ação                                                                           |
| -------------------------------------- | ------------------------------------------------------------------------------ |
| `BancoAusenteError`                    | `rclone copy gdrive:inculto-e-belo/aurelio_normalized.db ..`                   |
| `ContagemDivergenteError`              | Seção "Quando o banco mudar" acima                                             |
| `EsquemaInvalidoError`                 | Banco errado/antigo; conferir proveniência no README da raiz                   |
| `FalhaGeracaoError` citando `.dict.dz` | `uv sync` (python-idzip ausente do ambiente)                                   |
| Exit 3 (paridade reprovada)            | Ler `divergencias` no `parity-report.json`; corrigir e regenerar; não instalar |
| Popup vazio no KOReader                | Reiniciar o app (sessão fria) e conferir Configurações → Dicionário            |
