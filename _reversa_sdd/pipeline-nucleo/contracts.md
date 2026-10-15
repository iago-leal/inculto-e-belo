# pipeline-nucleo, Contratos externos

> Gerado pelo reversa-writer em 2026-10-15. Contrato da CLI com o operador e com o `[regen]` do Harness.

## Linha de comando

```
aurelio-pipeline [--db PATH] [--manifesto PATH] [--dist PATH]
                 [--cobertura {total,flexions-somente}]
                 [--alvo {ambos,koreader,readest}]
```

| Opção | Padrão | Efeito |
|-------|--------|--------|
| `--db` | `<repo>/aurelio_normalized.db` | Banco lido em `mode=ro` |
| `--manifesto` | `<repo>/pipeline/manifesto-integridade.json` | Contagens esperadas e data de referência |
| `--dist` | `<repo>/dist` | Raiz da saída |
| `--cobertura` | `total` | `flexions-somente` exclui as conjugações do índice |
| `--alvo` | `koreader` | `readest` ou `ambos` |

## Exit codes 🟢

| Código | Significado | Ação do operador |
|--------|-------------|------------------|
| 0 | Todos os alvos pedidos aprovados | Instalar ou importar |
| 2 | `ErroPipeline`: banco, manifesto, geração, artefato ou ambiente da conferência | Ler a mensagem, que traz a instrução |
| 3 | Algum alvo reprovado no gate | Não instalar nem importar; ler os relatórios |

## Saídas em disco

| Caminho | Alvo | Conteúdo |
|---------|------|----------|
| `dist/aurelio-stardict/` | KOReader | 4 arquivos StarDict, `relatorio-cobertura.json` e `parity-report.json` |
| `dist/readest/aurelio-readest/` | Readest | Só os 4 arquivos importáveis |
| `dist/readest/relatorios/` | Readest | `relatorio-agrupamento.json`, `validacao-readest.json` e `conferencia-readest.json` |
| `dist/readest.reprovado/` | Readest | Último reprovado, com relatórios e expectativa |

## Integração com o Harness

`harness.toml` → `[regen] command = "cd pipeline && uv run aurelio-pipeline"`, só com o alvo KOReader (D-19 da 003). 🟢
