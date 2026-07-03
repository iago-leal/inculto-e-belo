# Arquitetura — inculto-e-belo

> Gerado pelo reversa-architect em 2026-07-03
> Confidência: 🟢 CONFIRMADO (existe hoje), 🟡 PLANEJADO (specs SDD, ainda sem código)

## 1. Visão em uma frase

🟢 Um **ativo de dados** (SQLite normalizado do Aurélio) cercado por uma camada fina de governança, sobre o qual um **pipeline de conversão planejado** (specs SDD) produzirá dicionários StarDict para leitura offline no KOReader.

## 2. Componentes

### Existentes hoje (🟢)

| ID   | Componente               | Tecnologia        | Responsabilidade                                                                                           | Módulo (modules.json)    |
| ---- | ------------------------ | ----------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------ |
| C-01 | `banco-lexical`          | SQLite + FTS5     | Fonte única do léxico: 14 tabelas de domínio, hierarquia verbete→blocos→acepções, formas ligadas por texto | `banco-lexical`          |
| C-02 | `governanca-operacional` | Bash, rclone, git | Shim Harness, backup/restauração do ativo, exclusão do `.db` no git                                        | `governanca-operacional` |

### Planejados pelas specs SDD (🟡, sem código; fronteiras já decididas)

| ID   | Componente            | Spec de origem                           | Responsabilidade                                                                                 |
| ---- | --------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------ |
| P-01 | `ingestao-aurelio`    | `sdd/ingestao-aurelio.md`                | Ler o banco (somente-leitura) e entregar agregados `Verbete` + iteradores de pares de formas     |
| P-02 | `indice-de-flexoes`   | `sdd/indice-de-flexoes.md`               | Mapear forma→headword (domínio puro), com descartes auditados; materializa o `.syn`              |
| P-03 | `conversao-formato`   | `sdd/conversao-formato.md`               | Renderizar HTML e gerar StarDict via PyGlossary 5.4.1 pinado (adaptador isolado)                 |
| P-04 | `validacao-paridade`  | `sdd/validacao-paridade.md`              | Verificar equivalência banco↔artefato com parser StarDict próprio (stdlib)                       |
| P-05 | `distribuicao-webdav` | `sdd/distribuicao-webdav.md`             | Publicar o artefato nos dispositivos via WebDAV pessoal                                          |
| S-01 | `spike/001-flexoes`   | `_reversa_forward/001-spike-de-flexoes/` | **Gate**: valida a premissa do `.syn` em escala real no dispositivo antes do build (descartável) |

## 3. Fluxo de dependências (alvo)

```
banco-lexical (C-01)
   └→ ingestao-aurelio (P-01)
        ├→ indice-de-flexoes (P-02) ─┐
        └→ conversao-formato (P-03) ←┘  (mapa de flexões entra na mesma geração)
             └→ validacao-paridade (P-04)
                  └→ distribuicao-webdav (P-05) → KOReader (Boox Air 4C e demais)
spike S-01: atalho C-01 → artefato mínimo → dispositivo (antes de P-01..P-05 existirem)
```

Diagramas C4 em `c4-context.md`, `c4-containers.md`, `c4-components.md`; ERD completo em `erd-complete.md`.

## 4. Decisões arquiteturais em vigor

| Decisão                                                                                                      | Fonte        | Status         |
| ------------------------------------------------------------------------------------------------------------ | ------------ | -------------- |
| SQLite único normalizado como formato canônico                                                               | ADR-0001     | 🟢             |
| `.db` fora do git; backup rclone/Drive                                                                       | ADR-0002     | 🟢             |
| Harness com core no upstream                                                                                 | ADR-0003     | 🟢             |
| Specs antes de código; PyGlossary 5.4.1 pinado; banco somente-leitura                                        | ADR-0004     | 🟢             |
| Spike como gate do build completo (RN-05 pré-registrada)                                                     | ADR-0005     | 🟢 em execução |
| Camadas no pipeline: domínio puro (P-02, renderização) isolado de infra (PyGlossary, WebDAV) via adaptadores | specs SDD §8 | 🟡             |

## 5. Integrações externas

| Integração                              | Direção                       | Protocolo                        | Status       |
| --------------------------------------- | ----------------------------- | -------------------------------- | ------------ |
| Google Drive (`gdrive:inculto-e-belo/`) | bidirecional                  | rclone                           | 🟢 ativa     |
| `~/dev/harness` (core do Harness)       | saída (exec)                  | filesystem                       | 🟢 ativa     |
| KOReader (Boox Air 4C)                  | saída (artefato StarDict)     | USB/MTP no spike; WebDAV no alvo | 🟡 planejada |
| Origem `JailBrake Aurelio`              | entrada (one-shot, concluída) | `sqlite3 .backup`                | 🟢 histórica |

Não há APIs, filas, webhooks ou serviços de rede próprios.

## 6. Dívidas técnicas e riscos arquiteturais

| #     | Item                                                                                    | Severidade                                                | Evidência            |
| ----- | --------------------------------------------------------------------------------------- | --------------------------------------------------------- | -------------------- |
| DT-01 | README documenta 8 das 14 tabelas de domínio                                            | MEDIUM                                                    | `inventory.md` §5    |
| DT-02 | Integridade lemma↔formas sem constraint física (22 órfãs)                               | LOW (contratada como RB-05/RB-10: reportar, não corrigir) | `data-dictionary.md` |
| DT-03 | Backup único no Drive, sem verificação automática pós-restauração                       | MEDIUM                                                    | `dependencies.md` §2 |
| DT-04 | Semântica não documentada de `flexions.type`, `entries.head_type`, `conjugations.tense` | LOW p/ pipeline, MEDIUM p/ usos gramaticais futuros       | `domain.md` §6       |
| DT-05 | Nenhum teste automatizado sobre o ativo (integridade conferida manualmente)             | LOW hoje; sobe quando o pipeline nascer                   | `inventory.md` §6    |

## 7. Estado do ciclo forward

🟢 Feature ativa `001-spike-de-flexoes` em estágio `coding` pendente (13 ações), aguardando exatamente esta extração para satisfazer o gate do `/reversa-coding` (`architecture.md` + `domain.md`).
