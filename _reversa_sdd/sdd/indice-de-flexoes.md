# Spec: indice-de-flexoes

> Selo 🟡 PLANEJADO. Spec SDD gerada pelo reversa-spec-sdd a partir do prd.md. Todos os itens são hipóteses de projeto, não fatos de código existente.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-07-03
**Reviewers:** iago

---

## 1. Resumo

🟡 Constrói o mapeamento forma flexionada → headword que materializa o arquivo `.syn` do dicionário StarDict, usando exclusivamente as tabelas `flexions` (175.259 formas) e `conjugations` (869.119 formas) já presentes no banco. É o componente que faz o long-press em "cantávamos" abrir o verbete "cantar".

---

## 2. Contexto e Motivação

**Problema:**
🟡 O leitor toca em palavras como aparecem no texto — plurais, femininos, verbos conjugados. O formato StarDict indexa por headword exato; sem um índice de formas, a maioria dos toques em texto real retornaria vazio, quebrando a promessa central do produto.

**Evidências:**
🟡 O PRD marca o lookup de flexionadas como premissa de maior risco. Levantamento de 2026-07-03 reduziu esse risco: o próprio banco traz as formas prontas, com ligação quase perfeita aos verbetes (12.535 dos 12.546 infinitivos e 111.544 das 111.555 cabeças de flexão casam com `entries.lemma`). O mecanismo `.syn` é a via estabelecida para flexões em dicionários StarDict consumidos pelo KOReader.

**Por que agora:**
🟡 O `.syn` é gravado na mesma geração do artefato; este componente precisa existir antes do primeiro build completo. O spike que valida o comportamento no KOReader é a primeira tarefa do ciclo forward.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Mapear 100% das formas das tabelas `flexions` e `conjugations` cujo lema exista no dicionário — alvo quantitativo confirmado pelo usuário em 2026-07-03.
- [ ] 🟡 G-02: Produzir mapeamento deduplicado e determinístico: mesma entrada, mesmo resultado.
- [ ] 🟡 G-03: Registrar em relatório todas as formas descartadas e o motivo (órfã, duplicada, idêntica ao headword).
- [ ] 🟡 G-04: Validar cedo, com spike em dispositivo real, que o KOReader resolve formas via `.syn` no artefato gerado.

**Métricas de sucesso:**
| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Formas com lema existente presentes no `.syn` | 0 | 100% | na entrega |
| 🟡 Formas de entrada processadas (flexions + conjugations) | 0 | 1.044.378 (total das duas tabelas) | na entrega |
| 🟡 Palavras flexionadas do roteiro de spike resolvidas no KOReader | 0 | 20 de 20 | spike, antes do build final |
| 🟡 Duração da construção do mapeamento | inexistente | < 2 min | na entrega |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Gerar flexões por algoritmo morfológico próprio ou fonte externa (Hunspell, MorphoBr) — as tabelas do banco são a fonte única nesta entrega.
- 🟡 NG-02: Corrigir as 22 formas órfãs no banco (11 infinitivos + 11 cabeças sem verbete correspondente) — o banco é somente-leitura; órfãs são reportadas, não consertadas.
- 🟡 NG-03: Desambiguação semântica de forma ambígua — quando uma forma flexiona dois lemas distintos, ambos os destinos entram no `.syn`; a escolha fica com o leitor no popup.
- 🟡 NG-04: Escrever o arquivo `.syn` diretamente — a serialização é do componente `conversao-formato` via PyGlossary; aqui se produz apenas o mapeamento.

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 iago-leitor, tocando em palavras flexionadas durante leitura literária — o caso majoritário em texto real.
**Usuário secundário:** 🟡 iago-mantenedor-futuro, lendo o relatório de descartes para auditar a cobertura após regenerar o banco.

**Jornada atual (sem a feature):**
🟡 O toque em "disse" ou "árvores" não encontra headword exato e o popup retorna vazio ou aproximações erradas; o leitor abandona a consulta.

