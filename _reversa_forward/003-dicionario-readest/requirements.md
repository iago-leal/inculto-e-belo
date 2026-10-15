# Requirements: Dicionário do Aurélio para o Readest

> Identificador: `003-dicionario-readest`
> Data: `2026-10-15`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Esta feature entrega uma segunda versão do dicionário, destinada ao leitor Readest e gerada pelo mesmo pipeline que hoje produz a do KOReader. O Readest lê o mesmo formato, mas, ao consultar uma palavra, exibe um único verbete, ao passo que o KOReader exibe todos os que lhe correspondem; por isso formas frequentes como «era», «foi» e «fosse» perdem parte dos sentidos. A nova versão reúne numa só página todos os verbetes de cada palavra, de modo que o Readest dê o mesmo resultado que o KOReader. O usuário é o próprio mantenedor, como leitor no Readest e como operador do build; a versão do KOReader permanece como está.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#2-componentes` | Pipeline em camadas P-01 a P-04 (ingestão, índice de flexões, conversão, validação), hoje implementado em `pipeline/` pela feature 002; a nova versão reaproveita ingestão, índice e renderização | 🟡 |
| `_reversa_sdd/domain.md#3-regras-de-negócio` | RB-02 (fusão por lema é decisão do consumidor), RB-11 (uso estritamente pessoal), RB-12 (regeneração determinística e auditável), RB-13 (retomável por README) | 🟢 |
| `_reversa_sdd/domain.md#4-invariantes-quantitativas-baseline-2026-07-03` | 137.784 lemas únicos; base do índice de 774.003 formas válidas | 🟢 |
| `_reversa_sdd/sdd/conversao-formato.md#15-decisões-tomadas-decision-log` | Homônimos fundidos num artigo por lema porque «headwords repetidos têm comportamento imprevisível entre leitores»; formato StarDict com conteúdo HTML | 🟡 |
| `_reversa_sdd/sdd/validacao-paridade.md#6-requisitos-funcionais` | Validação independente com leitor próprio, tolerância zero e exit code como gate | 🟡 |
| `_reversa_sdd/prd.md#5-não-objetivos-out` | «Outras aplicações além do KOReader» ficaram para ciclos futuros; esta feature é esse ciclo | 🟡 |
| `_reversa_sdd/user-stories` e `_reversa_sdd/personas.md` | Personas iago-leitor e iago-mantenedor-futuro | 🟡 |
| `_reversa_forward/002-build-completo-de-producao/requirements.md#4-regras-de-negócio-novas-ou-alteradas` | RN-04 (gate de paridade), RN-05 (uso pessoal), RN-06 (determinismo), RN-07 (formas grafadas como no banco) | 🟢 |
| Código do leitor de dicionários do Readest, versões 0.12.12 a 0.12.16 (idênticas nos arquivos de busca) | Compara palavras em minúsculas; consulta o índice principal antes do índice de formas; devolve um único resultado; aceita conteúdo HTML e o arquivo comprimido em blocos; importa os quatro arquivos pela tela de dicionários e sincroniza-os com a nuvem do Readest quando a sincronização de dicionários está ligada | 🟢 |
| Medição de 2026-10-15, com o código de busca do Readest executado sobre `dist/aurelio-stardict/` | 137.648 de 137.784 verbetes abrem corretamente (132 colidem por maiúscula/minúscula, 4 ficam inalcançáveis por ordem de índice: «à», «à clef», «à clé», «Å»); 749.895 de 774.003 formas abrem o verbete certo; 22.913 palavras correspondem a mais de um verbete; 261 formas «/» sem letra vêm de verbos defectivos; texto de 100% dos verbetes lido íntegro | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| iago-leitor | Consultar o Aurélio completo ao ler no Readest | Seleciona «foi» num livro e a página do dicionário mostra os verbetes «ir» e «ser»; seleciona «cantávamos» e vê só «cantar» |
| iago-mantenedor-futuro | Regenerar as duas versões após meses de pausa, guiado pelo README | Roda a CLI do pipeline pedindo a versão do Readest; a validação aprova ou bloqueia com relatório nominal das divergências |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** A versão do Readest é um artefato separado, gerado do mesmo banco e com o mesmo conteúdo de artigos da versão do KOReader; a versão do KOReader não muda em conteúdo nem em contagens. 🟢
   - Origem no legado: `_reversa_forward/002-build-completo-de-producao/requirements.md#5-requisitos-funcionais` (RF-05)
   - Tipo: nova
