---
commit: 969fc82da9fea4aad94e513d36ef58451b2c9798
feature: default_feature
start_time: '2026-07-03T21:52:16.436985+00:00'
status: inactive
---

## O que foi feito
- **Feature `002-build-completo-de-producao` concluída de ponta a ponta (19/19 ações), artefato aprovado pela paridade.** Ciclo forward completo numa sessão: `/reversa-requirements` (herdando os achados do spike; a T007 da 001 foi reconciliada — estava `done` no progress.jsonl, faltava a checkbox) → `/reversa-clarify` (4 dúvidas resolvidas: pipeline nasce em `pipeline/` com spike congelado como registro; paridade normaliza whitespace; manifesto só com contagens; substituição sem retenção) → `/reversa-plan` (14 decisões, todas 🟢) → `/reversa-to-do` (19 ações) → `/reversa-coding`.
- **Pipeline de produção em camadas** (`pipeline/`, uv, PyGlossary 5.4.1 + python-idzip 0.3.9 + pytest 8.4.1 + coverage 7.9.1 pinados): `infra/repositorio.py` (único dono do SQL, `mode=ro`, smoke tests contra `manifesto-integridade.json` versionado), `dominio/indice_flexoes.py` e `dominio/renderizacao.py` (puros), `infra/escrita_stardict.py` (adaptador PyGlossary, escrita atômica, verificação do `.dict.dz`), `validacao/` (parser StarDict próprio em stdlib + checks de tolerância zero) e `cli.py` (`uv run aurelio-pipeline`, exit 0/2/3).
- **Build aprovado em escala real:** `wordcount=137784`, `synwordcount=774003`, órfãs 22 lemas/748 formas, invariante 1.045.742 fechada — idênticos ao baseline do spike. 12,2 s, 608 MB de pico, artefato 28,5 MB (limites: 10 min / 2 GB / 250 MB). Verbetes agora **integrais** (definições+rubricas, exemplos editor/citation, locuções, notas, regência Luft), homônimos fundidos.
- **O gate pegou um defeito real na 1ª rodada:** paridade reprovou com 166 divergências porque `texto_de_html` trocava tags por espaço (`"V. <u>sucuri</u>."` → `"sucuri ."`); corrigido para remoção por string vazia (mesma derivação do `content_text`), 2ª rodada aprovada 500/500 + 500/500.
- **Qualidade:** 50 testes, cobertura 96% em domínio+validação+repositório (exigência ≥ 60%); cada erro nomeado da ingestão coberto (aceite de RF-01). Instalado no KOReader do macOS com `aurelio-spike` removido; smoke sdcv 3/3 (`cantávamos`→cantar integral, `belas`→bela+belo+belas, `coração`→3 homônimos numerados).
- **Governança:** `pipeline/README.md` (runbook do zero + fluxo de atualização do manifesto + fallback `--cobertura flexions-somente`), README raiz com seção do pipeline, `.gitignore` cobre `dist/` e `pipeline/.venv/`, e `[regen]` do `harness.toml` **habilitado** com o build (determinístico, ~12 s, paridade embutida).

## Próximos passos
- **Re-extração `/reversa`** para fechar o ciclo: reclassificar P-01..P-04 de 🟡 PLANEJADO para 🟢 CONFIRMADO (agora existem em `pipeline/`) e rodar o step-04 contra os watch items da 001 **e** da 002 (12 no total). Decisão do usuário; não disparar sozinho.
- **Feature de distribuição** (`distribuicao-webdav`, única spec ainda sem código) quando houver interesse: antes, verificar caminho/autenticação do WebDAV no `koreader-notas` (OQ-01 da spec).
- Quando for ler no Boox: copiar `dist/aurelio-stardict/` por USB para `koreader/data/dict/` (removendo `aurelio-spike/` se estiver lá) — cumpre a condição de monitoramento do GO presumido; fallback pronto na CLI.
- Pergunta opcional em `_reversa_sdd/questions.md` (critério de `entries.most_used`) segue aberta, sem urgência.

## Pendências / bloqueios
- Nenhum bloqueio. **Risco residual (herdado do spike):** latência no e-ink segue presumida; a condição de monitoramento transferiu-se ao artefato de produção (O-04 do `regression-watch.md` da 002).
- `[regen]` roda o build a cada encerramento de sessão e pressupõe o `.db` presente — se incomodar, reverter é uma linha no `harness.toml` (O-03).
- O dicionário instalado no KOReader do macOS agora é `aurelio-stardict/` (o do spike foi removido).

## Ponteiros
- Código de produção: `pipeline/` (README com reprodução do zero; arquitetura em camadas mapeada às specs).
- Trilha da execução: `_reversa_forward/002-build-completo-de-producao/` — `actions.md` (19/19, §Notas de execução com os desvios), `progress.jsonl`, `roadmap.md` (14 decisões), `requirements.md` (§9 com as 4 decisões da clarificação).
- Auditoria: `legacy-impact.md` (banco e spike intocados; nenhuma regra 🟢 modificada) e `regression-watch.md` (6 watch items W001–W006 + observações O-01..O-04).
- Artefato: `dist/aurelio-stardict/` (fora do git) com `relatorio-cobertura.json` e `parity-report.json` aprovado.
- Estado Reversa: `.reversa/active-requirements.json` (feature 002 `done`, sem pausadas); extração em `_reversa_sdd/` ainda anterior ao pipeline (motivo da re-extração sugerida).