**Jornada futura (com a feature):**
🟡 O toque em qualquer forma presente nas tabelas do banco abre o verbete do lema correspondente, na mesma latência do lookup exato.

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID       | Requisito                                                                                                                                                                                                                         | Prioridade | Critério de Aceite                                                                                                                                                                   |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 🟡 RF-01 | O sistema deve consumir os iteradores de pares fornecidos pela ingestão: (`entry_head`, `flexion`) de `flexions` e (`infinitive`, `conjugation`) de `conjugations`.                                                               | Must       | Dado o banco íntegro, quando o componente executa, então processa 175.259 + 869.119 pares de entrada, totais registrados no relatório.                                               |
| 🟡 RF-02 | O sistema deve resolver cada lema-alvo ao headword do artigo correspondente (o lema fundido de homônimos do componente `conversao-formato`), descartando como órfã a forma cujo lema não exista em `entries.lemma`.               | Must       | Dado o levantamento atual, quando a resolução executa, então exatamente as formas dos 11 infinitivos e 11 cabeças órfãos são descartadas com motivo `orfa`.                          |
| 🟡 RF-03 | O sistema deve deduplicar o mapeamento: pares (forma, headword) repetidos entram uma única vez.                                                                                                                                   | Must       | Dado que `flexions` e `conjugations` contêm a mesma forma para o mesmo lema, quando o mapeamento conclui, então o par aparece uma única vez e o descarte é contado como `duplicada`. |
| 🟡 RF-04 | O sistema deve descartar a forma idêntica ao próprio headword (comparação exata, sensível a diacríticos), contando o descarte como `identica`.                                                                                    | Must       | Dado um par (forma=lema), quando processado, então não entra no `.syn` e incrementa o contador `identica`.                                                                           |
| 🟡 RF-05 | O sistema deve preservar forma ambígua apontando a N headwords distintos como N entradas do mapeamento.                                                                                                                           | Must       | Dada uma forma ligada a dois lemas existentes, quando o mapeamento conclui, então contém as duas entradas.                                                                           |
| 🟡 RF-06 | O sistema deve emitir relatório estruturado (JSON) com: formas de entrada por tabela, entradas gravadas, descartes por motivo (`orfa`, `duplicada`, `identica`) e a lista completa das órfãs.                                     | Must       | Dado o build concluído, quando o relatório é lido, então entrada = gravadas + soma dos descartes, e as órfãs estão listadas nominalmente.                                            |
| 🟡 RF-07 | O usuário deve poder executar o roteiro de spike documentado: artefato reduzido ou completo instalado num dispositivo real, com lista fixa de 20 palavras flexionadas (10 nominais, 10 verbais) e resultado esperado por palavra. | Must       | Dado o roteiro executado no KOReader, quando as 20 palavras são tocadas, então cada uma abre o verbete do lema esperado.                                                             |

### 6.2 Fluxo Principal (Happy Path)

1. O pipeline entrega os iteradores de pares de flexão e conjugação ao componente.
2. O sistema resolve cada lema-alvo ao headword do artigo, classificando órfãs.
3. O sistema deduplica pares e descarta formas idênticas ao headword.
4. O sistema entrega o mapeamento final ao componente `conversao-formato`.
5. O sistema grava o relatório JSON de cobertura e descartes.
6. Resultado: `.syn` materializado no build com 100% das formas válidas e auditoria completa dos descartes.

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Spike de validação da premissa:**

1. O mantenedor gera um artefato mínimo (subconjunto de verbetes + suas formas).
2. O mantenedor instala no dispositivo e percorre o roteiro de 20 palavras.
3. Resultado positivo destrava o build completo; resultado negativo reabre a decisão de formato antes de qualquer outro investimento.

---

## 7. Requisitos Não-Funcionais

| ID        | Requisito                           | Valor alvo                          | Observação                                           |
| --------- | ----------------------------------- | ----------------------------------- | ---------------------------------------------------- |
| 🟡 RNF-01 | Duração da construção do mapeamento | < 2 min                             | ~1M de pares; dicionário em memória é suficiente     |
| 🟡 RNF-02 | Pico de memória                     | < 1 GB                              | mapeamento de ~1M strings curtas                     |
| 🟡 RNF-03 | Determinismo                        | 2 execuções → mapeamentos idênticos | ordenação estável antes da entrega ao conversor      |
| 🟡 RNF-04 | Dependências externas próprias      | 0                                   | domínio puro; consome iteradores e devolve estrutura |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 camada de domínio (regra de construção do mapeamento, pura e testável isoladamente) e o contrato com `conversao-formato` (estrutura `MapaFlexoes`).

**Comportamento esperado:**
🟡 Função de domínio que recebe os pares e o conjunto de headwords válidos, devolve `MapaFlexoes` mais `RelatorioCobertura`. Sem I/O interno: leitura vem da ingestão, escrita do relatório fica na borda do pipeline. Testes de unidade cobrem cada regra de descarte com fixtures mínimas.

**Estados da UI:**

- Estado vazio: n/a — componente sem UI.
- Estado de carregamento: log de progresso a cada 100.000 pares processados.
- Estado de erro: exceção nomeada propagada ao pipeline.
- Estado de sucesso: relatório JSON gravado e totais no log estruturado.

---

## 9. Modelo de Dados

**Entidades novas ou modificadas:**

```
MapaFlexoes {
  entradas: list[(forma: str, headword: str)]   // deduplicado, ordenado
}

RelatorioCobertura {
  entrada_flexions: int        // 175.259 no banco atual
  entrada_conjugations: int    // 869.119 no banco atual
  gravadas: int
  descartes: {orfa: int, duplicada: int, identica: int}
  orfas: list[str]             // lemas sem verbete, nominalmente
}
```

**Migrações necessárias:** Não — estruturas em memória mais relatório JSON regenerável.

---

## 10. Integrações e Dependências

