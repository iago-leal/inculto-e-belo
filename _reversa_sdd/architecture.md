# Arquitetura — inculto-e-belo

> Gerado pelo reversa-architect em 2026-07-03; re-extraído em 2026-10-15, depois das features 001, 002 e 003
> Confidência: 🟢 CONFIRMADO (existe hoje no código), 🟡 PLANEJADO ou INFERIDO, 🔴 LACUNA

## 1. Visão em uma frase

🟢 Um **ativo de dados** (o SQLite normalizado do Aurélio) cercado por uma camada fina de governança. Sobre ele, um **pipeline Python em camadas** gera, sob demanda, dois dicionários StarDict de uso pessoal, um para o KOReader e outro para o Readest, e cada um só vale depois de aprovado no seu gate.

## 2. Componentes

### Existentes hoje (🟢)

| ID | Componente | Tecnologia | Responsabilidade | Módulo (modules.json) | Código |
|----|------------|------------|------------------|-----------------------|--------|
| C-01 | `banco-lexical` | SQLite + FTS5 | Fonte única do léxico: 14 tabelas de domínio, hierarquia verbete→blocos→acepções, formas ligadas por texto | `banco-lexical` | `aurelio_normalized.db` |
| C-02 | `governanca-operacional` | Bash, rclone, git, Harness | Shim e `[regen]`, backup e restauração, exclusões do git, runbooks | `governanca-operacional` | `harness`, `harness.toml`, `.gitignore`, READMEs |
| P-01 | `ingestao-aurelio` | Python, sqlite3 (stdlib) | Único dono do SQL; abre em `mode=ro`, valida esquema e contagens contra o manifesto, entrega agregados `Verbete` e pares de formas | `pipeline-nucleo` | `infra/repositorio.py`, `manifesto-integridade.json` |
| P-02 | `indice-de-flexoes` | Python puro | Mapa forma→headword com split RB-14 e descartes auditados | `pipeline-nucleo` | `dominio/indice_flexoes.py` |
| P-03 | `conversao-formato` | Python; PyGlossary 5.4.1 (KOReader), escritor próprio (Readest), python-idzip 0.3.9 | Metade pura: `Verbete → HTML`. Metade de infraestrutura: dois adaptadores de escrita StarDict | `pipeline-nucleo`, `pipeline-koreader`, `pipeline-readest` | `dominio/renderizacao.py`, `infra/escrita_stardict.py`, `infra/escrita_readest.py` |
| P-04 | `validacao-paridade` | Python (stdlib) | Leitor StarDict próprio e dois validadores de tolerância zero: paridade do KOReader e validação independente do Readest | `pipeline-koreader`, `pipeline-readest` | `validacao/leitor_stardict.py`, `validacao/paridade.py`, `validacao/paridade_readest.py` |
| R-01 | `agrupamento-readest` | Python puro | Para cada chave do Readest: artigos da página, ordem e destino no índice | `pipeline-readest` | `dominio/agrupamento_readest.py` |
| R-02 | `conferencia-readest` | Python + Node.js (subprocesso), TypeScript apagável, fflate 0.8.3 | Obtém o código de busca do Readest por commit fixado e confere o artefato com ele; segunda etapa do gate | `pipeline-readest` | `infra/conferencia_readest.py`, `conferencia_readest/` |
| O-01 | `orquestracao` | Python (argparse, logging) | CLI `aurelio-pipeline`: pré-verificação, ingestão e índice uma vez, alvos, exit code agregado | `pipeline-nucleo` | `cli.py`, `erros.py` |
| S-01 | `spike/001-flexoes` | Python + PyGlossary | Gate concluído (GO presumido); código descartável mantido reprodutível | `spike-001-flexoes` | `spike/001-flexoes/gerar_spike.py` |

Fronteiras verificadas nesta re-extração 🟢:
- o SQL só aparece em `infra/repositorio.py`;
- o PyGlossary só aparece em `infra/escrita_stardict.py`;
- `validacao/` importa só o leitor próprio e os erros, nunca o agrupamento, os escritores ou o PyGlossary;
- o Node só é invocado por subprocesso em `infra/conferencia_readest.py`;
- nenhum caminho de escrita no `.db`.

### Planejados (🟡, sem código)

| ID | Componente | Spec de origem | Responsabilidade |
|----|------------|----------------|------------------|
| P-05 | `distribuicao-webdav` | `sdd/distribuicao-webdav.md` | Publicar o artefato nos dispositivos via WebDAV pessoal. Hoje a instalação no KOReader é manual, e o Readest sincroniza pela conta |

## 3. Fluxo de dependências

```
banco-lexical (C-01)
   └→ ingestao-aurelio (P-01)  ← manifesto-integridade.json
        ├→ indice-de-flexoes (P-02)
        └→ renderização (P-03, metade pura)
             │
             ├─ alvo KOReader (padrão):
             │    escrita via PyGlossary (P-03) → dist/aurelio-stardict/ → paridade (P-04) → exit 0/3
             │
             └─ alvo Readest:
                  agrupamento (R-01) → escritor próprio (P-03) → preparo
                    → validação independente (P-04) → conferência no Node (R-02)
                    → promoção para dist/readest/ ou dist/readest.reprovado/

orquestração (O-01) encadeia tudo; pré-verifica R-02 antes da ingestão quando o Readest está no alvo
distribuição: manual (KOReader por cópia; Readest por importação + nuvem da conta); P-05 segue planejado
spike S-01: atalho C-01 → artefato de índices reais → KOReader (concluído)
```

