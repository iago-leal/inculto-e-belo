# Spike 001 — validação do lookup de flexões no KOReader

Código **descartável, mas reprodutível** (RN-04 da feature `001-spike-de-flexoes`): gera um
dicionário StarDict com índices em escala real (137.784 headwords; `.syn` com 774.003
formas) e corpo trivial — verbete completo apenas para os 20 lemas do roteiro de medição.
O objetivo não é o artefato: é o **veredito GO/NO-GO** sobre a latência do lookup no
Boox Air 4C (critério pré-registrado em RN-05).

Documentos da feature: `_reversa_forward/001-spike-de-flexoes/` (requirements, roadmap,
roteiro, onboarding, spike-report).

## Como rodar

Pré-requisitos: `uv` instalado; `aurelio_normalized.db` na raiz do repositório
(restauração: `rclone copy gdrive:inculto-e-belo/aurelio_normalized.db .`).

```sh
cd spike/001-flexoes
uv sync                              # PyGlossary 5.4.1 + python-idzip 0.3.9, pinados no uv.lock

uv run python gerar_spike.py --piloto    # ~2 s: valida a mecânica do .syn (22 verbetes)
/usr/bin/time -l uv run python gerar_spike.py 2> medicao-geracao.txt   # escala real (~5 s)
```

Saída em `dist/aurelio-spike/`: `.ifo`, `.idx`, `.dict.dz`, `.syn` e
`relatorio-cobertura.json` (invariante: entrada = gravadas + órfãs + duplicadas + idênticas).

Instalação no dispositivo e execução do roteiro: `_reversa_forward/001-spike-de-flexoes/onboarding.md` §3–§5.

## Fallback 1 de RN-05 (só em veredito NO-GO)

Reduz a cobertura do `.syn` cortando as conjugações (o grosso do volume), mantendo flexões nominais:

```sh
uv run python gerar_spike.py --cobertura flexions-somente
```

Reinstale e repita o roteiro; registre a 2ª rodada no `spike-report.md`.

## Regras que este código obedece

- Banco **somente-leitura** (URI `mode=ro`) — RN-02; órfãs são contadas e listadas, nunca corrigidas.
- Forma vazia/só espaços → aborta com o id do registro (EC-04). Zero ocorrências no banco atual.
- `flexions.flexion` com múltiplas formas (`,` ou `" ou "`) é dividida — RB-14 da extração reversa.
- Escrita atômica: gera em diretório temporário e move para `dist/` ao final.
- O artefato herda a restrição de uso pessoal (RN-03): **não distribuir**.

## Reproduzir após regenerar o banco

O resultado depende só do `.db`: regenerado o banco, `uv sync && uv run python gerar_spike.py`
reproduz o artefato (ordenação delegada ao PyGlossary; duas execuções sobre o mesmo banco
produzem os mesmos índices). Confira o `relatorio-cobertura.json` contra a baseline em
`_reversa_sdd/domain.md` §4.
