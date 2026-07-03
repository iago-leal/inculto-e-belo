# Spec: validacao-paridade

> Selo 🟡 PLANEJADO. Spec SDD gerada pelo reversa-spec-sdd a partir do prd.md. Todos os itens são hipóteses de projeto, não fatos de código existente.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-07-03
**Reviewers:** iago

---

## 1. Resumo

🟡 Validador independente do artefato: lê o dicionário StarDict gerado com parser próprio (sem PyGlossary), compara contagens e conteúdo amostrado contra o banco de origem, e emite veredito binário com relatório JSON. É o gate que separa "build concluiu" de "build está correto" — nenhum artefato segue para distribuição sem passar aqui.

---

## 2. Contexto e Motivação

**Problema:**
🟡 O risco de maior impacto do PRD é perda ou truncamento silencioso de verbetes na conversão. Como a geração usa o PyGlossary, validar com o próprio PyGlossary criaria dependência circular: um defeito da biblioteca passaria despercebido por afetar igualmente escrita e leitura.

**Evidências:**
🟡 O PRD define como critério de aceite: "o artefato final contém 100% dos verbetes, comprovado por validação automatizada". A mitigação prescrita na seção 8 é contagem total mais amostragem comparada à origem.

**Por que agora:**
🟡 A validação precisa nascer junto com o conversor (TDD): o teste de paridade é a definição executável de "conversão correta".

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Comprovar que 100% dos headwords esperados estão presentes e legíveis no artefato.
- [ ] 🟡 G-02: Comprovar que 100% das entradas esperadas do `.syn` apontam ao headword correto.
- [ ] 🟡 G-03: Comprovar, por amostragem determinística de conteúdo, que os artigos preservam o texto das definições da origem.
- [ ] 🟡 G-04: Bloquear a distribuição de artefato reprovado por construção (exit code), não por disciplina.

**Métricas de sucesso:**
| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Headwords verificados por contagem | 0 | 100% do esperado | na entrega |
| 🟡 Entradas do `.syn` verificadas por contagem | 0 | 100% do esperado | na entrega |
| 🟡 Amostra de verbetes com conteúdo comparado | 0 | 500 lemas (seed fixa) | por execução |
| 🟡 Amostra de flexões com destino verificado | 0 | 500 formas (seed fixa) | por execução |
| 🟡 Duração da validação completa | inexistente | < 3 min | na entrega |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Validar a experiência no dispositivo (latência do popup, renderização e-ink) — coberta pelo spike do componente `indice-de-flexoes` e pelo monitoramento pós-instalação.
- 🟡 NG-02: Corrigir divergências encontradas — o validador reporta e reprova; a correção acontece no conversor ou no banco, por decisão humana.
- 🟡 NG-03: Comparação de fidelidade tipográfica do HTML (espaços, ordem de atributos) — a paridade exigida é do texto das definições, não do markup byte a byte.
- 🟡 NG-04: Validar a publicação no WebDAV — responsabilidade do componente `distribuicao-webdav`.

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 iago-mantenedor-futuro, que confia no exit code do validador como única evidência necessária de que o artefato regenerado está íntegro.
**Usuário secundário:** 🟡 o componente `distribuicao-webdav`, que só aceita artefato acompanhado de relatório aprovado.

**Jornada atual (sem a feature):**
🟡 A única forma de detectar verbete perdido seria tocar nele durante uma leitura, meses depois — falha silenciosa clássica.

**Jornada futura (com a feature):**
🟡 Cada build termina com veredito explícito em segundos: aprovado com relatório de evidências, ou reprovado com a lista exata das divergências.

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID       | Requisito                                                                                                                                                                                                                | Prioridade | Critério de Aceite                                                                                                                          |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 🟡 RF-01 | O sistema deve ler `.ifo`, `.idx`, `.syn` e `.dict.dz` com parser próprio baseado apenas na biblioteca padrão (struct, gzip), sem importar PyGlossary.                                                                   | Must       | Dado o artefato gerado, quando o validador executa, então nenhum módulo do PyGlossary é importado (verificável por teste de importação).    |
| 🟡 RF-02 | O sistema deve comparar o número de headwords do `.idx` com o número de lemas únicos do banco e com o `wordcount` declarado no `.ifo`; qualquer diferença reprova.                                                       | Must       | Dado artefato com um headword a menos, quando a validação roda, então o veredito é reprovado e o relatório aponta esperado vs. obtido.      |
| 🟡 RF-03 | O sistema deve comparar o número de entradas do `.syn` com o total `gravadas` do relatório de cobertura do `indice-de-flexoes` e com o `synwordcount` do `.ifo`.                                                         | Must       | Dado `.syn` truncado, quando a validação roda, então o veredito é reprovado com as três contagens no relatório.                             |
| 🟡 RF-04 | O sistema deve sortear 500 lemas com seed fixa (registrada no relatório), extrair o artigo do `.dict.dz` via offsets do `.idx` e verificar que o texto de cada definição do banco está contido no artigo correspondente. | Must       | Dado um artigo com definição faltante, quando a amostra o inclui, então o relatório lista lema, definição ausente e o veredito é reprovado. |
| 🟡 RF-05 | O sistema deve sortear 500 formas flexionadas com seed fixa e verificar que cada entrada do `.syn` resolve ao índice do headword correto.                                                                                | Must       | Dada entrada do `.syn` apontando ao artigo errado, quando a amostra a inclui, então o relatório lista forma, destino esperado e obtido.     |
| 🟡 RF-06 | O sistema deve gravar `parity-report.json` com veredito, contagens, seeds, amostras verificadas e divergências, e terminar com exit code 0 apenas em aprovação total; tolerância de divergências é zero.                 | Must       | Dado qualquer check reprovado, quando o processo termina, então exit code ≠ 0 e o relatório contém a divergência.                           |
| 🟡 RF-07 | O sistema deve validar a integridade estrutural do `.idx`: offsets crescentes, tamanhos positivos e último offset dentro dos limites do `.dict` descomprimido.                                                           | Must       | Dado `.idx` truncado no meio de um registro, quando o parse roda, então falha com `ArtefatoCorrompidoError` indicando a posição do defeito. |

