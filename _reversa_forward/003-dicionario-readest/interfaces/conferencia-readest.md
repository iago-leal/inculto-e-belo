# Interface: obtenção e execução do código de busca do Readest

> Contrato da etapa obrigatória do gate do alvo Readest (RF-06). Tipos: HTTP (saída, só na primeira obtenção) e subprocesso local.
> Produtor do pedido: `infra/conferencia_readest.py`. Serviços externos: GitHub (arquivos brutos) e registro npm. Executor: Node.js local.

## 1. Fonte fixada (versionada em `pipeline/conferencia_readest/fonte-readest.json`)

| Campo | Valor |
|-------|-------|
| `repositorio` | `readest/readest` |
| `tag` | `v0.12.16` |
| `commit` | `3cc39ad7a558e6612e1a8135058fbd6f3c90b3e3` |
| `base` | `apps/readest-app/src/services/dictionaries/` |
| `arquivos` | `stardictReader.ts` (`affa164d…fd1418`), `dictZip.ts` (`2e8f5448…7e691b33`); hashes integrais em `investigation.md#1` |
| `fflate` | `0.8.3` (lockfile da tag) |
| `node_minimo` | `22.18` |

## 2. Obtenção por HTTP

| Item | Contrato |
|------|----------|
| Pedido | `GET https://raw.githubusercontent.com/readest/readest/<commit>/<base><arquivo>`, um por arquivo, com `urllib.request` da stdlib |
| Resposta esperada | `200` com o corpo do arquivo; SHA-256 do corpo igual ao de `fonte-readest.json` |
| Dependências npm | `npm ci` em `pipeline/conferencia_readest/`, com o `package-lock.json` versionado; o npm confere a integridade do pacote |
| Endereçamento | Pelo commit, não pela tag: o conteúdo não muda mesmo que a tag seja movida |
| Idempotência | Download só quando o cache não existe ou falha na conferência de hash; com o cache íntegro, nenhuma chamada de rede |
| Timeout | 30 s por arquivo; `npm ci` com o timeout padrão do npm |
| Reprocessamento | Nenhuma nova tentativa automática: a falha vira erro nomeado e o mantenedor reexecuta |

### Erros

| Situação | Erro | Mensagem acionável |
|----------|------|--------------------|
| Sem rede ou HTTP diferente de 200 na primeira obtenção | `AmbienteConferenciaError` | URL e status; «conecte-se à rede e repita; depois disso o cache dispensa a rede» |
| SHA-256 divergente | `AmbienteConferenciaError` | arquivo, hash esperado e obtido; o cache não é gravado |
| `node` ausente ou abaixo de 22.18 | `AmbienteConferenciaError` | versão encontrada; «instale com `brew install node`» |
| `npm ci` falhou | `AmbienteConferenciaError` | código de saída e as últimas linhas do erro |

Todos saem com exit code 2 e são verificados antes do build (D-14).

## 3. Preparação do cache

1. Baixar os arquivos para `pipeline/conferencia_readest/.cache/v0.12.16/`, conferindo o hash do original.
2. Aplicar as reescritas mecânicas listadas em `fonte-readest.json#reescritas`, cada uma com exatamente uma ocorrência, senão erro nomeado: em `stardictReader.ts`, o especificador `'./dictZip'` vira `'./dictZip.ts'`; em `dictZip.ts`, as duas propriedades de parâmetro de construtor (`private readonly buf`, `private readonly blob` e `private readonly meta`) viram campos declarados com atribuição no início do construtor, com a mesma semântica. A remoção nativa de tipos do Node recusa propriedades de parâmetro, e o Node 26 não oferece mais o modo de transformação.
3. Conferir o SHA-256 de cada arquivo reescrito contra `fonte-readest.json#arquivos_reescritos` e gravar um marcador `.pronto` com os hashes do original e do reescrito; cache sem marcador é refeito.

## 4. Execução por subprocesso

| Item | Contrato |
|------|----------|
| Comando | `node conferir.ts <dir-artefato> <basename> <expectativa.tsv>`, com o diretório da conferência como diretório de trabalho |
| Entrada | Os quatro arquivos do artefato no diretório de preparo e a expectativa `chave<TAB>offset<TAB>tamanho` (uma linha por chave pesquisável) |
| O que o roteiro faz | Carrega o artefato com o `StarDictReader` do Readest; para cada chave, executa `lookup` e, se falhar, `resolveSynonym`, como o provedor do Readest; compara offset e tamanho com a expectativa; lê cada trecho distinto pelo leitor por blocos e compara com a descompressão integral |
| Saída | Um objeto JSON no stdout: versões, contagens, até 50 falhas nominais, duração e veredito |
| Exit code | `0` aprovado; `1` reprovado; outro código = falha de execução |
| Timeout | 10 min; estourado, vira reprovação com a causa registrada |
| Dados | A expectativa contém só chaves e offsets; fica no diretório de preparo, fora do git |

## 5. Mapeamento para o exit code do pipeline

| Resultado | Pipeline |
|-----------|----------|
| Conferência aprovada e validação Python aprovada | promove; exit 0 |
| Qualquer das duas reprovada | `dist/readest.reprovado/`; exit 3 |
| Erro de ambiente ou de execução | não promove; exit 2 |

## 6. Atualização da versão fixada

Ao atualizar o Readest no Mac para uma versão com código de busca diferente, o mantenedor: (1) atualiza tag, commit e hashes em `fonte-readest.json`; (2) atualiza `fflate` no `package.json` e no lockfile, se a tag mudou a versão; (3) apaga o cache; (4) regenera o alvo Readest. O README descreve o passo a passo.
