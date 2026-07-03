# Spec: conversao-formato

> Selo 🟡 PLANEJADO. Spec SDD gerada pelo reversa-spec-sdd a partir do prd.md. Todos os itens são hipóteses de projeto, não fatos de código existente.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-07-03
**Reviewers:** iago

---

## 1. Resumo

🟡 Núcleo do pipeline: recebe os agregados `Verbete` da ingestão, renderiza cada lema como artigo HTML e gera o dicionário no formato StarDict (`.ifo`, `.idx`, `.dict.dz`, `.syn`) via PyGlossary pinado — o formato que o KOReader lê nativamente em todos os dispositivos do usuário.

---

## 2. Contexto e Motivação

**Problema:**
🟡 O Aurélio normalizado está preso em SQLite, formato que nenhum leitor de e-books consome. O KOReader aceita dicionários StarDict; sem esta conversão, os 143.376 verbetes permanecem inacessíveis no momento da leitura.

**Evidências:**
🟡 Verificação de 2026-07-03: o wiki oficial do KOReader confirma StarDict como formato nativo (`*.ifo`, `*.idx`, `*.dict`/`*.dict.dz`); o PyGlossary 5.4.1 está ativo e trata as armadilhas do formato (ordenação do `.idx`, offsets, dictzip). Decisão do usuário na mesma data: dependência PyGlossary pinada em vez de writer próprio.

**Por que agora:**
🟡 É a entrega central do PRD; ingestão e validação existem em função dela.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Gerar artefato StarDict completo e instalável, contendo 100% dos verbetes do banco (143.376 entries agrupados por lema).
- [ ] 🟡 G-02: Preservar a riqueza do verbete: classe gramatical, pronúncia, etimologia, definições numeradas, exemplos, locuções, notas e regência verbal.
- [ ] 🟡 G-03: Produzir saída com ordem estável e reproduzível: duas execuções sobre o mesmo banco geram o mesmo conjunto de headwords e artigos.
- [ ] 🟡 G-04: Concluir a conversão completa em tempo de build aceitável para uso pessoal.

**Métricas de sucesso:**
| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Entries representados no artefato | 0 | 143.376 (100%) | na entrega |
| 🟡 Duração da conversão completa | inexistente | < 10 min | na entrega |
| 🟡 Latência do lookup no dispositivo (toque → verbete) | n/a | < 1 s | na entrega |
| 🟡 Pico de memória do processo de conversão | n/a | < 2 GB | na entrega |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Gerar formatos além de StarDict (MDX, Kobo dicthtml, EPUB) — ciclos futuros, se surgirem outros leitores.
- 🟡 NG-02: Escrever código Lua ou plugin para o KOReader — restrição técnica do PRD; consumimos apenas o que o leitor já lê.
- 🟡 NG-03: Construir o índice de formas flexionadas — responsabilidade do componente `indice-de-flexoes`, que alimenta o `.syn` desta mesma geração.
- 🟡 NG-04: Validar o artefato gerado — responsabilidade do componente `validacao-paridade`, deliberadamente independente do conversor.

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 iago-leitor, que toca numa palavra no KOReader e recebe o verbete do Aurélio no popup, offline.
**Usuário secundário:** 🟡 iago-mantenedor-futuro, que regenera o artefato após atualizar o banco ou o pipeline.

**Jornada atual (sem a feature):**
🟡 O leitor toca numa palavra e recebe verbete truncado de dicionário StarDict de origem duvidosa, ou nenhum resultado; o Aurélio fica no desktop, fora do fluxo de leitura.

