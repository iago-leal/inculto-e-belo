# pipeline-koreader

> Gerado pelo reversa-writer em 2026-10-15 (re-extração). Unit da granularity `module`.
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral

É o alvo padrão do pipeline: converte os artigos renderizados e o mapa de formas do `pipeline-nucleo` num dicionário StarDict para o KOReader do Boox e o submete a uma paridade de tolerância zero contra o banco. Foi entregue pela feature 002 e permanece intacto desde então, inclusive quando roda junto com o alvo Readest. 🟢

## Responsabilidades

- Gravar `aurelio-stardict.{ifo,idx,syn,dict.dz}` pelo PyGlossary, único acoplamento do projeto a essa biblioteca. 🟢
- Ler o artefato gerado com um leitor próprio, independente do PyGlossary. 🟢
- Conferir contagens, metadados e duas amostras determinísticas contra o banco e emitir `parity-report.json`. 🟢
- Gravar `relatorio-cobertura.json` ao lado do artefato. 🟢

## Regras de Negócio

- RB-02: um headword por lema; homônimos fundidos no mesmo artigo. 🟢
- RB-05: lemas órfãos não entram no `.syn`; constam do relatório de cobertura. 🟢
- RB-11: `bookname` «Aurélio (uso pessoal)»; o artefato fica em `dist/`, fora do git. 🟢
- RB-12: a regeneração é auditável pelos dois relatórios JSON; a data do `.ifo` é a do build, o único campo que muda entre gerações. 🟢
- RB-17: é o alvo padrão, e o `[regen]` do Harness gera só ele, para que o encerramento de sessão não dependa de Node nem de rede. 🟢
- RB-18: tolerância zero; qualquer divergência de qualquer check reprova o artefato, com exit 3. O artefato reprovado **já está** em `dist/aurelio-stardict/`, porque a troca precede o veredito; a proteção é a mensagem «não instale». 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Gravar um headword por lema, com as formas como chaves alternativas no `.syn` | Must | `.idx` com 137.784 entradas e `.syn` com 774.003 no banco atual 🟢 |
| RF-02 | Dicionário comprimido por dictzip | Must | `.dict.dz` presente; ausência gera `FalhaGeracaoError`, que aponta o python-idzip 🟢 |
| RF-03 | Troca atômica do diretório de saída | Must | Uma falha no meio da escrita deixa o artefato anterior intacto 🟢 |
| RF-04 | Leitor próprio que valida a estrutura binária | Must | NUL ausente, truncamento, UTF-8 inválido, offset além do corpo e índice do `.syn` fora do `.idx` produzem `ArtefatoCorrompidoError` 🟢 |
| RF-05 | Paridade com cinco checks e relatório integral | Must | `parity-report.json` lista cada check com o veredito e todas as divergências 🟢 |
| RF-06 | Amostras determinísticas | Must | Sementes 20260703 (verbetes) e 20260704 (flexões), 500 itens cada 🟢 |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | Build do alvo em cerca de 12 s | Comentário do `[regen]` em `harness.toml` | 🟢 |
| Isolamento | PyGlossary só em `escrita_stardict.py` | `grep` de `pyglossary` no pacote | 🟢 |
| Independência da verificação | O leitor não usa o PyGlossary | `validacao/leitor_stardict.py` usa só `gzip` e `struct` | 🟢 |
| Observabilidade | Progresso a cada 10.000 artigos | `infra/escrita_stardict.py:23` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado o banco de 2026-07-03
Quando o mantenedor executa "uv run aurelio-pipeline"
Então dist/aurelio-stardict/ contém os quatro arquivos, parity-report.json com veredito "aprovado"
E o processo termina com exit 0

Dado um artefato cujo .syn tem uma entrada a menos que as formas gravadas
Quando a paridade roda
Então o check contagem-syn reprova, o relatório registra a diferença e o processo termina com exit 3
E o log diz "ARTEFATO DO KOREADER REPROVADO — não instale"

Dado um ambiente sem python-idzip
Quando a escrita termina sem o .dict.dz
Então FalhaGeracaoError interrompe o build com exit 2
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| RF-01 a RF-05 | Must | Formam o artefato consumido no Boox e o gate que o protege |
| RF-06 | Must | Garante paridade reproduzível entre execuções |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `pipeline/src/aurelio_pipeline/infra/escrita_stardict.py` | `EscritorStarDict` | 🟢 |
| `pipeline/src/aurelio_pipeline/validacao/leitor_stardict.py` | `LeitorStarDict`, `_registros` | 🟢 |
| `pipeline/src/aurelio_pipeline/validacao/paridade.py` | `executar_paridade`, `ParityReport`, `gravar_relatorio`, `texto_de_html` | 🟢 |
| `pipeline/src/aurelio_pipeline/cli.py` | `_alvo_koreader` | 🟢 |
