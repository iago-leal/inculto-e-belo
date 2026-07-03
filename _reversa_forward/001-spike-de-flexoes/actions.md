# Actions: Spike de flexões — validação do lookup de formas no KOReader

> Identificador: `001-spike-de-flexoes`
> Data: `2026-07-03`
> Roadmap: `_reversa_forward/001-spike-de-flexoes/roadmap.md`

## Resumo

| Métrica                     | Valor                                                                    |
| --------------------------- | ------------------------------------------------------------------------ |
| Total de ações              | 13                                                                       |
| Paralelizáveis (`[//]`)     | 3                                                                        |
| Maior cadeia de dependência | 10 (T001 → T003 → T004 → T006 → T007 → T008 → T009 → T010 → T012 → T013) |

## Fase 1, Preparação

| ID   | Descrição                                                                                                                                                                                                                                                                                                                                        | Dependências | Paralelismo | Arquivo alvo                                       | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ----------- | -------------------------------------------------- | ----------- | ------ |
| T001 | Criar `spike/001-flexoes/` com `pyproject.toml` (PyGlossary pinado em `==5.4.1`) e `uv.lock`; validar com `uv sync` e `uv run python -c "import pyglossary"` (D-01, D-06)                                                                                                                                                                        | -            | `[//]`      | `spike/001-flexoes/pyproject.toml`                 | 🟡          | `[X]`  |
| T002 | Selecionar as 20 palavras do roteiro por query SQL no banco (10 nominais de `flexions`, 10 verbais de `conjugations`, ≥ 2 formas com diacríticos, ≥ 2 gravadas em minúsculas para o teste de capitalização) e gravar `roteiro.md` com as colunas forma → lema esperado → resultado → latência, mais a query registrada em apêndice (D-08, RF-02) | -            | `[//]`      | `_reversa_forward/001-spike-de-flexoes/roteiro.md` | 🟢          | `[X]`  |

## Fase 2, Testes

Omitida: a feature é categoria Snippet/Script (roadmap §2, Princípio nº 4 do mantenedor) — sem suíte formal de testes. O teste de fumaça do gerador é a ação T007 (piloto), na fase Núcleo.

## Fase 3, Núcleo

| ID   | Descrição                                                                                                                                                                                                                                                                                                    | Dependências | Paralelismo | Arquivo alvo                       | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ----------- | ---------------------------------- | ----------- | ------ |
| T003 | Implementar em `gerar_spike.py` a camada de leitura: conexão somente-leitura (`file:...?mode=ro`, RN-02), headwords fundidos por lema (ordem `homonym`, depois `sort_key`) e iteração dos pares de `flexions` e `conjugations` com falha barulhenta para forma vazia/só espaços identificando o `id` (EC-04) | T001         | -           | `spike/001-flexoes/gerar_spike.py` | 🟢          | `[X]`  |
| T004 | Implementar o mapeamento do `.syn`: descartes classificados (`orfa`, `duplicada`, `identica` — comparação exata sensível a diacríticos), ambíguas preservadas em N headwords, contadores e gravação de `relatorio-cobertura.json` com a invariante entrada = gravadas + descartes e órfãs nominais (D-04)    | T003         | -           | `spike/001-flexoes/gerar_spike.py` | 🟢          | `[X]`  |
| T005 | Implementar a composição do corpo: HTML trivial de uma linha para todos os lemas; verbete completo (definições, exemplos, locuções, notas, regência) apenas para os 20 lemas do roteiro (D-03, RF-01)                                                                                                        | T003, T002   | -           | `spike/001-flexoes/gerar_spike.py` | 🟢          | `[X]`  |
| T006 | Implementar a escrita StarDict via PyGlossary: formas do mapeamento como chaves alternativas (`l_word`) das entradas, `sametypesequence=h`, dictzip, metadados do `.ifo` (`bookname`, `date`, contagens), geração em diretório temporário com move atômico para `dist/` (D-02, D-05)                         | T004, T005   | -           | `spike/001-flexoes/gerar_spike.py` | 🟡          | `[X]`  |
| T007 | Implementar o modo `--piloto` (~10 verbetes + suas formas) e executá-lo: confirmar que o artefato-piloto tem `.syn` materializado, `synwordcount > 0` coerente no `.ifo` e abre em ferramenta StarDict local — valida a premissa 1 do roadmap (L-05) antes da escala                                         | T006         | -           | `spike/001-flexoes/gerar_spike.py` | 🟡          | `[ ]`  |

## Fase 4, Integração

| ID   | Descrição                                                                                                                                                                                                                                                                                                            | Dependências | Paralelismo | Arquivo alvo                                       | Confidência | Status |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------- | -------------------------------------------------- | ----------- | ------ |
| T008 | Executar a geração em escala real sob `/usr/bin/time -l`, salvando `medicao-geracao.txt` (pico de RSS e duração, RF-07/D-07); conferir `wordcount=137784`, `synwordcount ≥ 900000` e invariante do `relatorio-cobertura.json` com órfãs ≈ 22 lemas                                                                   | T007         | -           | `spike/001-flexoes/dist/`                          | 🟢          | `[X]`  |
| T009 | Instalar o artefato no Boox Air 4C: cópia USB/MTP para `koreader/data/dict/aurelio-spike/`, confirmar detecção em Configurações → Dicionário e reiniciar o KOReader para sessão fria (D-09; executada pelo mantenedor com o roteiro do `onboarding.md` §3)                                                           | T008         | -           | dispositivo (fora do repo)                         | 🟡          | `[X]`  |
| T010 | Executar o roteiro das 20 palavras no dispositivo: latência por cronômetro, remedição por vídeo na faixa 0,8–1,2 s, registro por palavra (verbete aberto + latência) no `roteiro.md`, incluindo o comportamento das 2 capitalizadas e 2 com diacríticos (RF-03/RF-05; executada pelo mantenedor, `onboarding.md` §4) | T009         | -           | `_reversa_forward/001-spike-de-flexoes/roteiro.md` | 🟢          | `[X]`  |