**Jornada futura (com a feature):**
🟡 O mantenedor roda o pipeline uma vez; o artefato instalado em cada dispositivo responde ao toque com o verbete completo do Aurélio em menos de 1 segundo, sem rede.

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID       | Requisito                                                                                                                                                                                                                                                                                      | Prioridade | Critério de Aceite                                                                                                                                                  |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🟡 RF-01 | O sistema deve agrupar entries homônimos (mesmo `lemma`) num único artigo por headword, com seções numeradas na ordem do campo `homonym` e, na ausência dele, na ordem de `sort_key`.                                                                                                          | Must       | Dado o lema `a` (5 entries no banco), quando o artigo é gerado, então contém as 5 seções numeradas num único headword.                                              |
| 🟡 RF-02 | O sistema deve renderizar cada artigo em HTML autocontido (sem CSS externo, sem imagens, sem scripts), incluindo: lema estilizado, classe gramatical, pronúncia IPA quando presente, etimologia, definições numeradas com rubrica, exemplos, locuções com definições, notas e regência verbal. | Must       | Dado o verbete de teste `abacaxi`, quando renderizado, então o HTML contém todas as definições e exemplos presentes no banco, na mesma ordem.                       |
| 🟡 RF-03 | O sistema deve gerar o artefato via PyGlossary 5.4.1 (versão exata pinada no lock file) no formato StarDict com `sametypesequence=h` e compressão dictzip (`.dict.dz`).                                                                                                                        | Must       | Dado o build concluído, quando o diretório de saída é inspecionado, então contém `.ifo`, `.idx`, `.dict.dz` e `.syn`, e o `.ifo` declara `sametypesequence=h`.      |
| 🟡 RF-04 | O sistema deve preencher os metadados do `.ifo`: `bookname` "Aurélio (uso pessoal)", `date` da geração, `wordcount` e `synwordcount` coerentes com os totais reais gravados.                                                                                                                   | Must       | Dado o build concluído, quando o `.ifo` é lido, então `wordcount` é igual ao número de headwords únicos gravados.                                                   |
| 🟡 RF-05 | O sistema deve escrever o artefato de forma atômica: gerar em diretório temporário e mover para `dist/aurelio-stardict/` somente após conclusão íntegra.                                                                                                                                       | Must       | Dado um build interrompido no meio, quando o processo morre, então `dist/aurelio-stardict/` permanece na versão anterior, sem arquivos parciais.                    |
| 🟡 RF-06 | O sistema deve receber do componente `indice-de-flexoes` o mapeamento forma→headword e repassá-lo ao PyGlossary para materializar o `.syn` na mesma geração.                                                                                                                                   | Must       | Dado o mapeamento com N formas válidas, quando o build conclui, então `synwordcount` no `.ifo` é igual a N.                                                         |
| 🟡 RF-07 | O sistema deve emitir log estruturado ao fim do build: headwords gravados, sinônimos gravados, duração e tamanho de cada arquivo gerado.                                                                                                                                                       | Should     | Dado build íntegro, quando conclui, então o log contém `headwords=`, `sinonimos=`, `duracao_s=` e `bytes_dict=` com valores numéricos.                              |
| 🟡 RF-08 | O sistema deve manter a ordenação de headwords delegada ao PyGlossary (regra de ordenação do formato StarDict), sem reimplementação própria.                                                                                                                                                   | Must       | Dado o `.idx` gerado, quando lido pelo leitor independente da validação, então a ordem satisfaz a regra do formato e o lookup binário encontra headword arbitrário. |

### 6.2 Fluxo Principal (Happy Path)

1. O pipeline entrega à conversão o iterador de agregados `Verbete` e o mapeamento de flexões.
2. O sistema agrupa os agregados por lema, fundindo homônimos em artigo único.
3. O sistema renderiza cada artigo em HTML autocontido e o adiciona ao glossário em memória do PyGlossary.
4. O sistema registra os sinônimos (forma→headword) no glossário.
5. O sistema invoca a escrita StarDict com dictzip em diretório temporário.
6. O sistema move o resultado para `dist/aurelio-stardict/` e emite o log estruturado de build.
7. Resultado: artefato completo pronto para a validação de paridade.

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Regeneração sobre artefato existente:**

1. O mantenedor roda o build com `dist/aurelio-stardict/` já povoado pela versão anterior.
2. O sistema gera a nova versão no diretório temporário e substitui a antiga numa única operação de rename.

---

## 7. Requisitos Não-Funcionais

| ID        | Requisito                     | Valor alvo                                     | Observação                                                                    |
| --------- | ----------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------- |
| 🟡 RNF-01 | Duração da conversão completa | < 10 min                                       | hardware do mantenedor (MacBook)                                              |
| 🟡 RNF-02 | Pico de memória               | < 2 GB                                         | atenção: o modelo de escrita do PyGlossary pode exigir o glossário em memória |
| 🟡 RNF-03 | Tamanho do artefato final     | < 250 MB                                       | precisa caber em Kindle com armazenamento modesto                             |
| 🟡 RNF-04 | Compatibilidade               | KOReader (versão testada registrada no README) | mitigação do risco de mudança de formato                                      |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 camada de aplicação (orquestração do build) e camada de infraestrutura (adaptador PyGlossary). A regra de renderização HTML é domínio puro, testável sem PyGlossary.

**Comportamento esperado:**
🟡 Três papéis separados: um renderizador (`Verbete` → HTML, função pura), um adaptador de glossário (encapsula PyGlossary atrás de interface própria, único ponto de acoplamento à biblioteca) e um orquestrador de build (streaming dos agregados, escrita atômica, log). Trocar o PyGlossary no futuro altera apenas o adaptador.

**Estados da UI:**

- Estado vazio: n/a — componente sem UI própria.
- Estado de carregamento: log de progresso a cada 10.000 verbetes renderizados.
- Estado de erro: exceção nomeada; diretório final intocado.
- Estado de sucesso: log estruturado de build com totais e tamanhos.

---

## 9. Modelo de Dados

**Entidades novas ou modificadas:**

```
ArtigoStarDict {
  headword: str            // lemma canônico, com diacríticos
  html: str                // artigo autocontido renderizado
}

ResultadoBuild {
  headwords: int           // total de artigos gravados
  sinonimos: int           // total de entradas .syn
  duracao_s: float
  arquivos: mapa nome→bytes    // um item por arquivo gerado
}
```

**Migrações necessárias:** Não — a saída é um diretório de artefatos regenerável; nada de banco.

---

## 10. Integrações e Dependências

