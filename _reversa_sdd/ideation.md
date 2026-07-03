# Ideation, inculto-e-belo — Aurélio no KOReader

> Selo 🟡 PLANEJADO em todos os itens, sujeito a validação.

## Brief original

Utilizaremos esse banco de dados de dicionário (SQLite, Aurélio normalizado, ~143k verbetes) para desenvolver algumas aplicações. A primeira será fazer com que ele seja acessível ao KOReader.

Prioridades declaradas: longevidade, saúde, manutenibilidade e mínimo de dívida técnica. Isso inclui: alta coesão; baixo acoplamento; programação orientada a objetos; desenvolvimento orientado a testes (TDD); desenvolvimento orientado a especificações (SDD).

## Problema

🟡 Falta um dicionário de português brasileiro de qualidade utilizável no KOReader. Quem sente o problema é o leitor que, durante a leitura no e-reader, toca numa palavra e recebe verbete fraco, truncado ou nenhum resultado — os dicionários StarDict de português em circulação não têm a cobertura nem a qualidade do Aurélio. O momento da dor é o toque na palavra em plena leitura: a consulta ou funciona ali, offline e imediata, ou quebra o fluxo.

## Valor entregue

🟡 O Aurélio passa a existir num formato portátil que o e-reader consome diretamente — o usuário leva o dicionário para qualquer dispositivo, começando pelo KOReader, sem depender de conexão. O valor central é a portabilidade do ativo (143k verbetes), não apenas uma integração pontual.

## Alternativas existentes

🟡
- **Dicionários StarDict de português já circulantes** — cobertura pobre, verbetes truncados ou de origem duvidosa; nenhum se compara ao Aurélio normalizado. Não bastam por qualidade.
- **Dicionários online (navegador, apps)** — exigem conexão e quebram o fluxo de leitura no e-reader; incompatíveis com o cenário de uso offline.

## Público-alvo (bruto)

🟡 Perfil primário: o próprio mantenedor, leitor no ecossistema KOReader/Boox. Perfil aspiracional: a comunidade KOReader lusófona, caso o dicionário convertido venha a ser publicado — **condicionado à premissa de direitos autorais (ver abaixo); o escopo vigente é uso estritamente pessoal.**

## Métricas de sucesso

🟡
- **Uso diário real**: o dicionário instalado torna-se o padrão das leituras do mantenedor — toque em palavra retorna verbete do Aurélio em **< 1 segundo**, **offline**, por **90 dias** sem necessidade de manutenção.

## Premissas a validar

🟡
1. **A conversão preserva os ~143k verbetes** — supõe-se que o formato-alvo (StarDict/dictzip ou similar) comporta o volume e a formatação dos verbetes sem perda. Se houver perda estrutural, o produto perde sua razão de ser (a qualidade do Aurélio).
2. **O KOReader encontra a palavra flexionada** — supõe-se que o lookup funciona com plurais e verbos conjugados. Se só encontrar o lema exato, a experiência de toque-na-palavra morre na prática.
3. **Uso estritamente pessoal neste momento** — o escopo atual não inclui distribuição pública; a publicação à comunidade dependeria de resolver a questão de licença/direitos autorais do conteúdo do Aurélio.

## Notas

🟡
- Existe tensão deliberada entre o público aspiracional (comunidade lusófona) e a premissa 3 (uso pessoal): a arquitetura deve nascer pronta para publicação futura, mas nenhum artefato distribuível público faz parte do escopo inicial.
- O valor escolhido ("levar o Aurélio para qualquer dispositivo") sugere que o conversor/pipeline é o produto duradouro, e o artefato para KOReader é a primeira saída de várias — reforça as prioridades de baixo acoplamento e extensibilidade do brief.
- Contexto técnico herdado do projeto: `aurelio_normalized.db` (SQLite) fica fora do git; backup no Drive via rclone. A premissa implícita de integridade do banco normalizado não foi listada entre as três fatais, mas merece verificação de fumaça no pipeline.
- Prioridades de engenharia do brief (longevidade, alta coesão, baixo acoplamento, OOP, TDD, SDD) valem como restrições transversais para os agentes seguintes, não como features.

---
Gerado por reversa-ideator em 2026-07-03T19:30:34Z
Fonte: newproject-brief.md
