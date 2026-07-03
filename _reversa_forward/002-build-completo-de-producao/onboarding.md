# Onboarding — 002-build-completo-de-producao

> Passo a passo executável para quem vai rodar e testar o pipeline pela primeira vez (inclusive o iago de daqui a 12 meses). Assume macOS com zsh.

## 0. Pré-requisitos

| O quê                      | Como conferir                                            | Se faltar                                                   |
| -------------------------- | -------------------------------------------------------- | ----------------------------------------------------------- |
| uv                         | `uv --version`                                           | `brew install uv`                                           |
| Banco local                | `ls -lh aurelio_normalized.db` (~189 MB na raiz do repo) | `rclone copy gdrive:inculto-e-belo/aurelio_normalized.db .` |
| rclone com remote `gdrive` | `rclone listremotes`                                     | Ver README da raiz do repo                                  |

## 1. Preparar o ambiente

```zsh
cd ~/dev/inculto-e-belo/pipeline
uv sync            # instala PyGlossary 5.4.1, python-idzip 0.3.9 e deps de dev do lock file
```

Esperado: término sem erro; `uv run python -c "import pyglossary, idzip"` silencioso.

## 2. Rodar a suíte de testes

```zsh
uv run pytest
```

Esperado: tudo verde em menos de 2 minutos (fixtures em memória, sem tocar o banco real).

## 3. Build completo com validação

```zsh
uv run aurelio-pipeline
```

O comando encadeia: smoke tests do banco → índice de flexões → renderização + escrita StarDict → validação de paridade.

Esperado no log (chave=valor):

- `entries=143376` e `duracao_ms=` nos smoke tests (< 5 s);
- progresso a cada 100.000 pares e 10.000 verbetes;
- `headwords=137784 sinonimos=774003` ao fim da escrita;
- veredito `aprovado` da paridade e exit code 0 (`echo $?` → `0`).

Saída: `dist/aurelio-stardict/` com `.ifo`, `.idx`, `.dict.dz`, `.syn`, `relatorio-cobertura.json` e `parity-report.json`.

Medição opcional de recursos (recomendada no primeiro build): `/usr/bin/time -l uv run aurelio-pipeline` — pico de RSS esperado < 2 GB.

## 4. Conferir o artefato manualmente (2 min)

```zsh
cat dist/aurelio-stardict/*.ifo
python3 -c "import json; r=json.load(open('dist/aurelio-stardict/parity-report.json')); print(r['veredito'], r['contagens'])"
```

Esperado: `wordcount=137784`, `synwordcount=774003`, veredito `aprovado`.

## 5. Instalar no KOReader do macOS (smoke de leitura)

```zsh
cp -R dist/aurelio-stardict "$HOME/Library/Application Support/koreader/data/dict/"
rm -rf "$HOME/Library/Application Support/koreader/data/dict/aurelio-spike"   # remove o dicionário do spike (roadmap §8)
```

Abra o KOReader, confirme o dicionário em Configurações → Dicionário, e teste 3 palavras: `cantávamos` → cantar (verbete completo, com definições numeradas), `belas` → bela + belo (popup lista os dois), `coração` → artigo único com os 3 homônimos.

## 6. Instalar no Boox (quando for ler de verdade)

Copiar `dist/aurelio-stardict/` por USB/MTP para `koreader/data/dict/` do dispositivo, removendo `aurelio-spike/` se estiver lá. Nas primeiras leituras, observar a latência do toque — isso cumpre a condição de monitoramento do GO presumido do spike (`spike-report.md#1`). Se a latência decepcionar (típico ≥ 1 s), o 1º fallback é `uv run aurelio-pipeline --cobertura flexions-somente`.

## 7. Quando algo falhar

| Sintoma                                       | Causa provável                                    | Ação                                                                                                                      |
| --------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `BancoAusenteError`                           | Banco não restaurado                              | Passo 0: `rclone copy`                                                                                                    |
| `ContagemDivergenteError`                     | Banco regenerado/trocado desde o último manifesto | Se a mudança foi deliberada: atualizar `pipeline/manifesto-integridade.json` em commit próprio; senão, investigar o banco |
| `EsquemaInvalidoError`                        | Banco de origem errado ou versão antiga           | Conferir proveniência (README raiz §Proveniência)                                                                         |
| Falha nomeada de dictzip / `.dict` sem `.dz`  | `python-idzip` ausente do ambiente                | `uv sync` de novo; conferir `uv.lock`                                                                                     |
| Paridade reprovada                            | Defeito real de conversão                         | Ler `divergencias` no `parity-report.json`; o artefato NÃO deve ser instalado; corrigir e regenerar                       |
| Popup vazio para forma flexionada no KOReader | Dicionário não recarregado                        | Reiniciar o KOReader (sessão fria) e repetir                                                                              |