2. **RN-02:** Cada consulta abre uma página com **exatamente** os artigos de todos os lemas a que a palavra corresponde, sem faltar nem sobrar: os homônimos e homógrafos do próprio lema e os lemas de que ela é forma flexionada. A correspondência ignora diferença entre maiúsculas e minúsculas, como faz o Readest. 🟢
   - Origem no legado: estende a fusão de homônimos de `_reversa_sdd/sdd/conversao-formato.md#15-decisões-tomadas-decision-log` a homógrafos entre lemas e formas; decisão do usuário em 2026-10-15 (opção «juntar os verbetes numa página só»)
   - Tipo: alterada
3. **RN-03:** Uma forma que pertence a um só lema abre só o artigo desse lema, ainda que a palavra do lema, consultada diretamente, abra página combinada. Exemplo: «vieram» abre só «vir», embora «vir» abra «vir» e «ver». 🟢
   - Origem no legado: decorre de RN-02 («sem sobrar»)
   - Tipo: nova
4. **RN-04:** Numa página combinada, vem primeiro o artigo cujo lema coincide com a palavra consultada; os demais seguem com os de vocabulário frequente à frente (verbetes que o banco marca como tal) e, no empate, em ordem alfabética. Exemplo: «fosse» abre «ir», «ser» e «fossar», nessa ordem. Cada artigo abre com o próprio lema em destaque e separa-se do seguinte por divisor visível. 🟢
   - Origem no legado: marca de vocabulário frequente em `_reversa_sdd/domain.md#6-lacunas--revisadas-em-2026-07-03` (L-04, critério editorial inferido); decisão do usuário em 2026-10-15 (§9)
   - Tipo: nova
5. **RN-05:** A ordem dos índices da versão do Readest segue a comparação do próprio Readest, e não a ordem canônica do formato, de modo que toda palavra pesquisável seja encontrável; com isso, as quatro entradas hoje inalcançáveis passam a abrir. 🟢
   - Origem no legado: n/a (achado da medição de 2026-10-15)
   - Tipo: nova
6. **RN-06:** Formas sem nenhuma letra (as 261 «/» de verbos defectivos) ficam fora da versão do Readest; a versão do KOReader as mantém até decisão em contrário. 🟢
   - Origem no legado: decisão do usuário em 2026-10-15
   - Tipo: nova
7. **RN-07:** Nenhum artefato do Readest é entregue sem validação independente aprovada e sem aprovação na conferência com o código de busca do próprio Readest, ambas com tolerância zero a divergências. 🟢
   - Origem no legado: `_reversa_forward/002-build-completo-de-producao/requirements.md#4-regras-de-negócio-novas-ou-alteradas` (RN-04); estendida por decisão do usuário em 2026-10-15 (§9)
   - Tipo: alterada
8. **RN-08:** O artefato continua de uso estritamente pessoal e nunca é publicado. Por decisão do usuário em 2026-10-15, pode ficar armazenado na nuvem privada do Readest, vinculada à conta dele, para chegar aos seus outros aparelhos; esse armazenamento privado não constitui publicação. O repositório, que é público, não recebe conteúdo do Aurélio, nem como artefato nem como dado de teste. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#3-regras-de-negócio` (RB-11); altera o requisito de privacidade da feature 002, segundo o qual nenhum dado saía do processo local
   - Tipo: alterada
