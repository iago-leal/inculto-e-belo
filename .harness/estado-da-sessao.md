---
commit: adeaeeee668b1016ceef0ef0cefd165a8e230417
feature: default_feature
start_time: '2026-07-03T23:16:00.117332+00:00'
status: inactive
---

## O que foi feito
- **Dicionário de produção instalado no Boox, cumprindo o passo pendente do GO presumido do spike 001.** Os 4 arquivos de `dist/aurelio-stardict/` (build de 2026-07-03, paridade aprovada) foram transferidos para `koreader/data/dict/aurelio-stardict/` no aparelho, com tamanhos verificados byte a byte no destino (288 B / 2,6 MB / 12,3 MB / 13,6 MB). Não havia `aurelio-spike/` no Boox — nada a remover.
- **Caminho de transferência inteiramente via terminal, sem depuração USB.** O Boox (ONYX "LAGOON") apareceu no barramento USB só em modo MTP, invisível ao `adb`; a solução foi a `libmtp` 1.1.23 (instalada via Homebrew): `mtp-newfolder` + `mtp-sendfile` com o **ID numérico** da pasta como destino, porque (a) o parse por caminho (`/koreader/data/dict/...`) falha no utilitário e (b) os IDs de objeto MTP **mudam entre sessões** — é preciso reconferir o ID com `mtp-folders | grep` imediatamente antes de enviar.
- Nenhuma mudança de código nesta sessão; repo intocado fora de `.harness/`.

## Próximos passos
- **Observar a latência do popup no e-ink nas primeiras leituras** (condição de monitoramento O-04 do `regression-watch.md` da 002): se o típico passar de 1 s, gerar `uv run aurelio-pipeline --cobertura flexions-somente` e reinstalar pelo mesmo caminho MTP.
- **Re-extração `/reversa`** para fechar o ciclo: reclassificar P-01..P-04 de 🟡 PLANEJADO para 🟢 CONFIRMADO e rodar o step-04 contra os 12 watch items (001+002). Decisão do usuário; não disparar sozinho.
- **Feature de distribuição** (`distribuicao-webdav`, única spec sem código) quando houver interesse — a rota MTP local desta sessão reduz a urgência dela; antes de codar, verificar caminho/autenticação do WebDAV no `koreader-notas` (OQ-01 da spec).
- Pergunta opcional em `_reversa_sdd/questions.md` (critério de `entries.most_used`) segue aberta, sem urgência.

## Pendências / bloqueios
- Nenhum bloqueio. **Risco residual:** a latência no e-ink continua presumida até a primeira leitura real no Boox (agora dá para medir — o dicionário está instalado).
- `[regen]` roda o build a cada encerramento e pressupõe o `.db` presente (reverter é uma linha no `harness.toml`, O-03).
- Instalações ativas: KOReader do macOS e KOReader do Boox, ambos com `aurelio-stardict/` integral.

## Ponteiros
- **Receita de reinstalação no Boox (MTP):** conectar USB em modo transferência → `mtp-folders | grep -n dict` para achar o ID atual de `koreader/data/dict` → `mtp-newfolder <nome> <id> 65537` (storage fixo 0x00010001) → reconferir o ID novo → `mtp-sendfile <arq> "<id>/<arq>"` por arquivo. IDs não sobrevivem entre sessões; caminho por nome não funciona.
- Código de produção: `pipeline/` (README com runbook, incl. seção "Instalar no KOReader" — a linha do Boox agora tem alternativa MTP além de USB/arrastar).
- Trilha da 002: `_reversa_forward/002-build-completo-de-producao/` (actions 19/19, roadmap, regression-watch com O-01..O-04).
- Artefato: `dist/aurelio-stardict/` (fora do git), `parity-report.json` aprovado.
- Estado Reversa: `.reversa/active-requirements.json` (feature 002 `done`, sem pausadas); extração em `_reversa_sdd/` ainda anterior ao pipeline (motivo da re-extração sugerida).
