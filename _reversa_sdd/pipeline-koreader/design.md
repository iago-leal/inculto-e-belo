# pipeline-koreader, Design Técnico

> Gerado pelo reversa-writer em 2026-10-15.

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `EscritorStarDict` | `(dist_dir: Path, basename: str = "aurelio-stardict", ...)` | instância | `basename` passado pela CLI 🟢 |
| `.escrever` | `(artigos: Iterable[(lema, html, formas)], data: str)` | `ResultadoBuild` (headwords, sinônimos, caminho) | `data` = `time.strftime("%Y-%m-%d")` 🟢 |
| `LeitorStarDict` | `(diretorio: Path)` | instância | Exige os 4 sufixos de `SUFIXOS_OBRIGATORIOS` 🟢 |
| `.headwords` / `.artigo(i)` | `()` / `(indice: int)` | `list[str]` / `str` | Acesso ao `.idx` e ao corpo 🟢 |
| `executar_paridade` | `(leitor, headwords_esperados, syn_esperado, mapa, textos_definicoes, ...)` | `ParityReport` | Sementes e tamanho da amostra com padrões 🟢 |
| `gravar_relatorio` | `(relatorio, caminho: Path)` | `None` | JSON UTF-8 indentado; reaproveitado pelo alvo Readest 🟢 |

## Fluxo Principal

1. `_alvo_koreader` recebe os artigos já renderizados, se o Readest também estiver no alvo, ou os renderiza sob demanda a partir de `repositorio.artigos()` (`cli.py:51`). 🟢
2. `EscritorStarDict.escrever` (`infra/escrita_stardict.py:44`):
   - cria o glossário do PyGlossary com `bookname` «Aurélio (uso pessoal)», descrição padrão e data;
   - para cada artigo, `newEntry([lema, *formas], html, defiFormat="h")`, com log a cada 10.000;
   - grava num diretório temporário com `formatName="Stardict"`, `dictzip=True` e `sametypesequence="h"`;
   - confere os quatro arquivos e troca o diretório final por renomeação.
   🟢
3. A CLI grava `relatorio-cobertura.json` em `dist/aurelio-stardict/`. 🟢
4. `executar_paridade` (`validacao/paridade.py:60`) roda os cinco checks e acumula as divergências com `reprovar(check, detalhe)`. O veredito é «aprovado» só sem nenhuma divergência. 🟢
5. A CLI grava `parity-report.json` e devolve 0 ou 3. 🟢

## Fluxos Alternativos

- **Arquivo faltando após a escrita:** `FalhaGeracaoError`; com o `.dict.dz` ausente, a mensagem aponta o python-idzip. 🟢
- **Artefato ausente na leitura:** `ArtefatoAusenteError`. 🟢
- **Estrutura binária inválida:** `ArtefatoCorrompidoError`, com o arquivo e a posição. 🟢
- **Paridade reprovada:** artefato já trocado em `dist/aurelio-stardict/`, log de erro e exit 3. 🟢

## Dependências

- `pipeline-nucleo`: artigos, mapa, headwords, `textos_definicoes` e relatório de cobertura.
- PyGlossary 5.4.1 e python-idzip (`pipeline/pyproject.toml`).
- KOReader no Boox, como consumidor do artefato.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| PyGlossary confinado num adaptador | `infra/escrita_stardict.py` (ADR-0006) | 🟢 |
| Leitor de verificação independente do escritor | `validacao/leitor_stardict.py` | 🟢 |
| Extração de texto do HTML sem inserir espaço, igual à derivação do `content_text` | `validacao/paridade.py:34` | 🟢 |
| Troca sem retenção nem promoção condicionada, ao contrário do Readest | `infra/escrita_stardict.py` e ADR-0008 | 🟢 |

## Estado Interno

Nenhum estado persistente fora de `dist/aurelio-stardict/`. O leitor carrega o corpo descomprimido inteiro em memória. 🟢

## Observabilidade

- `etapa=conversao alvo=koreader`, com progresso do escritor;
- `etapa=paridade alvo=koreader`;
- `alvo_fim alvo=koreader veredito=… headwords=… sinonimos=… duracao_s=… relatorio=…`;
- os relatórios `relatorio-cobertura.json` e `parity-report.json`.

## Riscos e Lacunas

- 🟡 DT-07 de `architecture.md`: o artefato reprovado fica no lugar do aprovado; um usuário que ignore o exit 3 instalaria um artefato reprovado.
- 🟡 Recomendação da feature 001 (GO presumido, sem medição no Boox): tempo de abertura e de consulta no aparelho ainda não medidos.
