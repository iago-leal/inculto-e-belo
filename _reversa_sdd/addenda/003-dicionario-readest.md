# Adendo da feature 003-dicionario-readest

> Feature: `003-dicionario-readest`
> Data: 2026-10-15
> Cenário: legado
> Gerado por `/reversa-sync` (modo autônomo)

## Vigência

Vigente desde 2026-10-15.
Superado pela re-extração de 2026-10-15.

## Resumo da entrega

A feature entrega uma segunda versão do dicionário do Aurélio, destinada ao leitor Readest e gerada pelo mesmo pipeline que produz a do KOReader. O Readest mostra um único resultado por consulta, ao passo que o KOReader mostra todos os verbetes correspondentes. Por isso a versão nova reúne numa só página todos os artigos de cada palavra: homônimos, homógrafos e os lemas de que ela é forma flexionada. Assim, «foi» abre «ir» e «ser», e «cantávamos» abre só «cantar». A versão do KOReader continua sendo o alvo padrão e não muda em conteúdo nem em contagens. O artefato do Readest só é entregue depois de aprovado em duas etapas: a validação independente em Python e a conferência com o código de busca do próprio Readest.

Foram concluídas as 23 ações do `actions.md`. A última, a importação no Readest do Mac (T021), foi feita pelo usuário e verificada no disco: os arquivos importados têm hash idêntico ao do artefato aprovado, e o dicionário está habilitado e sincronizado na conta.

**Nota de leitura:** esta extração antecede o coding das features 001 e 002. Os componentes P-01 a P-04, que `architecture.md` ainda lista como planejados, existem em `pipeline/` desde a feature 002. Ela não tem adendo, e seu delta está em `_reversa_forward/002-build-completo-de-producao/legacy-impact.md`.

## Impacto por artefato da extração

| Artefato | Seção | Tipo de impacto | Delta |
|----------|-------|-----------------|-------|
| `_reversa_sdd/architecture.md#2-componentes` | Componente novo `agrupamento-readest` | componente-novo | Leia como componente de domínio puro (`dominio/agrupamento_readest.py`). Para cada palavra, ele decide a página com todos os artigos correspondentes, a ordem desses artigos e o descarte das formas sem letra. |
| `_reversa_sdd/architecture.md#2-componentes` | P-03 `conversao-formato` | componente-novo | O componente ganhou um segundo adaptador, `infra/escrita_readest.py`: um escritor StarDict próprio, sem PyGlossary, que grava os índices na ordem do Readest e páginas compostas com trechos compartilhados. |
| `_reversa_sdd/architecture.md#2-componentes` | P-04 `validacao-paridade` | componente-novo | O componente ganhou `validacao/paridade_readest.py`. Ele recalcula as páginas sem importar o agrupamento e simula a busca do Readest para todas as chaves, com tolerância zero. |
| `_reversa_sdd/architecture.md#2-componentes` | Componente novo `conferencia-readest` | delta-de-contrato-externo | Esta é a primeira dependência de Node.js e de rede do projeto, e funciona como segunda etapa obrigatória do gate do Readest. O componente obtém o código de busca do Readest pelo commit fixado da `v0.12.16`, confere o SHA-256, instala o `fflate` 0.8.3 por `npm ci` e executa `conferir.ts`. Com o cache local íntegro, a rede é dispensada. |
| `_reversa_sdd/architecture.md#3-fluxo-de-dependências-alvo` | Fluxo do pipeline | regra-alterada | Ingestão, índice de flexões e renderização passaram a alimentar dois consumidores numa única execução. O KOReader é o alvo padrão e não mudou. O Readest acrescenta agrupamento, escrita, validação e conferência, e o artefato só é promovido se for aprovado; quando reprovado, vai para `dist/readest.reprovado/`. A CLI ganhou `--alvo {koreader,readest,ambos}`. |
| `_reversa_sdd/architecture.md#4-decisões-arquiteturais-em-vigor` | ADR-0004 (PyGlossary 5.4.1 pinado) | regra-alterada | O pino do PyGlossary vale só para o alvo KOReader. O alvo Readest não usa o PyGlossary, porque ele não grava os índices na ordem que o Readest exige. |
| `_reversa_sdd/architecture.md#5-integrações-externas` | Integrações de saída e de entrada | delta-de-contrato-externo | Há duas integrações novas. Na saída, o Readest do Mac recebe o artefato StarDict importado pela tela de dicionários e o sincroniza na nuvem privada da conta. Na entrada, o GitHub e o registro npm são consultados na primeira obtenção da conferência. |
| `_reversa_sdd/domain.md#3-regras-de-negócio` | RB-02 | regra-alterada | A fusão continua no consumidor, e o banco mantém os homônimos em linhas próprias. Na página do Readest, porém, a fusão passou a unir também homógrafos entre lemas e formas. |
| `_reversa_sdd/domain.md#3-regras-de-negócio` | RB-11 | regra-alterada | O artefato do Readest segue de uso estritamente pessoal e nunca é publicado. Guardá-lo na nuvem privada do Readest, vinculada à conta do usuário, não constitui publicação (RN-08 da 003). |
| `_reversa_sdd/domain.md#3-regras-de-negócio` | RB-12 | regra-alterada | O determinismo estende-se ao `.ifo` do Readest, que leva a data do manifesto e a impressão digital do conteúdo, e cada execução grava três relatórios JSON. Duas gerações sobre o mesmo banco produziram bytes idênticos. |
| `_reversa_sdd/domain.md#3-regras-de-negócio` | RB-10 | delta-de-dados | O banco segue somente-leitura. A coluna `entries.most_used` passou a ser requerida e é só lida, para ordenar os artigos não coincidentes nas páginas combinadas. |
| `_reversa_sdd/domain.md#3-regras-de-negócio` | RB-13 (`governanca-operacional`, C-02) | regra-nova | O `pipeline/README.md` ganhou a seção do Readest, que mantém o processo retomável. A seção cobre pré-requisitos, geração, números esperados, importação, atualização da versão fixada e erros novos. O `.gitignore` passou a excluir o cache do código do Readest e o `node_modules/`. |
| `_reversa_sdd/domain.md#4-invariantes-quantitativas-baseline-2026-07-03` | Baseline sobre o banco de 2026-07-03 | delta-de-dados | Os números do alvo Readest se somam aos do KOReader: 887.546 chaves pesquisáveis, 160.302 entradas no `.idx`, 727.244 no `.syn`, 22.913 páginas combinadas, 16.910 sequências distintas e 261 formas sem letra descartadas. |

## Regras sob vigilância

W001, W002, W003, W004, W005 e W006, em `_reversa_forward/003-dicionario-readest/regression-watch.md`.

## Fontes

- `_reversa_forward/003-dicionario-readest/legacy-impact.md`
- `_reversa_forward/003-dicionario-readest/regression-watch.md`
- `_reversa_forward/003-dicionario-readest/requirements.md`
- `_reversa_forward/003-dicionario-readest/progress.jsonl`
- `_reversa_forward/003-dicionario-readest/actions.md`
- `_reversa_sdd/architecture.md`
- `_reversa_sdd/domain.md`