### 6.2 Fluxo Principal (Happy Path)

1. O pipeline invoca o validador com o diretório do artefato, o banco de origem e o relatório de cobertura de flexões.
2. O sistema parseia `.ifo`, `.idx` e `.syn` com o parser próprio e valida a integridade estrutural.
3. O sistema executa as comparações de contagem (headwords, sinônimos, metadados do `.ifo`).
4. O sistema executa as duas amostragens determinísticas de conteúdo e destino.
5. O sistema grava `parity-report.json` com veredito aprovado e termina com exit code 0.
6. Resultado: artefato liberado para o componente `distribuicao-webdav`.

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Reprovação:**

1. Qualquer verificação encontra divergência.
2. O sistema completa as demais verificações (relatório integral, sem parar na primeira falha), grava o relatório reprovado e termina com exit code ≠ 0.
3. O mantenedor corrige a causa e regenera o artefato; a distribuição permanece bloqueada.

---

## 7. Requisitos Não-Funcionais

| ID        | Requisito                     | Valor alvo                                   | Observação                                                |
| --------- | ----------------------------- | -------------------------------------------- | --------------------------------------------------------- |
| 🟡 RNF-01 | Duração da validação completa | < 3 min                                      | contagens integrais + 1.000 amostras                      |
| 🟡 RNF-02 | Dependências externas         | 0                                            | parser em stdlib pura é condição de independência (RF-01) |
| 🟡 RNF-03 | Determinismo                  | mesma entrada + mesma seed → mesmo relatório | seeds registradas no próprio relatório                    |
| 🟡 RNF-04 | Pico de memória               | < 1 GB                                       | índice em memória; artigos extraídos um a um              |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 módulo próprio de validação com CLI dedicada (invocável isoladamente ou pelo pipeline); parser StarDict de leitura como submódulo reutilizável.

**Comportamento esperado:**
🟡 Separação em dois papéis: um leitor StarDict (parse binário, stdlib pura — infraestrutura) e um conjunto de verificações de paridade (domínio, cada check é uma classe com nome, execução e resultado). Adicionar um check novo no futuro é criar uma classe, sem tocar nas existentes.

**Estados da UI:**

- Estado vazio: n/a — CLI com saída em log estruturado.
- Estado de carregamento: log por verificação iniciada.
- Estado de erro: `ArtefatoCorrompidoError` ou veredito reprovado com exit code ≠ 0.
- Estado de sucesso: veredito aprovado, caminho do relatório no log.

---

## 9. Modelo de Dados

**Entidades novas ou modificadas:**

```
ParityReport {
  veredito: "aprovado" | "reprovado"
  gerado_em: str (ISO 8601)
  seeds: {verbetes: int, flexoes: int}
  contagens: {headwords_idx: int, headwords_esperado: int,
              syn: int, syn_esperado: int,
              wordcount_ifo: int, synwordcount_ifo: int}
  amostras: {verbetes_ok: int, flexoes_ok: int}
  divergencias: list[{check: str, detalhe: str}]
}
```

**Migrações necessárias:** Não — relatório JSON regenerável por execução.

---

## 10. Integrações e Dependências