Diagramas C4 em `c4-context.md`, `c4-containers.md` e `c4-components.md`; ERD em `erd-complete.md`.

## 4. Decisões arquiteturais em vigor

| Decisão | Fonte | Status |
|---------|-------|--------|
| SQLite único normalizado como formato canônico | ADR-0001 | 🟢 |
| `.db` fora do git; backup rclone/Drive | ADR-0002 | 🟢 |
| Harness com core no upstream | ADR-0003 | 🟢 |
| Specs antes de código; PyGlossary 5.4.1 pinado para o KOReader; banco somente-leitura | ADR-0004 | 🟢 (o pino vale só para o alvo KOReader desde a 003) |
| Spike como gate do build completo | ADR-0005 | 🟢 executada (GO presumido) |
| Pipeline em camadas, manifesto de integridade, paridade independente com exit code como gate | ADR-0006 | 🟢 |
| Alvo Readest com página única por palavra e escritor StarDict próprio | ADR-0007 | 🟢 |
| Gate de duas etapas no Readest com o código real do leitor; promoção condicionada; `[regen]` só no KOReader | ADR-0008 | 🟢 |
| Nuvem privada do Readest não constitui publicação | ADR-0009 | 🟢 |

## 5. Integrações externas

| Integração | Direção | Protocolo | Status |
|------------|---------|-----------|--------|
| Google Drive (`gdrive:inculto-e-belo/`) | bidirecional | rclone | 🟢 ativa |
| `~/dev/harness` (core do Harness) | saída (exec) | filesystem | 🟢 ativa |
| KOReader (macOS e Boox Air 4C) | saída (artefato StarDict) | cópia manual (pasta `data/dict/`, USB/MTP) | 🟢 ativa |
| Readest (Mac e dispositivos da conta) | saída (artefato StarDict) | importação manual na tela de dicionários; sincronização pela nuvem privada da conta | 🟢 ativa desde 2026-10-15 |
| GitHub (`raw.githubusercontent.com/readest/readest`) | entrada (dois arquivos .ts por commit fixado) | HTTPS, só na primeira obtenção | 🟢 ativa |
| Registro npm (`fflate` 0.8.3) | entrada | `npm ci`, só na primeira preparação | 🟢 ativa |
| Origem `JailBrake Aurelio` | entrada (one-shot) | `sqlite3 .backup` | 🟢 histórica |
| WebDAV pessoal | saída | HTTP | 🟡 planejada (P-05) |

Não há APIs, filas, webhooks ou serviços residentes: tudo roda como processo sob demanda do mantenedor.

## 6. Dívidas técnicas e riscos arquiteturais

| # | Item | Severidade | Evidência |
|---|------|------------|-----------|
| DT-01 | ~~README documenta 8 das 14 tabelas~~ | **resolvida** na feature 001: o README lista as 14 | `README.md` |
| DT-02 | Integridade lemma↔formas sem constraint física (22 órfãs) | LOW: contratada como reportar, não corrigir | `relatorio-cobertura.json` |
| DT-03 | Backup único no Drive, sem verificação automática pós-restauração | MEDIUM, mitigada: o primeiro build confere esquema e contagens | `dependencies.md` §3 |
| DT-04 | Semântica não documentada de `entries.most_used` (L-04) | MEDIUM desde a 003, porque agora ordena as páginas do Readest | `domain.md` §6 |
| DT-05 | ~~Nenhum teste automatizado~~ | **resolvida** no pipeline: 145 testes, cobertura de 91% a 100% em domínio e validação. O spike segue sem testes, por ser descartável | `pipeline/tests/` |
| DT-06 | O alvo KOReader troca o artefato antes do veredito; um reprovado fica em `dist/` | LOW: o exit 3 e a mensagem protegem, mas não há bloqueio físico | `infra/escrita_stardict.py` |
| DT-07 | Dependência de Node.js em evolução rápida: o Node 26 já exigiu reescritas no código do Readest | MEDIUM | `fonte-readest.json#reescritas` |
| DT-08 | O README da raiz e o docstring do pacote não citam o alvo Readest | LOW | `README.md`, `aurelio_pipeline/__init__.py` |
| DT-09 | A lógica do índice de flexões está duplicada no spike | LOW: o spike é descartável | `spike/001-flexoes/gerar_spike.py` |
| DT-10 | O build com os dois alvos usa 1,4 GB de pico por renderizar todos os artigos em memória (D-18) | LOW no Mac do mantenedor | notas da T019 da 003 |

## 7. Estado do ciclo forward

🟢 As features 001, 002 e 003 estão em `done`. A 003 tem adendo de sync, que esta re-extração supera; a 002 não teve adendo, e seu delta foi absorvido aqui. Não há feature ativa em andamento.