## Fase 5, Polimento

| ID   | Descrição                                                                                                                                                                                                                                                                                        | Dependências | Paralelismo | Arquivo alvo                                            | Confidência | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ | ----------- | ------------------------------------------------------- | ----------- | ------ |
| T011 | Escrever `README.md` do spike: o que é, como rodar (piloto e escala), como reproduzir após regenerar o banco, e a flag de corte de cobertura usada pelo 1º fallback de RN-05 (RN-04)                                                                                                             | T006         | `[//]`      | `spike/001-flexoes/README.md`                           | 🟢          | `[X]`  |
| T012 | Redigir `spike-report.md`: dados brutos das 20 palavras, mediana e máximo, veredito GO/NO-GO aplicando RN-05 mecanicamente, respostas explícitas às 4 OQs (OQ-01/OQ-02 de `indice-de-flexoes`; OQ-01 memória e OQ-02 HTML de `conversao-formato`) e observações oportunistas (RF-06/RF-07/RF-08) | T010, T008   | -           | `_reversa_forward/001-spike-de-flexoes/spike-report.md` | 🟢          | `[X]`  |
| T013 | Aplicar o desfecho do veredito: em GO, registrar no `spike-report.md` o destrave do build completo; em NO-GO, acionar o 1º fallback de RN-05 (regenerar com corte de cobertura do `.syn`, reinstalar, repetir o roteiro) e registrar a 2ª rodada no relatório (D-10)                             | T012         | -           | `_reversa_forward/001-spike-de-flexoes/spike-report.md` | 🟢          | `[X]`  |

## Notas de execução

- T009 e T010 exigem o dispositivo físico nas mãos do mantenedor: o agente prepara, guia e registra; o toque e o cronômetro são humanos. O `/reversa-coding` deve pausar nesses pontos e retomar com os dados coletados.
- T013 é sempre executável (os dois desfechos têm ação definida); não deixar checkbox aberto por veredito GO.
- **[2026-07-03, T008] Desvio documentado no critério de RF-01:** `synwordcount=774.003` < 900.000. O limiar era estimativa; o banco tem ~220 mil pares (forma, lema) repetidos legítimos (mesma forma superficial em pessoas/tempos distintos, ex.: "eu cantava"/"ele cantava") que a deduplicação de D-04 remove por design. Verificado contra o banco: pares únicos brutos = 785.585 (610.584 conj + 175.001 flex); 774.003 gravadas = 100% das formas válidas após descartes auditados (748 formas de 22 lemas órfãos + 50.428 idênticas + dedup). A escala do índice segue real; o veredito do spike não é afetado. Números completos em `dist/aurelio-spike/relatorio-cobertura.json`.
- **[2026-07-03, T003–T007] RB-14 aplicado:** split de `,` e `" ou "` em `flexions.flexion` (achado da extração reversa da mesma data) — 176.623 formas após split contra 175.259 linhas.
- **[2026-07-03, T001] Ajustes de ambiente:** `requires-python >=3.12` (exigência do PyGlossary 5.4.1) e dependência extra `python-idzip==0.3.9` (sem ela o writer emite `.dict` sem compressão, violando o contrato `.dict.dz`).
- **[2026-07-03, T009/T010] Medição no dispositivo DISPENSADA por decisão do usuário** ("vou pressupor que funcione no boox"). As duas ações foram fechadas sem execução física; o veredito registrado no `spike-report.md` é **GO presumido**, com condição de monitoramento nas primeiras leituras reais e a escada de fallbacks de RN-05 preservada. As colunas de resultado do `roteiro.md` ficam vazias por esse motivo.
- **[2026-07-03, preparação desktop] Roteiro validado no KOReader do macOS** (sdcv embutido do app, artefato instalado em `~/Library/Application Support/koreader/data/dict/aurelio-spike/`): 20/20 formas resolvem ao(s) lema(s) esperado(s); ambíguas listam os múltiplos destinos; **modo exato não normaliza caixa nem diacríticos** ("Árvores"/"Disse"/"cantavamos" → nada; o fuzzy resgata "Árvores"→árvore, "Disse"→dizer). Mediana de 16 ms no Mac — **informativa apenas**: pela decisão do requirements §9, o desktop não substitui o Boox; T009/T010 e o veredito de RN-05 permanecem pendentes do dispositivo.

## Histórico de alterações

| Data       | Alteração                                  | Autor   |
| ---------- | ------------------------------------------ | ------- |
| 2026-07-03 | Versão inicial gerada por `/reversa-to-do` | reversa |
