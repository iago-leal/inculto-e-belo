---
commit: 7703eb768367ca08e0e78d481f8a0a11245f0501
feature: default_feature
start_time: '2026-07-03T20:54:38.048137+00:00'
status: inactive
---

## O que foi feito
- **Feature `001-spike-de-flexoes` concluída de ponta a ponta (13/13 ações), veredito GO presumido.** Pipeline completo numa sessão: `/reversa-plan` (roadmap com 10 decisões, investigation, data-delta, onboarding, interface do artefato) → `/reversa-to-do` (13 ações) → `/reversa-coding`.
- **Extração reversa completa via `/reversa-autonomous`** — o gate do coding exigia `architecture.md`+`domain.md` inexistentes (projeto nasceu greenfield). Artefatos em `_reversa_sdd/`: inventário, dicionário de dados das **14 tabelas** (o README listava 8), domain com 14 regras, C4 níveis 1–3, ERD, 5 ADRs retroativos, units `banco-lexical/` e `governanca-operacional/`, confiança ~92%. O Revisor resolveu por amostragem as 4 lacunas do banco: `flexions.type` (1=plural, 2=fem., 3=fem. pl., 4=dim., 5=aum.), `entries.head_type` (palavra/símbolo/afixo/locução), mapa completo dos 13 `conjugations.tense`.
- **Achado RB-14:** `flexions.flexion` traz múltiplas formas por linha (1.349 com `,`, 15 com `" ou "`) — o gerador divide; sem isso ~1.400 entradas do `.syn` nasceriam corrompidas.
- **Spike implementado e gerado** (`spike/001-flexoes/`, uv + PyGlossary 5.4.1 + python-idzip 0.3.9 pinados): 137.784 headwords, `.syn` com **774.003 formas = 100% dos pares válidos** (o limiar de 900 mil de RF-01 era estimativa que ignorava ~220 mil repetições legítimas entre pessoas verbais — desvio documentado), 4,9 s de geração, 462 MB de pico, órfãs = 22 lemas exatos, invariante fechada.
- **Validação no KOReader do macOS** (sdcv embutido do app): 20/20 formas do roteiro resolvem ao(s) lema(s) esperado(s), ambíguas listam múltiplos destinos, mediana 16 ms (informativa). OQ-02 respondida: o lookup exato **não normaliza** caixa/diacríticos; o fallback fuzzy resgata ("Árvores"→árvore).
- **Decisão do usuário:** medição no Boox dispensada ("vou pressupor que funcione") — T009/T010 fechadas como skipped, veredito **GO presumido** com condição de monitoramento nas primeiras leituras reais e escada de fallbacks de RN-05 preservada. `spike-report.md` redigido com as 4 OQs respondidas.
- Pendências de governança executadas: README atualizado para as 14 tabelas; `.gitignore` cobre `spike/*/dist|.venv|medições`. Commit `7703eb7` (56 arquivos) pushed para `origin/main`.

## Próximos passos
- **Abrir a feature do build completo** com `/reversa-requirements`: pipeline de produção (`ingestao-aurelio` → `indice-de-flexoes` → `conversao-formato` → `validacao-paridade`), herdando os achados do spike (baseline 774.003, RB-14, python-idzip pinado, homonym-merge validado).
- Quando for ler no Boox: copiar `spike/001-flexoes/dist/aurelio-spike/` por USB para `koreader/data/dict/` — cumpre a condição de monitoramento do veredito. Se latência decepcionar, 1º fallback pronto: `uv run python gerar_spike.py --cobertura flexions-somente`.
- Verificar caminho/autenticação do WebDAV no `koreader-notas` (OQ-01 da spec `distribuicao-webdav`) — só quando o build chegar à distribuição.
- Pergunta opcional em `_reversa_sdd/questions.md` (critério de `entries.most_used`) — responder só se houver interesse gramatical.

## Pendências / bloqueios
- Nenhum bloqueio. **Risco residual assumido:** latência no e-ink não foi medida (decisão do usuário, registrada no decision log do `spike-report.md`); mitigação = monitoramento nas primeiras leituras + fallbacks de RN-05 na ordem fixa.
- Artefato do spike instalado também no KOReader do macOS (`~/Library/Application Support/koreader/data/dict/aurelio-spike/`) — lembrar de remover se um dia incomodar.
- Na próxima re-extração `/reversa`, o step-04 verificará os 6 watch items de `regression-watch.md` (baseline do banco, RB-14, órfãs=22, mode=ro, uso pessoal, mapa dos tempos).

## Ponteiros
- Veredito e OQs: `_reversa_forward/001-spike-de-flexoes/spike-report.md` (GO presumido; decision log na §6).
- Trilha da execução: `actions.md` (§Notas de execução tem os 3 desvios documentados) e `progress.jsonl` da feature.
- Auditoria: `legacy-impact.md` e `regression-watch.md` (6 watch items + observações O-01..O-03).
- Código do spike: `spike/001-flexoes/` (README com reprodução e fallback; `dist/` fora do git).
- Extração: `_reversa_sdd/` (confidence-report ~92%; `data-dictionary.md` com os enums resolvidos; `domain.md` §6 com RB-14).
- Estado Reversa: `.reversa/state.json` (5 fases concluídas), `.reversa/active-requirements.json` (feature `done`).