9. **RN-09:** Duas execuções sobre o mesmo banco produzem o mesmo conteúdo nos índices e no corpo do artefato do Readest. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#3-regras-de-negócio` (RB-12)
   - Tipo: herdada (inalterada)

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | O pipeline gera, a pedido, a versão do Readest numa pasta própria de saída, com os quatro arquivos importáveis pelo Readest (descrição, índice principal, índice de formas e corpo comprimido), conteúdo em HTML, metadados coerentes (nome, totais, data) e escrita atômica | Must | A pasta nova contém os quatro arquivos com totais declarados iguais aos reais; build interrompido não deixa versão parcial; a versão do KOReader segue com 137.784 verbetes e 774.003 formas | 🟢 |
| RF-02 | O agrupamento por palavra é função de domínio pura: a partir dos lemas e do mapa de formas, decide quais artigos cada palavra pesquisável exibe e em que ordem (RN-02, RN-04, RN-06), e emite relatório JSON com páginas simples, páginas combinadas, formas descartadas por não terem letra e distribuição de artigos por página | Must | Sobre o banco atual: 22.913 páginas combinadas; «era» → era, ser, erar; «foi» → ir, ser; «fosse» → ir, ser, fossar; «boa» → boa, bom, boar (listas na ordem de exibição); 261 formas descartadas por falta de letra; testes de unidade sem banco real | 🟢 |
| RF-03 | Cada artigo continua endereçável isoladamente para as formas de um só lema (RN-03), sem duplicar texto quando o artigo já faz parte de uma página combinada | Must | «vieram» abre só «vir»; nenhuma das 13.549 formas cujo lema abre página combinada exibe artigo alheio | 🟢 |
| RF-04 | Os índices da versão do Readest seguem a comparação do Readest (RN-05): cada chave é única nessa comparação e a sequência é estritamente crescente | Must | «à», «à clef», «à clé» e «Å» abrem os próprios verbetes; zero palavras pesquisáveis inalcançáveis | 🟢 |
| RF-05 | A validação independente lê o artefato com o leitor próprio do projeto, imita a busca do Readest para **todas** as palavras pesquisáveis e confere que a página aberta tem exatamente os artigos esperados; confere ordem, unicidade das chaves, metadados e uma amostra de 500 lemas (semente fixa) cujas definições do banco devem constar da página; grava relatório e sai com código 0 só em aprovação | Must | Página sem um artigo, página com artigo a mais, chave fora de ordem e metadado divergente reprovam, cada um com a divergência nominal no relatório | 🟢 |
| RF-06 | Como etapa obrigatória do gate, a geração da versão do Readest executa sobre o artefato o código de busca do próprio Readest, em versão fixada, obtido do repositório público do Readest e guardado em cache local fora do git; a falta do ambiente de execução desse código, ou da rede na primeira obtenção, interrompe a geração com erro nomeado | Must | 100% das palavras pesquisáveis abrem a página esperada e 100% dos artigos são lidos íntegros do corpo comprimido; qualquer falha reprova o artefato; sem o ambiente de execução, a geração termina com código diferente de 0 e mensagem acionável; com o cache presente, a geração funciona sem rede | 🟢 |
| RF-07 | A CLI única passa a aceitar o alvo da geração (KOReader, Readest ou ambos), mantendo o comportamento atual quando o alvo não é informado | Must | Sem argumento novo, o build produz só a versão do KOReader, como hoje; com o alvo do Readest, produz e valida a versão nova; o log final traz totais, duração e caminho do relatório de cada alvo gerado | 🟢 |
| RF-08 | O artefato aprovado é importado no Readest do Mac pela tela de dicionários, com a sincronização de dicionários ligada (RN-08), e fica habilitado | Must | No Readest do Mac, num livro em português, «era», «foi», «vieram» e «cantávamos» abrem as páginas descritas em RF-02 e RF-03 | 🟢 |
| RF-09 | O README do pipeline documenta a geração da versão do Readest, os números esperados, a importação e a atualização no Readest e as limitações conhecidas | Must | Seguindo só o README, o mantenedor gera, valida e reinstala a versão do Readest sem passo não documentado | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Build da versão do Readest em menos de 2 min e validação integral em menos de 2 min (MacBook do mantenedor) | O build do KOReader leva cerca de 12 s; a medição de 2026-10-15 percorreu todas as palavras em cerca de 10 s | 🟡 |
| Memória | Pico do processo abaixo de 2 GB | Herdado da feature 002 (pico atual de cerca de 0,6 GB) | 🟢 |
| Tamanho | Artefato do Readest com até 50 MB | Estimativa de cerca de 38 MB, apresentada e aceita pelo usuário em 2026-10-15 (corpo cresce cerca de 36 MB antes da compressão) | 🟡 |
| Latência | Consulta no Readest do Mac abre a página em menos de 1 s | Métrica do PRD (`_reversa_sdd/prd.md#3-métricas-de-sucesso`); o Readest lê o corpo comprimido por blocos | 🟡 |
| Compatibilidade | Funciona no Readest 0.12.12 ou posterior | Versão instalada no Mac; código de busca idêntico de 0.12.12 a 0.12.16 | 🟢 |
| Testabilidade | Domínio puro com testes de unidade; cobertura de pelo menos 60%; dados de teste sintéticos, sem conteúdo do Aurélio | Herdado da feature 002; repositório público (RN-08) | 🟢 |
| Observabilidade | Logs chave=valor por etapa e relatórios JSON de agrupamento e de validação persistidos por execução | Herdado da feature 002 | 🟢 |
| Reprodutibilidade | Dependências com versões exatas; a conferência com o código do Readest fixa a versão dele | `_reversa_sdd/domain.md#3-regras-de-negócio` (RB-12, RB-13) | 🟢 |
| Dependências de execução | A geração da versão do Readest exige o ambiente de execução JavaScript Node.js, já instalado no Mac do mantenedor, e acesso à rede apenas na primeira obtenção do código do Readest; o uso do dicionário no Readest não depende de rede | Decisão do usuário em 2026-10-15 (§9) | 🟢 |
| Privacidade | Artefato fora do git; nuvem privada do Readest autorizada; nenhuma publicação | RN-08 | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: build da versão do Readest aprovado de ponta a ponta
  Dado o banco íntegro e o manifesto de integridade em dia
  Quando o mantenedor roda a CLI pedindo o alvo do Readest
  Então a pasta de saída do Readest contém os quatro arquivos com totais declarados iguais aos reais
  E o relatório de validação registra veredito «aprovado» e o processo termina com código 0

