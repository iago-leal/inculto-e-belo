# pipeline-nucleo, Design Técnico

> Gerado pelo reversa-writer em 2026-10-15.

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `main` | CLI `aurelio-pipeline [--db] [--manifesto] [--dist] [--cobertura total\|flexions-somente] [--alvo koreader\|readest\|ambos]` | `sys.exit(código)` | `ErroPipeline` capturado vira exit 2 🟢 |
| `executar` | `(db: Path, manifesto: Path, dist: Path, cobertura: str, alvo: str = "koreader")` | `int` | Padrões: `../aurelio_normalized.db`, `pipeline/manifesto-integridade.json`, `../dist` 🟢 |
| `RepositorioAurelio` | `(db_path: Path, manifesto_path: Path)` | instância | Conexão preguiçosa, reaproveitada até `close()` 🟢 |
| `.validar` | `()` | `dict[str, int]` | Totais por tabela 🟢 |
| `.headwords` | `()` | `list[str]` | `DISTINCT lemma` ordenado 🟢 |
| `.lemas_frequentes` | `()` | `frozenset[str]` | Lemas com alguma entrada `most_used = 1` 🟢 |
| `.flexoes` / `.conjugacoes` | `()` | `Iterator[tuple[int, str, str]]` | `(id, cabeça, forma_bruta)` em ordem de id 🟢 |
| `.textos_definicoes` | `(lemma: str)` | `list[str]` | `content_text` de todas as acepções de todas as entradas do lema 🟢 |
| `.artigos` | `()` | `Iterator[tuple[str, list[Verbete]]]` | Agrupado por lema na ordem de fusão 🟢 |
| `dividir_formas` | `(bruta: str \| None, tabela: str, rowid: int)` | `list[str]` | Levanta `FormaAnomalaError` 🟢 |
| `construir_mapa` | `(fontes: Mapping[str, Iterable[(id, head, forma)]], headwords: Collection[str], progresso=None)` | `(dict[lema, list[forma]] ordenado, RelatorioCobertura)` | Formas ordenadas por lema 🟢 |
| `renderizar_artigo` | `(lemma: str, verbetes: Sequence[Verbete], advertir=None)` | `str` | Função pura 🟢 |

## Fluxo Principal

1. Se `readest` estiver no alvo, `ConferenciaReadest().preparar()` roda antes de tudo (`cli.py:200`). 🟢
2. `RepositorioAurelio.validar()` executa estes passos (`infra/repositorio.py:154`):
   - abre o banco com `sqlite3.connect("file:<db>?mode=ro", uri=True, timeout=5)` e `row_factory=Row`;
   - testa `SELECT 1 FROM sqlite_schema`;
   - para cada tabela de `COLUNAS_REQUERIDAS`, lê `PRAGMA table_info` e acumula tabelas ausentes e colunas faltantes;
   - conta as linhas e compara com o manifesto.
   🟢
3. `construir_mapa` recebe `{"flexions": flexoes()}` e, com cobertura total, também `{"conjugations": conjugacoes()}`, junto com `set(headwords)`. Para cada forma resultante do split, classifica (`dominio/indice_flexoes.py:55`):
   - **órfã**, se a cabeça não está em headwords: conta e registra a cabeça;
   - **idêntica**, se a forma é igual à cabeça;
   - **duplicada**, se o par já foi visto;
   - **gravada**, nos demais casos.

   Ao fim, a invariante é verificada com `assert`. 🟢
4. Se o Readest estiver no alvo, `artigos = {lema: renderizar_artigo(...)}` para todos os lemas (`cli.py:228`); o KOReader reusa esse dicionário na mesma execução. 🟢
5. Os alvos rodam em ordem (`koreader`, depois `readest`). O repositório é fechado em `finally`, e o código final é `max(codigos)`. 🟢

### Montagem do agregado `Verbete` (`infra/repositorio.py:337`)

Para cada linha de `entries` na `ORDEM_FUSAO`:
- blocos de `word_class_blocks` por `position`, com a classe vinda do cache `word_classes.whole`;
- acepções por `position`, com a rubrica vinda do cache `rubrics.abbreviation`, mais exemplos (`definition_id`, por `position`) e notas (`parent_type='definition'`);
- locuções por `position`, com definições, exemplos (`locution_definition_id`) e notas (`locution_definition`, `locution`);
- notas do verbete (`parent_type='entry'`);
- regências ordenadas por `COALESCE(sense, 0), position`.

