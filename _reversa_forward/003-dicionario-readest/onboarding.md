# Onboarding: 003-dicionario-readest

> Passo a passo para quem vai gerar e testar a versão do Readest pela primeira vez, inclusive o iago de daqui a 12 meses. Assume macOS com zsh e o pipeline da feature 002 funcionando (`_reversa_forward/002-build-completo-de-producao/onboarding.md`).

## 0. Pré-requisitos

| O quê | Como conferir | Se faltar |
|-------|---------------|-----------|
| uv | `uv --version` | `brew install uv` |
| Banco local | `ls -lh aurelio_normalized.db` (cerca de 189 MB, na raiz do repo) | `rclone copy gdrive:inculto-e-belo/aurelio_normalized.db .` |
| Node.js 22.18 ou posterior, com npm | `node --version` e `npm --version` | `brew install node` |
| Rede (só na primeira vez) | baixa o código de busca do Readest e o `fflate` | depois disso o cache em `pipeline/conferencia_readest/` dispensa a rede |
| Readest 0.12.12 ou posterior no Mac | Readest → Sobre | atualizar o aplicativo; se a versão nova mudar o código de busca, ver o README, seção de atualização da versão fixada |

## 1. Preparar o ambiente e rodar os testes

```zsh
cd ~/dev/inculto-e-belo/pipeline
uv sync
uv run pytest
```

Esperado: tudo verde. O teste de integração com o Readest roda quando há Node; sem ele, aparece como pulado.

## 2. Gerar a versão do Readest

```zsh
uv run aurelio-pipeline --alvo readest
echo $?
```

O comando encadeia: pré-verificação do ambiente → smoke tests do banco → índice de flexões → agrupamento → renderização e escrita no diretório de preparo → validação independente → conferência com o código do Readest → promoção.

Esperado no log (chave=valor), com o banco de 2026-07-03:

- `chaves=887546 paginas_combinadas=22913 descartes_sem_letra=261` no agrupamento;
- `idx=160302 syn=727244` ao fim da escrita;
- veredito `aprovado` na validação e na conferência;
- bloco final do alvo `readest` com totais, duração (abaixo de 4 min no total) e caminho dos relatórios;
- `echo $?` → `0`.

Saída: `dist/readest/aurelio-readest/` com os quatro arquivos e `dist/readest/relatorios/` com os três relatórios.

Para gerar as duas versões numa só execução: `uv run aurelio-pipeline --alvo ambos`. Sem `--alvo`, o comando gera só a do KOReader, como antes.

Medição opcional de recursos na primeira vez: `/usr/bin/time -l uv run aurelio-pipeline --alvo ambos` (pico esperado abaixo de 2 GB).

## 3. Conferir o artefato à mão (2 min)

```zsh
cat ../dist/readest/aurelio-readest/aurelio-readest.ifo
du -sh ../dist/readest/aurelio-readest
python3 -c "import json; r=json.load(open('../dist/readest/relatorios/validacao-readest.json')); print(r['veredito'], r['contagens'])"
```

Esperado: `wordcount=160302`, `synwordcount=727244`, `bookname=Aurélio (uso pessoal, Readest)`, tamanho até 50 MB (cerca de 34 MB), veredito `aprovado`.

## 4. Importar no Readest do Mac

1. Abrir o Readest e ligar a sincronização de dicionários nas configurações de sincronização.
2. Na tela de dicionários, importar e selecionar os quatro arquivos de `dist/readest/aurelio-readest/`.
3. Conferir que «Aurélio (uso pessoal, Readest)» aparece habilitado.
4. Abrir um livro em português e consultar:

| Palavra | Esperado |
|---------|----------|
| era | era, depois ser, depois erar |
| foi | ir, depois ser |
| fosse | ir, ser, fossar |
| vieram | só vir |
| cantávamos | só cantar |
| à | o verbete «à», e não o de «a» |

Cada artigo começa com o lema em negrito, e um traço horizontal separa os artigos. Conferir também no tema escuro.

## 5. Atualizar depois de mudanças no banco ou no código

1. Regenerar com `uv run aurelio-pipeline --alvo readest` até exit code 0.
2. Se o conteúdo mudou, o `.ifo` muda e o Readest trata o pacote como dicionário novo: remover o anterior na tela de dicionários e importar o novo.
3. Se nada mudou, reimportar apenas substitui o registro existente.

## 6. Quando algo falhar

| Sintoma | Causa provável | Ação |
|---------|----------------|------|
| `AmbienteConferenciaError` citando o Node | Node ausente ou antigo | `brew install node` e repetir |
| `AmbienteConferenciaError` citando URL ou status HTTP | Sem rede na primeira obtenção | Conectar e repetir; depois o cache basta |
| `AmbienteConferenciaError` citando hash divergente | Arquivo baixado diferente do fixado | Não contornar; conferir `fonte-readest.json` e o commit |
| Exit code 3 e `dist/readest.reprovado/` | Validação ou conferência reprovou | Ler `divergencias` em `validacao-readest.json` e as falhas em `conferencia-readest.json`; a versão aprovada anterior continua em `dist/readest/` |
| Dois «Aurélio» no Readest | Conteúdo novo importado sem remover o anterior | Remover o mais antigo |
| Palavra sem resultado no Readest | Dicionário desabilitado, ou a palavra é forma sem letra (descartada por RN-06) | Conferir a tela de dicionários; para formas, ver `formas_descartadas` no relatório de agrupamento |
| Os erros já conhecidos do pipeline (`BancoAusenteError`, `ContagemDivergenteError` e outros) | Os mesmos da feature 002 | Ver `_reversa_forward/002-build-completo-de-producao/onboarding.md#7` |