Cenário: forma de dois lemas abre os dois verbetes
  Dado a versão do Readest aprovada e importada
  Quando o leitor consulta «foi»
  Então a página mostra o verbete «ir» e o verbete «ser», cada um aberto pelo próprio lema e separados por divisor

Cenário: lema que também é forma de outros lemas
  Dado a versão do Readest aprovada e importada
  Quando o leitor consulta «era»
  Então a página mostra primeiro o substantivo «era» e depois os verbetes «ser» e «erar», nessa ordem

Cenário: verbete de vocabulário frequente vem antes do raro
  Dado a versão do Readest aprovada e importada
  Quando o leitor consulta «fosse»
  Então a página mostra os verbetes «ir», «ser» e «fossar», nessa ordem

Cenário: forma de um só lema não traz verbete alheio
  Dado que «vir» abre página combinada com «ver»
  Quando o leitor consulta «vieram»
  Então a página mostra só o verbete «vir»

Cenário: palavra antes inalcançável passa a abrir
  Dado a versão do Readest aprovada
  Quando o leitor consulta «à»
  Então a página mostra o verbete «à», e não o de «a»

Cenário: forma sem letra fica de fora
  Dado o banco com 261 formas «/» de verbos defectivos
  Quando o pipeline gera a versão do Readest
  Então nenhuma chave «/» existe no artefato e o relatório de agrupamento registra 261 descartes por falta de letra

Cenário: versão do KOReader inalterada
  Dado o pipeline com suporte ao Readest
  Quando o mantenedor roda a CLI sem informar o alvo
  Então só a versão do KOReader é gerada, com 137.784 verbetes e 774.003 formas, aprovada pela validação de sempre

Cenário: página incompleta reprova a validação
  Dado um artefato do Readest em que «foi» abre só «ir»
  Quando a validação independente executa
  Então o relatório registra veredito «reprovado», nomeia «foi» e o artigo ausente, e o processo termina com código diferente de 0

Cenário: chave fora de ordem reprova a validação
  Dado um artefato do Readest com duas chaves em ordem invertida
  Quando a validação independente executa
  Então o relatório registra veredito «reprovado» com as duas chaves envolvidas