| Dependência                                      | Tipo        | Impacto se indisponível                                                 |
| ------------------------------------------------ | ----------- | ----------------------------------------------------------------------- |
| 🟡 Artefato em `dist/aurelio-stardict/`          | Obrigatória | Falha imediata com `ArtefatoAusenteError` orientando rodar o build      |
| 🟡 `aurelio_normalized.db` (fonte de verdade)    | Obrigatória | Reutiliza o componente `ingestao-aurelio`, com os mesmos erros nomeados |
| 🟡 Relatório de cobertura do `indice-de-flexoes` | Obrigatória | Sem ele a contagem esperada do `.syn` é indeterminável; falha nomeada   |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário                                                        | Trigger                                                    | Comportamento esperado                                                             |
| -------------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| 🟡 EC-01: Artefato ausente ou incompleto                       | Diretório sem um dos quatro arquivos                       | `ArtefatoAusenteError` nomeando o arquivo que falta; exit code ≠ 0                 |
| 🟡 EC-02: `.idx` corrompido                                    | Offsets decrescentes, registro truncado                    | `ArtefatoCorrompidoError` com posição do defeito; sem tentativa de leitura parcial |
| 🟡 EC-03: `.dict.dz` com falha de descompressão                | gzip inválido ou truncado                                  | Erro nomeado distinguindo corrupção de compressão de corrupção de índice           |
| 🟡 EC-04: Divergência em 1 único item da amostra               | Definição ausente num artigo amostrado                     | Reprovação integral (tolerância zero); relatório identifica o item exato           |
| 🟡 EC-05: Metadados do `.ifo` inconsistentes com o `.idx` real | `wordcount` declarado difere do contado                    | Reprovação com as duas contagens; defeito de metadado é defeito do artefato        |
| 🟡 EC-06: Banco de origem mudou depois do build                | Contagens do banco diferem das do manifesto usado no build | Reprovação com aviso de dessincronia build↔validação; orienta regenerar o build    |

---

## 12. Segurança e Privacidade

- **Autenticação:** n/a — execução local.
- **Autorização:** n/a.
- **Dados sensíveis:** o relatório cita lemas e trechos de definição (conteúdo sob direitos autorais); permanece local, junto do artefato de uso pessoal.
- **Auditoria:** `parity-report.json` versionado por build (data no nome) é o registro permanente de aprovação.

---

## 13. Plano de Rollout

- **Estratégia:** nasce junto com o conversor via TDD; o pipeline encadeia build → validação desde a primeira execução completa.
- **Como reverter (rollback):** `git revert` do código; relatórios anteriores permanecem como histórico.
- **Monitoramento pós-deploy:** o exit code integra o pipeline; reprovação interrompe a cadeia antes da distribuição.

---

## 14. Open Questions

| #        | Pergunta                                                                                                                                               | Impacto | Dono | Prazo                                     |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- | ---- | ----------------------------------------- |
| 🟡 OQ-01 | A comparação de texto da amostra deve normalizar whitespace do HTML renderizado antes do contains (risco de falso negativo por reformatação legítima)? | Médio   | iago | definir no reversa-plan, com fixture real |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão                                | Alternativas consideradas                                   | Racional                                                                                                                                         |
| -------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Parser de leitura próprio em stdlib    | Ler com o próprio PyGlossary; validar com sdcv externo      | Independência do caminho de escrita é o valor central do gate; ler StarDict é ordens de magnitude mais simples que escrever                      |
| Tolerância zero em divergências        | Threshold percentual de falhas aceitáveis                   | O alvo do PRD é 100% dos verbetes; qualquer tolerância reintroduz a falha silenciosa que o componente existe para impedir                        |
| Amostra de 500 + 500 com seed fixa     | Comparação integral de conteúdo; amostra aleatória sem seed | Integral custaria minutos a mais por build com ganho marginal sobre contagem integral + amostra; seed fixa garante reprodutibilidade do veredito |
| Relatório integral, sem parada precoce | Parar na primeira divergência                               | Uma execução reprovada deve dar o quadro completo para o diagnóstico, poupando ciclos de regeneração                                             |

---

## Apêndice

### Referências

- prd.md (seções 3, 8 e 9) em `_reversa_sdd/`
- Formato StarDict: estrutura de `.ifo`/`.idx`/`.syn` documentada no repositório do PyGlossary (doc/p/stardict.md)

### Histórico de Revisões

| Versão | Data       | Autor            | Mudanças        |
| ------ | ---------- | ---------------- | --------------- |
| 1.0    | 2026-07-03 | reversa-spec-sdd | Criação inicial |

---

## Relatório de avaliação automática

> Gerado por `spec_scorer.py` em 2026-07-03. Selo 🟡 mantido em todos os itens.

```

============================================================
  SPEC QUALITY REPORT
  Arquivo: _reversa_sdd/sdd/validacao-paridade.md
============================================================

  SCORE TOTAL: 100.0/100  —  ⭐ Excelente — Pronta para implementação

  BREAKDOWN POR DIMENSÃO:
  Dimensão             Score      Peso     Contribuição
  --------------------------------------------------
  Completude           100%       30%     30.0/pt
  Testabilidade        100%       25%     25.0/pt
  Clareza              100%       20%     20.0/pt
  Escopo               100%       15%     15.0/pt
  Edge Cases           100%       10%     10.0/pt

  ✅ PONTOS FORTES:
     ✅ Seção 1 (Resumo) presente e preenchida
     ✅ Seção 2 (Contexto) presente e preenchida
     ✅ Seção 3 (Goals) presente e preenchida
     ✅ Seção 4 (Non-Goals) presente e preenchida
     ✅ Seção 5 (Usuários) presente e preenchida

============================================================

```
