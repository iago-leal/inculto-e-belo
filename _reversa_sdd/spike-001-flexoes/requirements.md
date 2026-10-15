# spike-001-flexoes

> Gerado pelo reversa-writer em 2026-10-15 (re-extração). Unit da granularity `module`.
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral

Gerador descartável, mas reprodutível, da feature 001. Testa a hipótese de que o KOReader do Boox mantém latência aceitável com um `.syn` em escala real: índices completos (137.784 headwords e 774.003 formas), corpo trivial, e verbete completo só para os 22 lemas tirados do roteiro de medição de 20 palavras. O veredito registrado é **GO presumido**, por decisão do usuário, sem medição no aparelho (ADR-0005). O pipeline de produção o substituiu funcionalmente; o código permanece como evidência. 🟢

## Responsabilidades

- Gerar `aurelio-spike.{ifo,idx,syn,dict.dz}` em `spike/001-flexoes/dist/`, fora do git. 🟢
- Gerar um piloto só com os lemas do roteiro, para validar a mecânica do `.syn`. 🟢
- Oferecer o primeiro fallback de RN-05 da feature 001 (`--cobertura flexions-somente`). 🟢
- Gravar `relatorio-cobertura.json` com descartes, órfãs, duração e tamanhos. 🟢

## Regras de Negócio

- RB-10: banco aberto por URI `mode=ro`. 🟢
- RB-11: `bookname` «Aurélio spike (uso pessoal)»; `dist/` do spike fora do git. 🟢
- RB-14 e RB-16: split por `,` e `" ou "` e descartes classificados, reimplementados localmente. 🟢
- EC-04 da 001: forma vazia ou só com espaços aborta a geração com exit 2 e o id do registro. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Índices em escala real com corpo trivial | Must | `.idx` com 137.784 e `.syn` com 774.003 🟢 |
| RF-02 | Verbete completo para os lemas de `ROTEIRO_LEMAS` | Must | Os 22 lemas do roteiro abrem o verbete integral 🟢 |
| RF-03 | `--piloto` | Should | Artefato `aurelio-spike-piloto` com os lemas do roteiro 🟢 |
| RF-04 | `--cobertura flexions-somente` | Could | `.syn` sem as conjugações 🟢 |
| RF-05 | Relatório de cobertura | Must | `relatorio-cobertura.json` no diretório do artefato 🟢 |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Isolamento | Autocontido; não importa o pipeline | `spike/001-flexoes/gerar_spike.py` (imports) | 🟢 |
| Reprodutibilidade | Ambiente próprio por `uv` | `spike/001-flexoes/pyproject.toml`, `uv.lock` | 🟢 |
| Manutenibilidade | Lógica do índice duplicada com `dominio/indice_flexoes.py`, aceita por ser descartável | `spike/001-flexoes/gerar_spike.py:100`, `:112` contra `dominio/indice_flexoes.py:20`, `:32` | 🟢 **[Revisão 2026-10-15]** 🟡 → 🟢 |

## Critérios de Aceitação

```gherkin
Dado o banco de 2026-07-03
Quando o mantenedor executa "uv run python gerar_spike.py" em spike/001-flexoes/
Então spike/001-flexoes/dist/aurelio-spike/ contém os quatro arquivos e relatorio-cobertura.json
E o log registra build_ok com headwords=137784 e sinonimos=774003

Dado um registro de flexions com fragmento vazio
Quando o spike gera o mapa
Então a geração aborta com "EC-04 … geração abortada" e exit 2
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| RF-01, RF-02, RF-05 | Must | Sustentam a medição que a feature 001 previa |
| RF-03 | Should | Validação rápida da mecânica |
| RF-04 | Could | Fallback nunca acionado |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `spike/001-flexoes/gerar_spike.py` | `conectar`, `carregar_headwords`, `dividir_formas`, `construir_mapa`, `corpo_trivial`, `verbete_completo`, `gerar`, `main` | 🟢 |
| `spike/001-flexoes/README.md` | runbook | 🟢 |