### Renderização (`dominio/renderizacao.py:112`, seções em `:58`)

O artigo começa com `<b>{lema}</b>`, com escape HTML. Para cada verbete, a seção é numerada `<b>n.</b>` quando há mais de um, e contém, nesta ordem:
- um parágrafo de cabeçalho com `lemma_stylized` em `<b>` (se diferente do lema), a classe em `<i>` (`word_class_summary` dividido por vírgula, sem vazios, unido por ` · `) e `[ipa]`;
- `<p><small>Etim.: …</small></p>`;
- para cada bloco: `<p><i>classe</i></p>`, `<p>intro</p>` e `<ul>` com as acepções;
- cada acepção: `<li><b>número.</b> <i>rubrica</i> content_html`, seguida dos exemplos (` <i>…</i>` do editor; ` <small><i>…</i></small>` da abonação) e das notas (` <small>[Obs.: …]</small>`);
- as locuções: `<p><u>Locuções</u></p><ul><li><b>expressão</b> <i>rubrica</i>: definições unidas por "; " …</li></ul>`;
- a regência: `<p><u>Regência (Luft)</u></p><ul><li><b>sense.</b> transitividade (prep.: …) <small>observação</small></li></ul>`;
- as notas do verbete: `<p><small>[Nota: …]</small></p>`.

`content_html` e `etymology_html` entram sem escape, porque são HTML curado pelo banco; os demais textos passam por `html.escape(quote=False)`. 🟢

## Fluxos Alternativos

- **Banco ausente:** `BancoAusenteError`, com `rclone copy gdrive:inculto-e-belo/aurelio_normalized.db <dir>/`. 🟢
- **Banco bloqueado (`locked`/`busy`):** `BancoIndisponivelError`. 🟢
- **Arquivo ilegível:** `BancoCorrompidoError`, com o comando de restauração. 🟢
- **Manifesto ilegível ou sem `contagens`:** `ManifestoAusenteError`; sem `gerado_em`, também `ManifestoAusenteError`, mas só no alvo Readest. 🟢
- **Forma vazia:** `FormaAnomalaError("forma vazia ou só espaços em <tabela>.id=<id>")`. 🟢

## Dependências

- `banco-lexical`: as tabelas e colunas de `COLUNAS_REQUERIDAS`.
- `pipeline-koreader` e `pipeline-readest`: consumidores dos artigos, do mapa e dos headwords.
- stdlib: `sqlite3`, `json`, `html`, `re`, `logging`, `argparse`.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Repositório como único dono do SQL; consumidores recebem agregados e pares | `infra/repositorio.py:1` (docstring) | 🟢 |
| Validação de esquema e contagens antes de qualquer leitura de conteúdo | `infra/repositorio.py:154` | 🟢 |
| Ordem de classificação órfã → idêntica → duplicada (a órfã não entra em `vistos`) | `dominio/indice_flexoes.py:63` | 🟢 |
| Renderização em memória só quando o Readest está no alvo | `cli.py:227` | 🟢 |
| Exit code agregado pelo máximo | `cli.py:253` | 🟢 |

## Estado Interno

Caches de `word_classes` e `rubrics` em memória, criados no primeiro `artigos()`. Uma conexão SQLite por instância. Com o Readest no alvo, o dicionário de 137.784 artigos fica em memória durante a execução. 🟢

## Observabilidade

Logs no formato `etapa=<nome>`: `pre-verificacao`, `ingestao`, `indice`, `renderizacao`, `conversao`, `paridade`, `agrupamento`, `validacao` e `conferencia`. Além deles:
- `smoke_tests_ok duracao_ms=… <tabela>=<n>…`;
- `indice_ok gravadas=… orfas=… descartes=…`;
- `progresso pares_processados=…`;
- `alvo_fim alvo=… veredito=…`;
- `pipeline_fim alvo=… exit=… duracao_s=…`.

O formato é `%(asctime)s %(levelname)s %(message)s`. 🟢

## Riscos e Lacunas

- 🟢 Montagem do agregado por consultas aninhadas, N+1 por verbete (`infra/repositorio.py:266`–`:376`); aceitável no volume atual, de cerca de 12 s. **[Revisão 2026-10-15]** 🟡 → 🟢.
- 🟢 O docstring de `pipeline/src/aurelio_pipeline/__init__.py:1` lista só as camadas da feature 002 e não cita os módulos do Readest. **[Revisão 2026-10-15]** 🟡 → 🟢 (o fato está confirmado; a correção cabe ao mantenedor).
