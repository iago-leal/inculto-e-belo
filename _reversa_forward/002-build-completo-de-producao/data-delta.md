# Data delta — 002-build-completo-de-producao

> Data: 2026-07-03 · Diff conceitual sobre o modelo extraído em `_reversa_sdd/`
> Referências: `_reversa_sdd/erd-complete.md`, `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/domain.md#4`

## 1. Banco de origem: zero mudanças

O `aurelio_normalized.db` não ganha, perde nem altera campo algum (RN-01: `mode=ro` por construção). As 22 órfãs conhecidas continuam no banco e continuam sendo **reportadas, não corrigidas** (RB-05/RB-10). Nenhuma migração.

Tabelas consumidas pelo pipeline (leitura apenas), conforme RF-03 da spec `ingestao-aurelio`:

`entries`, `word_class_blocks`, `word_classes`, `definitions`, `rubrics`, `examples`, `locutions`, `locution_definitions`, `notes`, `verb_rection`, `flexions`, `conjugations` — 12 tabelas. As FTS (`fts_*`) e as ortográficas (`orthographic_*`) ficam fora (NG-04 da ingestão; ortográficas sem papel no verbete renderizado desta entrega).

## 2. Dados derivados novos

### 2.1 `pipeline/manifesto-integridade.json` (versionado no git) 🟢

Contrato dos smoke tests (RF-01; D-10 do roadmap — só contagens, sem hash):

```json
{
  "gerado_em": "2026-07-03",
  "banco_referencia": "aurelio_normalized.db",
  "contagens": {
    "entries": 143376,
    "word_class_blocks": 168361,
    "definitions": 259337,
    "examples": 54726,
    "locutions": 22168,
    "notes": 28903,
    "flexions": 175259,
    "conjugations": 869119,
    "verb_rection": 6170
  }
}
```

As contagens acima vêm do baseline 2026-07-03 (`_reversa_sdd/domain.md#4`, `inventory.md#5`); `word_classes`, `rubrics` e `locution_definitions` entram no manifesto com os valores levantados na implementação (o inventário não os contou — conferir com `SELECT COUNT(*)` na primeira execução e registrar). Atualização do manifesto é sempre commit deliberado (Fluxo Alternativo A da spec de ingestão).

### 2.2 `dist/aurelio-stardict/` (fora do git) 🟢

Artefato StarDict de produção — contrato detalhado em `interfaces/artefato-stardict.md`. Invariantes: `wordcount=137784`, `synwordcount=774003` (RN-03; recalculáveis a cada regeneração do banco).

### 2.3 `dist/aurelio-stardict/relatorio-cobertura.json` (fora do git) 🟢

Mesmo esquema validado no spike (`RelatorioCobertura` da spec `indice-de-flexoes` §9, estendido na prática):

```
entrada_linhas   {flexions, conjugations}      linhas lidas das tabelas
entrada_formas   {flexions, conjugations}      formas após split RB-14
gravadas         int                           pares únicos no .syn (774.003 no baseline)
descartes        {orfa, duplicada, identica}   contadores auditáveis
orfas            [str]                         22 lemas, nominalmente
headwords_com_formas  int
```

Invariante: `Σ entrada_formas = gravadas + Σ descartes` (RF-03; verificada por teste e por assert em runtime).

### 2.4 `dist/aurelio-stardict/parity-report.json` (fora do git) 🟡

Esquema da spec `validacao-paridade` §9 (`ParityReport`), com as seeds das duas amostras registradas. Fica fora do git porque cita lemas e trechos de definição sob direitos autorais (spec §12). O veredito também sai no exit code, então o git não precisa do relatório para a auditoria do gate — o log estruturado do build registra o resultado.

## 3. Estruturas em memória (contratos internos entre camadas)

Sem persistência própria; definem as fronteiras das camadas (specs §9 de cada componente):

| Estrutura                                                                                               | Produtor → Consumidor                                | Fonte                          |
| ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------ |
| `Verbete` (agregado com blocos, definições, exemplos, locuções, notas, regências)                       | `infra/repositorio` → `dominio/renderizacao`         | `ingestao-aurelio.md#9`        |
| Pares `(head, forma)` brutos, uma linha da tabela por par — o split de RB-14 é regra do domínio (RF-03) | `infra/repositorio` → `dominio/indice_flexoes`       | `indice-de-flexoes.md#6` RF-01 |
| `MapaFlexoes` (headword → formas ordenadas) + `RelatorioCobertura`                                      | `dominio/indice_flexoes` → `infra/escrita_stardict`  | `indice-de-flexoes.md#9`       |
| `ResultadoBuild` (totais, duração, bytes por arquivo)                                                   | `infra/escrita_stardict` → `cli` (log) e `validacao` | `conversao-formato.md#9`       |

## 4. Mudanças em arquivos de governança

| Arquivo            | Mudança                                            | Motivo                                                                                                                   |
| ------------------ | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `.gitignore`       | + `dist/`, + `pipeline/.venv/`                     | Artefato e venv regeneráveis fora do git (D-14)                                                                          |
| `README.md` (raiz) | + ponteiro para `pipeline/README.md`               | Retomabilidade (RB-13); a regra non-destructive do Reversa não se aplica ao `/reversa-coding`, que pode editar o projeto |
| `harness.toml`     | candidato: descomentar `[regen]` apontando o build | Opcional; avaliar no coding — agora existe artefato derivado a regenerar                                                 |

## 5. Migrações

n/a — nenhum dado existente muda de forma ou de lugar. A única operação de troca é a substituição do dicionário instalado no KOReader (`aurelio-spike/` → `aurelio-stardict/`), coberta no roadmap §8.
