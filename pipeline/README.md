# pipeline — build dos dicionários StarDict do Aurélio (KOReader e Readest)

Converte o `aurelio_normalized.db` (raiz do repo) num dicionário StarDict
completo para o KOReader: **137.784 verbetes integrais** (definições, exemplos,
locuções, notas e regência) mais **774.003 formas flexionadas** no índice
`.syn` (tocar em "cantávamos" abre "cantar"). Todo build passa por validação de
paridade independente antes de valer: exit code 0 é a única evidência necessária
de que o artefato está íntegro.

Com `--alvo readest` (ou `ambos`), o mesmo banco gera uma segunda versão, própria
para o **Readest**, em que cada palavra abre uma única página com todos os
verbetes a que corresponde (seção [Versão do Readest](#versão-do-readest)).

> Conteúdo sob direitos autorais do Aurélio — **uso estritamente pessoal, jamais
> publicar o artefato** (nem commitar: `dist/` está no `.gitignore`).

## Reprodução do zero

Pré-requisitos: [uv](https://docs.astral.sh/uv/) (`brew install uv`) e o banco
restaurado na raiz do repo:

```zsh
cd ~/dev/inculto-e-belo
rclone copy gdrive:inculto-e-belo/aurelio_normalized.db .   # se o .db não existir
cd pipeline
uv sync          # instala PyGlossary 5.4.1 + python-idzip 0.3.9 (pinados no uv.lock)
uv run pytest    # 145 testes, < 5 s (2 de integração pulados sem Node ou sem o cache da conferência)
uv run aurelio-pipeline
```

O comando único encadeia: smoke tests do banco → índice de flexões →
renderização + escrita StarDict → validação de paridade. Saída em
`../dist/aurelio-stardict/` com os 4 arquivos do formato mais
`relatorio-cobertura.json` e `parity-report.json`.

**Números esperados** (banco de 2026-07-03): `wordcount=137784`,
`synwordcount=774003`, 22 lemas órfãos (748 formas) reportados, veredito
`aprovado`, ~12 s de build, ~0,6 GB de pico, ~29 MB de artefato.

**Exit codes:** `0` aprovado · `2` erro nomeado (banco/manifesto/geração) ·
`3` paridade reprovada — **não instale um artefato reprovado**.

## Instalar no KOReader

- **macOS:** `cp -R ../dist/aurelio-stardict "$HOME/Library/Application Support/koreader/data/dict/"`
- **Boox / e-ink:** copiar `dist/aurelio-stardict/` por USB/MTP para `koreader/data/dict/`.

Remova o dicionário antigo (`aurelio-spike/`, se ainda existir) para evitar
resultados duplicados, e reinicie o KOReader. Nas primeiras leituras no e-ink,
observe a latência do toque (condição de monitoramento do spike 001): se o
típico passar de 1 s, gere o artefato reduzido e reinstale:

```zsh
uv run aurelio-pipeline --cobertura flexions-somente   # corta as 869k conjugações do .syn
```

## Versão do Readest

O Readest lê o mesmo formato, mas mostra **um único** verbete por consulta e
compara as palavras em minúsculas. Por isso a versão do KOReader perde sentidos
no Readest («foi» abriria só «ir» ou só «ser») e deixa quatro entradas
inalcançáveis («à», «à clef», «à clé», «Å»). A versão do Readest resolve as duas
coisas: cada palavra abre uma página com todos os verbetes correspondentes, na
ordem «lema da própria palavra → vocabulário frequente → ordem alfabética»,
separados por um traço horizontal; uma forma de um só lema abre só o verbete
dele («vieram» → vir, mesmo que «vir» abra vir e ver).

> **Não instale a versão do Readest no KOReader**, nem a do KOReader no Readest.

### Pré-requisitos (além dos da versão do KOReader)

| O quê | Como conferir | Se faltar |
|-------|---------------|-----------|
| Node.js 22.18 ou posterior, com npm | `node --version` e `npm --version` | `brew install node` |
| Rede, só na primeira vez | baixa dois arquivos do código de busca do Readest (GitHub) e o `fflate` (npm) | depois disso o cache em `conferencia_readest/` dispensa a rede |
| Readest 0.12.12 ou posterior no Mac | Readest → Sobre | atualizar o aplicativo; ver "Atualizar a versão fixada do Readest" |

### Gerar

```zsh
uv run aurelio-pipeline --alvo readest   # só o Readest
uv run aurelio-pipeline --alvo ambos     # KOReader e Readest numa execução
echo $?
```

Sem `--alvo`, o comando gera só a versão do KOReader, como antes; o `[regen]` do
Harness, que roda a cada encerramento de sessão, continua só com ela.

O alvo Readest encadeia: verificação do ambiente da conferência (antes de gastar o
build) → smoke tests → índice de flexões → renderização em memória → agrupamento
por palavra → escrita num diretório de preparo em `../dist/` → **validação
independente** em Python → **conferência com o código de busca do próprio
Readest** (versão fixada, executada no Node) → promoção. Só quando as duas
etapas aprovam o preparo vira `../dist/readest/`:

```
dist/readest/
├── aurelio-readest/        os quatro arquivos importáveis (.ifo, .idx, .syn, .dict.dz)
└── relatorios/             relatorio-agrupamento.json, validacao-readest.json, conferencia-readest.json
```

Reprovado, o artefato vai para `../dist/readest.reprovado/` (com os relatórios e a
expectativa da conferência, para diagnóstico) e a versão aprovada anterior em
`dist/readest/` fica intacta. Exit codes: `0` aprovado e promovido · `2` erro
nomeado (inclusive `AmbienteConferenciaError`) · `3` reprovado.

**Números esperados** (banco de 2026-07-03), no log `agrupamento_ok` e `alvo_fim alvo=readest`:
`chaves=887546`, `paginas_combinadas=22913`, `sequencias_distintas=16910`,
`descartes_sem_letra=261`, `idx=160302`, `syn=727244`, `validacao=aprovado`,
`conferencia=aprovado`, `conteudo=d4bc5db7f94992ba`. Cerca de 70 s com
`--alvo ambos` (a conferência leva uns 45 s), pico de 1,4 GB, artefato de cerca
de 30 MB. Duas gerações sobre o mesmo banco produzem os mesmos bytes.

### Importar no Readest do Mac

Rótulos da interface em português do Readest 0.12.12:

1. Entre na sua conta do Readest e, nas configurações, em **Sincronização de
   Dados**, deixe ativada a categoria **Dicionários** («pacotes de dicionários
   importados e configurações»): é ela que leva o dicionário à nuvem privada da
   sua conta e daí aos outros aparelhos. Guardar o pacote nessa nuvem privada não
   é publicação; o artefato continua de uso estritamente pessoal.
2. Em **Configurações → Idioma → Dicionários**, use **Importar dicionário** e
   selecione **os quatro arquivos juntos** de `dist/readest/aurelio-readest/`.
3. Confira que **Aurélio (uso pessoal, Readest)** aparece e está ativado.
4. Num livro em português, consulte:

| Palavra | Esperado |
|---------|----------|
| era | era, depois ser, depois erar |
| foi | ir, depois ser |
| fosse | ir, ser, fossar |
| vieram | só vir |
| cantávamos | só cantar (o título mostra «cantar») |
| à | o verbete «à», e não o de «a» |

Cada verbete começa com o lema em negrito, e um traço horizontal separa um do
outro; confira também no tema escuro.

### Atualizar depois de mudanças no banco ou no código

O `.ifo` carrega a impressão digital do conteúdo (`Versão do conteúdo …` na
descrição), e o Readest identifica o dicionário por ele. Se o conteúdo mudou, o
Readest trata o pacote como dicionário novo: exclua o anterior (**Excluir
dicionário**) e importe o novo. Reimportar o mesmo conteúdo só substitui o
registro existente.

### Atualizar a versão fixada do Readest

A conferência roda o código de busca do Readest da tag fixada em
`conferencia_readest/fonte-readest.json` (`v0.12.16`; o código de busca é idêntico
desde a 0.12.12). Ao atualizar o Readest no Mac para uma versão que mude a busca:

1. Atualize `tag`, `commit` e os SHA-256 de `arquivos` em `fonte-readest.json`
   (hashes dos arquivos brutos em `raw.githubusercontent.com/readest/readest/<commit>/apps/readest-app/src/services/dictionaries/`).
2. Confira as `reescritas`: o Node executa TypeScript só com sintaxe apagável, então
   o especificador `'./dictZip'` ganha `.ts` e as propriedades de parâmetro de
   construtor do `dictZip.ts` viram campos. Se o código mudou, a preparação do cache
   para com «encontrou 0 ocorrência(s)»: ajuste as reescritas e recalcule
   `arquivos_reescritos`.
3. Se a versão do `fflate` travada pelo Readest mudou, atualize `package.json` e
   rode `npm install --package-lock-only` em `conferencia_readest/`.
4. Apague `conferencia_readest/.cache/` e `conferencia_readest/node_modules/` e
   regenere com `--alvo readest`.

O código do Readest (AGPL-3.0) fica só no cache local, fora do git.

### Limitações conhecidas

- Peculiaridades do banco aparecem nas páginas: o banco registra «a» como forma de
  «bretão», e a página de «a» mostra «bretão» (o KOReader faz o mesmo).
- As 261 formas sem nenhuma letra («/» de verbos defectivos) ficam fora da versão
  do Readest; consultá-las não dá resultado (lista nominal em `relatorio-agrupamento.json`).
- Uma forma de um só lema cuja página do lema é simples abre com o título do lema
  («cantávamos» → título «cantar»); as demais abrem com o título da própria palavra.

## Quando o banco mudar (atualização deliberada)

Os smoke tests comparam as contagens do banco com `manifesto-integridade.json`.
Após regenerar o banco, o build falha com `ContagemDivergenteError` — é o
comportamento desejado. Para aceitar o banco novo:

1. Confira que a mudança era esperada (proveniência no README da raiz).
2. Atualize as contagens: `sqlite3 ../aurelio_normalized.db "SELECT COUNT(*) FROM <tabela>"` para cada tabela do manifesto.
3. Commite o `manifesto-integridade.json` novo **em commit próprio** (mudança explícita e auditável).
4. Rode o build; os números de `wordcount`/`synwordcount` esperados também mudam.

## Arquitetura (para o eu de daqui a 12 meses)

```
src/aurelio_pipeline/
├── cli.py                         orquestração, --alvo + exit codes
├── erros.py                       erros nomeados (falha barulhenta é contrato)
├── infra/repositorio.py           ÚNICO dono do SQL; banco somente-leitura (mode=ro)
├── dominio/indice_flexoes.py      forma→headword, puro (split RB-14, descartes auditados)
├── dominio/renderizacao.py        Verbete→HTML integral, puro
├── dominio/agrupamento_readest.py palavra→página do Readest (artigos, ordem, índice), puro
├── infra/escrita_stardict.py      adaptador PyGlossary (único acoplamento à lib; KOReader)
├── infra/escrita_readest.py       escritor StarDict próprio do Readest + promoção condicionada
├── infra/conferencia_readest.py   obtenção do código do Readest, cache e subprocesso Node
└── validacao/                     parser StarDict próprio (stdlib) + paridade KOReader e Readest
conferencia_readest/               fonte fixada, lockfile e conferir.ts (cache e node_modules fora do git)
```

Specs completas em `../_reversa_sdd/sdd/`; decisões e medições das features em
`../_reversa_forward/002-build-completo-de-producao/` (KOReader) e
`../_reversa_forward/003-dicionario-readest/` (Readest).

## Troubleshooting

| Sintoma                                | Ação                                                                           |
| -------------------------------------- | ------------------------------------------------------------------------------ |
| `BancoAusenteError`                    | `rclone copy gdrive:inculto-e-belo/aurelio_normalized.db ..`                   |
| `ContagemDivergenteError`              | Seção "Quando o banco mudar" acima                                             |
| `EsquemaInvalidoError`                 | Banco errado/antigo; conferir proveniência no README da raiz                   |
| `FalhaGeracaoError` citando `.dict.dz` | `uv sync` (python-idzip ausente do ambiente)                                   |
| Exit 3 (paridade reprovada)            | Ler `divergencias` no `parity-report.json`; corrigir e regenerar; não instalar |
| Popup vazio no KOReader                | Reiniciar o app (sessão fria) e conferir Configurações → Dicionário            |
| `AmbienteConferenciaError` citando o Node ou o npm | `brew install node` e repetir |
| `AmbienteConferenciaError` citando URL, HTTP ou `npm ci` | Sem rede na primeira obtenção: conectar e repetir; depois o cache basta |
| `AmbienteConferenciaError` citando hash divergente | Não contornar: conferir commit e hashes em `conferencia_readest/fonte-readest.json` |
| Exit 3 no alvo Readest | Ler `divergencias` em `dist/readest.reprovado/relatorios/validacao-readest.json` e `falhas` em `conferencia-readest.json`; a versão aprovada segue em `dist/readest/` |
| Dois «Aurélio» no Readest | Conteúdo novo importado sem excluir o anterior: excluir o mais antigo |
| Palavra sem resultado no Readest | Dicionário desativado em Configurações → Idioma → Dicionários, ou forma sem letra (ver `formas_descartadas`) |