| Dependência                                            | Tipo                     | Impacto se indisponível                                                                                         |
| ------------------------------------------------------ | ------------------------ | --------------------------------------------------------------------------------------------------------------- |
| 🟡 Componente `ingestao-aurelio` (iteradores de pares) | Obrigatória              | Sem pares validados o componente nem executa                                                                    |
| 🟡 Conjunto de headwords do `conversao-formato`        | Obrigatória              | Resolução de lema→headword falha com erro nomeado                                                               |
| 🟡 KOReader em dispositivo real (spike)                | Obrigatória para o spike | Sem dispositivo disponível o spike usa o emulador desktop do KOReader como aproximação, registrando a limitação |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário                                              | Trigger                                                                           | Comportamento esperado                                                                                                              |
| ---------------------------------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 🟡 EC-01: Forma órfã                                 | Lema da forma inexiste em `entries.lemma`                                         | Descarte contado e listado nominalmente no relatório; execução prossegue                                                            |
| 🟡 EC-02: Forma ambígua                              | Mesma forma flexiona 2+ lemas existentes                                          | Todas as entradas preservadas no mapeamento (RF-05); nenhum descarte                                                                |
| 🟡 EC-03: Forma colide com headword de outro verbete | Forma flexionada é também lema próprio (ex.: substantivo homógrafo de conjugação) | Entrada do `.syn` mantida; o lookup exato do headword tem precedência natural no leitor, e o popup lista as demais correspondências |
| 🟡 EC-04: Forma vazia ou com apenas espaços          | Registro anômalo nas tabelas de origem                                            | Falha barulhenta com id do registro; indica investigação do banco, sem descarte silencioso                                          |
| 🟡 EC-05: Explosão de volume no `.syn`               | Comportamento lento do KOReader com ~1M de sinônimos                              | Cenário coberto pelo spike (OQ-01); critério de fallback definido lá antes do build completo                                        |
| 🟡 EC-06: Divergência de diacríticos                 | Forma difere do lema só por acento (colisão de slug)                              | Comparação de identidade é exata (RF-04); slugs não participam da igualdade, evitando descartes indevidos                           |

---

## 12. Segurança e Privacidade

- **Autenticação:** n/a — build local.
- **Autorização:** n/a.
- **Dados sensíveis:** as formas derivam do conteúdo do Aurélio; herdam a restrição de uso pessoal do artefato. Sem PII.
- **Auditoria:** relatório JSON por build é o registro de cobertura; versões sucessivas permitem comparar regressões de cobertura.

---

## 13. Plano de Rollout

- **Estratégia:** spike primeiro (roteiro de 20 palavras em dispositivo real), build completo depois — o spike é o gate que destrava o restante do investimento.
- **Como reverter (rollback):** artefato anterior preservado pelo componente de distribuição; código via `git revert`.
- **Monitoramento pós-deploy:** durante as primeiras leituras reais, anotar palavras tocadas sem resultado; a lista alimenta o backlog de cobertura de ciclo futuro.

---

## 14. Open Questions

| #        | Pergunta                                                                                                                      | Impacto | Dono | Prazo                          |
| -------- | ----------------------------------------------------------------------------------------------------------------------------- | ------- | ---- | ------------------------------ |
| 🟡 OQ-01 | O KOReader mantém latência < 1 s com `.syn` de ~1M de entradas em e-ink modesto?                                              | Alto    | iago | spike, antes do build completo |
| 🟡 OQ-02 | O lookup do KOReader normaliza caixa/diacríticos antes de consultar o `.syn` (afeta formas capitalizadas em início de frase)? | Médio   | iago | spike, antes do build completo |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão                                                   | Alternativas consideradas                             | Racional                                                                                                                             |
| --------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Fonte única: tabelas `flexions` + `conjugations` do banco | Hunspell pt_BR; MorphoBr; gerador morfológico próprio | Dados já existem, ligados aos verbetes reais (99,9% de casamento); zero dependência externa e zero manutenção de regras morfológicas |
| Alvo de 100% das formas válidas                           | Amostra estatística; sem alvo formal                  | Decisão do usuário em 2026-07-03; único alvo plenamente verificável por contagem                                                     |
| Órfãs reportadas, nunca corrigidas                        | Consertar o banco durante o build                     | Banco somente-leitura por decisão explícita; correção silenciosa esconderia defeito do insumo                                        |
| Mapeamento como domínio puro sem I/O                      | Componente ler o banco diretamente                    | Testabilidade com fixtures mínimas; coesão funcional e baixo acoplamento exigidos pelos princípios do projeto                        |

---

## Apêndice

### Referências

- prd.md (seções 4, 8 e pendências) em `_reversa_sdd/`
- Levantamento das tabelas `flexions` e `conjugations` em 2026-07-03 (sessão de specs)
- https://koreader.rocks/doc/modules/koplugin.japanese.html (sinônimos como via para formas flexionadas)

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
  Arquivo: _reversa_sdd/sdd/indice-de-flexoes.md
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