| Dependência                              | Tipo        | Impacto se indisponível                                                                             |
| ---------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------- |
| 🟡 PyGlossary 5.4.1 (pinada, build-time) | Obrigatória | Build falha na importação com erro nomeado orientando `pip install` a partir do lock file           |
| 🟡 Componente `ingestao-aurelio`         | Obrigatória | Sem agregados validados o build nem inicia                                                          |
| 🟡 Componente `indice-de-flexoes`        | Obrigatória | Sem mapeamento, build falha com erro nomeado — artefato sem `.syn` violaria o alvo de flexões       |
| 🟡 dictzip (embutido/na dependência)     | Obrigatória | Falha nomeada; sem fallback para `.dict` sem compressão, para não gerar artefato divergente do spec |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário                                           | Trigger                                     | Comportamento esperado                                                                                                                                 |
| ------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 🟡 EC-01: HTML de origem malformado               | `content_html` com tag não fechada no banco | Renderizador aplica saneamento estrutural (fechamento de tags via parser tolerante) e registra o id do verbete no log; nunca corrompe o artigo vizinho |
| 🟡 EC-02: Lema vazio ou apenas espaços            | Registro anômalo em `entries`               | Falha barulhenta com id do registro; indica correção do manifesto/banco em vez de pular em silêncio                                                    |
| 🟡 EC-03: Falha interna do PyGlossary             | Exceção da biblioteca durante escrita       | Capturada e reembalada em `FalhaGeracaoError` com contexto; diretório final intocado pela escrita atômica                                              |
| 🟡 EC-04: Disco cheio durante o build             | Sem espaço no diretório temporário          | Erro claro com bytes livres e necessários; artefato anterior preservado                                                                                |
| 🟡 EC-05: Artigo excede tamanho plausível         | HTML renderizado > 1 MB para um único lema  | Log de advertência com lema e tamanho; build prossegue (verbetes longos são legítimos no Aurélio)                                                      |
| 🟡 EC-06: Interrupção do processo (Ctrl-C, queda) | Sinal durante a escrita                     | Diretório temporário descartado na próxima execução; `dist/` permanece íntegro                                                                         |

---

## 12. Segurança e Privacidade

- **Autenticação:** n/a — build local.
- **Autorização:** n/a.
- **Dados sensíveis:** conteúdo sob direitos autorais do Aurélio; o artefato é para uso estritamente pessoal e não deve ser publicado — restrição herdada pelo componente `distribuicao-webdav`.
- **Auditoria:** log de build por execução com totais; `ResultadoBuild` persiste no relatório da validação de paridade.

---

## 13. Plano de Rollout

- **Estratégia:** build local sob demanda; a primeira geração validada é instalada manualmente num dispositivo para o spike de flexões antes de qualquer distribuição.
- **Como reverter (rollback):** restaurar a versão anterior do artefato (mantida pelo componente de distribuição); `git revert` para o código.
- **Monitoramento pós-deploy:** conferir latência de lookup e renderização do popup no dispositivo mais modesto (e-ink) nas primeiras sessões de leitura.

---

## 14. Open Questions

| #        | Pergunta                                                                                                                                                 | Impacto | Dono | Prazo                        |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ---- | ---------------------------- |
| 🟡 OQ-01 | O modo de escrita do PyGlossary comporta streaming ou exige o glossário inteiro em memória? Define se RNF-02 (< 2 GB) precisa de estratégia de chunking. | Médio   | iago | spike, antes do reversa-plan |
| 🟡 OQ-02 | Qual subconjunto de HTML/CSS inline o popup do KOReader renderiza bem em e-ink (negrito, itálico, listas)? Define o vocabulário do renderizador.         | Médio   | iago | spike, antes do reversa-plan |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão                                           | Alternativas consideradas                        | Racional                                                                                                                                                                                                     |
| ------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PyGlossary 5.4.1 pinado como dependência de build | Writer StarDict próprio (~300 linhas, zero deps) | Decisão do usuário em 2026-07-03: a biblioteca já resolve ordenação do `.idx`, offsets e dictzip; menos código próprio para o mantenedor intermitente; risco coberto pela validação de paridade independente |
| Formato StarDict com `sametypesequence=h`         | Texto puro (`m`); Kobo dicthtml                  | Único formato nativo do KOReader; HTML preserva a estrutura rica do verbete                                                                                                                                  |
| Homônimos fundidos num artigo por lema            | Um artigo por entry (headwords repetidos)        | Popup único e completo no toque; headwords repetidos têm comportamento imprevisível entre leitores                                                                                                           |
| Acoplamento ao PyGlossary isolado em adaptador    | Uso direto da API pela regra de negócio          | Baixo acoplamento exigido pelos princípios do usuário; troca futura da ferramenta fica local                                                                                                                 |

---

## Apêndice

### Referências

- prd.md (seções 4, 6 e 8) em `_reversa_sdd/`
- https://github.com/koreader/koreader/wiki/Dictionary-support
- https://github.com/ilius/pyglossary (release 5.4.1)

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
  Arquivo: _reversa_sdd/sdd/conversao-formato.md
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