Cenário: conferência com o código do próprio Readest integra o gate
  Dado o artefato do Readest aprovado pela validação independente
  Quando a geração roda o código de busca do Readest em versão fixada
  Então todas as palavras pesquisáveis abrem a página esperada e todos os artigos são lidos íntegros
  E qualquer falha reprova o artefato com código diferente de 0

Cenário: ambiente de execução ausente interrompe a geração
  Dado um Mac sem o ambiente de execução do código do Readest
  Quando o mantenedor pede a geração da versão do Readest
  Então a geração termina com código diferente de 0 e mensagem que diz o que instalar, sem entregar artefato não conferido

Cenário: instalação no Readest do Mac
  Dado o artefato aprovado e a sincronização de dicionários ligada
  Quando o dicionário é importado pela tela de dicionários do Readest
  Então ele aparece habilitado e responde às consultas de «era», «foi», «vieram» e «cantávamos»

Cenário: reinstalação guiada pelo README
  Dado o banco atualizado e o README do pipeline
  Quando o mantenedor segue só o README para gerar e reinstalar a versão do Readest
  Então conclui sem passo não documentado
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-07 | Must | Sem a geração separada e a CLI, a versão do KOReader correria risco e o mantenedor perderia o comando único |
| RF-02, RF-03 | Must | São a razão da feature: página completa sem verbete alheio |
| RF-04 | Must | Sem a ordem do Readest, palavras ficam inalcançáveis |
| RF-05 | Must | Gate de entrega (RN-07) |
| RF-06 | Must | Decisão do usuário em 2026-10-15: a conferência com o código real do Readest integra o gate |
| RF-08 | Must | Entrega no aparelho é o objetivo do usuário |
| RF-09 | Must | Retomabilidade por README (RB-13) |
| Tabelas de conjugação e demais melhorias de verbos nos verbetes | Won't | Pedido do usuário para feature posterior |
| Retirar as formas «/» da versão do KOReader | Won't | Só sob pedido do usuário (RN-06) |
| Links clicáveis entre verbetes | Won't | O Readest não segue links nesse formato de dicionário |

## 9. Esclarecimentos

### Sessão 2026-10-15

- **Q:** A conferência feita com o código de busca do próprio Readest fica guardada no projeto e com que peso?
  **R:** Etapa obrigatória da geração da versão do Readest; o usuário aceita depender de rede, ao menos na primeira obtenção do código, e do ambiente de execução já instalado. Integrado a RF-06, RN-07, §6 (dependências de execução) e §7.
- **Q:** Em que ordem vêm, depois do artigo do próprio lema, os demais artigos de uma página combinada? (a) alfabética; (b) vocabulário frequente primeiro, alfabética no empate; (c) verbete mais longo primeiro; (d) frequente, depois mais longo, depois alfabética.
  **R:** (b). Medição sobre o banco atual: das 22.913 páginas combinadas, 9.787 têm dois ou mais artigos de outros lemas; a marca muda a ordem alfabética em 866 delas e, nas demais, prevalece a alfabética. O critério por extensão foi descartado por erros visíveis («esposa» abriria «esposar» antes de «esposo»). Integrado a RN-04, RF-02 e §7.

## 10. Lacunas

Nenhuma.

## Pendências de Qualidade

- **SoluçãoImplícita (Q-018), exceção deliberada:** o documento nomeia os leitores Readest e KOReader porque eles são o objeto da feature, não escolha de implementação; a versão do Readest citada (0.12.12 a 0.12.16) é o limite de compatibilidade verificado; o Node.js é citado porque o código de busca do Readest só roda nesse ambiente, e a dependência foi aceita pelo usuário (§9).

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-15 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-10-15 | Sessão de esclarecimentos (parcial): conferência com o código do Readest vira etapa obrigatória (RF-06 Must, RN-07 alterada) | reversa + iago |
| 2026-10-15 | Sessão de esclarecimentos: ordem dos artigos na página combinada (RN-04 🔴 → 🟢, vocabulário frequente primeiro); RF-02 e §7 com listas ordenadas; lacunas zeradas | reversa + iago |
