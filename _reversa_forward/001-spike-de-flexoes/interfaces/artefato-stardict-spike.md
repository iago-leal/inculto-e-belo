# Contrato: artefato StarDict do spike (arquivo, consumido pelo KOReader)

> Identificador: `001-spike-de-flexoes`
> Tipo: arquivo (conjunto de 4 arquivos StarDict)
> Produtor: `spike/001-flexoes/gerar_spike.py` (via PyGlossary 5.4.1)
> Consumidor: KOReader no Boox Air 4C (lookup por toque e busca de dicionário)

## 1. Forma do artefato

Diretório `dist/aurelio-spike/` com basename comum (ex.: `aurelio-spike`):

| Arquivo                 | Papel                                              | Requisito                                                                                                                                                                        |
| ----------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `aurelio-spike.ifo`     | Metadados e contagens                              | `version=3.0.0`, `sametypesequence=h`, `bookname=Aurélio spike (uso pessoal)`, `wordcount=137784`, `synwordcount` = total real de formas gravadas (≥ 900.000), `date` da geração |
| `aurelio-spike.idx`     | Índice de headwords ordenado pela regra do formato | 137.784 headwords (lemas únicos, fusão de homônimos), UTF-8 com diacríticos preservados                                                                                          |
| `aurelio-spike.dict.dz` | Corpo dos artigos (HTML, dictzip)                  | Corpo trivial de uma linha para todos os lemas, exceto os 20 do roteiro (verbete completo)                                                                                       |
| `aurelio-spike.syn`     | Índice forma flexionada → posição do headword      | Todas as formas válidas de `flexions` + `conjugations` após descartes (órfã, duplicada, idêntica)                                                                                |

## 2. Semântica do lookup (o que o roteiro exercita)

- **Requisição:** toque longo numa palavra do texto (ou busca manual no dicionário do KOReader).
- **Resposta esperada:** popup com o artigo do headword; para forma flexionada, o artigo do lema apontado pelo `.syn`; para forma ambígua, as N correspondências listadas.
- **Erros possíveis:** nenhum resultado (forma ausente do `.syn` — órfã ou descartada); resultado errado (defeito de mapeamento); timeout perceptível (a hipótese sob teste, RN-05).

## 3. Propriedades operacionais

- **Idempotência:** regeneração sobre o mesmo banco produz artefato equivalente (mesmos headwords, mesmas formas, mesma ordenação — ordenação delegada ao PyGlossary; RNF-03 da spec `indice-de-flexoes`).
- **Atomicidade:** geração em diretório temporário com move final; nunca sobra artefato parcial em `dist/` (herda RF-05 da spec `conversao-formato`).
- **Timeout de referência:** não há timeout técnico no consumidor; o "timeout" é o critério de RN-05 (mediana < 1 s, máximo < 3 s).
- **Restrição de circulação:** o artefato contém conteúdo do Aurélio sob direitos autorais — instalação apenas em dispositivos do usuário, jamais publicado (RN-03).

## 4. Instalação (lado consumidor)

Cópia por USB/MTP para `koreader/data/dict/aurelio-spike/` no dispositivo; detecção automática pelo KOReader (conferível em Configurações → Dicionário). Nenhuma configuração adicional no leitor.

## 5. Diferenças em relação ao artefato de produção futuro

| Aspecto           | Spike                                                                   | Produção (spec `conversao-formato`)  |
| ----------------- | ----------------------------------------------------------------------- | ------------------------------------ |
| Corpo dos artigos | Trivial (1 linha), exceto 20 lemas                                      | Verbete completo para todos os lemas |
| `bookname`        | `Aurélio spike (uso pessoal)`                                           | `Aurélio (uso pessoal)`              |
| Destino           | `spike/001-flexoes/dist/`                                               | `dist/aurelio-stardict/`             |
| Distribuição      | USB manual                                                              | Componente `distribuicao-webdav`     |
| `.idx`/`.syn`     | **Idênticos em escala e mecânica** — é isso que dá validade ao veredito | Idem                                 |
