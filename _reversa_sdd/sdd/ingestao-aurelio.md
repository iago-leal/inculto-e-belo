# Spec: ingestao-aurelio

> Selo 🟡 PLANEJADO. Spec SDD gerada pelo reversa-spec-sdd a partir do prd.md. Todos os itens são hipóteses de projeto, não fatos de código existente.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-07-03
**Reviewers:** iago

---

## 1. Resumo

🟡 Componente de entrada do pipeline: abre o `aurelio_normalized.db` em modo somente-leitura, executa smoke tests de esquema e contagem, e expõe os verbetes como agregados de domínio (`Verbete`) para o componente `conversao-formato`. É a única camada do sistema que conhece SQL; todo o resto do pipeline consome objetos.

---

## 2. Contexto e Motivação

**Problema:**
🟡 O banco é o insumo único do pipeline e vive fora do git (backup no Drive via rclone). Se ele estiver ausente, corrompido ou com esquema divergente do esperado, a conversão produziria um dicionário silenciosamente incompleto — o pior modo de falha para um mantenedor intermitente, que só descobriria meses depois, durante a leitura.

**Evidências:**
🟡 O risco "banco normalizado com defeitos de integridade" consta na seção 8 do PRD com mitigação definida: smoke tests de esquema e contagem na entrada, com falha barulhenta e erro nomeado. Levantamento real do banco em 2026-07-03: 143.376 `entries`, 259.337 `definitions`, 22.168 `locutions`, 175.259 `flexions`, 869.119 `conjugations`.

**Por que agora:**
🟡 Todos os demais componentes dependem do contrato de leitura definido aqui; é o primeiro a implementar no ciclo forward.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Abrir o banco exclusivamente em modo somente-leitura; nenhuma escrita é possível por construção.
- [ ] 🟡 G-02: Validar esquema e contagens contra um manifesto de integridade versionado, antes de qualquer conversão.
- [ ] 🟡 G-03: Expor 100% dos verbetes como agregados `Verbete` completos (definições, exemplos, locuções, notas, regência).
- [ ] 🟡 G-04: Falhar com erro nomeado e mensagem acionável em toda condição anômala.

**Métricas de sucesso:**
| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Verbetes expostos ao pipeline | 0 | 143.376 (100% do manifesto) | na entrega |
| 🟡 Tempo dos smoke tests de entrada | inexistente | < 5 s | na entrega |
| 🟡 Iteração completa dos agregados | inexistente | < 60 s | na entrega |
| 🟡 Escritas possíveis no banco pelo componente | n/a | 0 | contínuo |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Editar, corrigir ou normalizar conteúdo do banco — decisão confirmada pelo usuário em 2026-07-03; o banco é somente-leitura para todo o pipeline.
- 🟡 NG-02: Fazer backup ou restauração do banco — já coberto pelo rclone/Drive, fora deste sistema.
- 🟡 NG-03: Renderizar HTML ou conhecer o formato StarDict — responsabilidade do componente `conversao-formato`.
- 🟡 NG-04: Consultar as tabelas FTS (`fts_entries`, `fts_definitions`) — busca textual não participa da conversão.

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 iago-mantenedor-futuro, executando o pipeline via CLI após meses de pausa, guiado apenas pelo README.
**Usuário secundário:** 🟡 os demais componentes do pipeline, que consomem o contrato `Verbete` sem tocar em SQL.

**Jornada atual (sem a feature):**
🟡 O banco existe, porém nenhum código o valida nem o expõe; qualquer consumo exigiria SQL ad hoc espalhado, acoplado ao esquema.

**Jornada futura (com a feature):**
🟡 O mantenedor roda o pipeline; a ingestão valida o banco em segundos, reporta totais em log estruturado e entrega os agregados ao conversor. Em anomalia, a execução para com erro nomeado que diz exatamente o que restaurar ou investigar.

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID       | Requisito                                                                                                                                                                                                                                                                                             | Prioridade | Critério de Aceite                                                                                                                                                                                     |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 🟡 RF-01 | O sistema deve abrir o banco via URI `file:...?mode=ro`, garantindo impossibilidade estrutural de escrita.                                                                                                                                                                                            | Must       | Dado o banco aberto, quando qualquer escrita é tentada, então `sqlite3.OperationalError` é levantada; teste automatizado comprova.                                                                     |
| 🟡 RF-02 | O sistema deve verificar a existência do arquivo do banco no caminho configurado (config externa, não hardcode) e falhar com `BancoAusenteError` incluindo o caminho esperado e a instrução de restauração via rclone.                                                                                | Must       | Dado caminho inexistente, quando o pipeline inicia, então a execução termina com exit code ≠ 0 e a mensagem contém caminho e comando de restauração.                                                   |
| 🟡 RF-03 | O sistema deve validar a presença das tabelas e colunas requeridas (entries, word_class_blocks, definitions, examples, locutions, locution_definitions, notes, flexions, conjugations, word_classes, rubrics, verb_rection) e falhar com `EsquemaInvalidoError` listando cada divergência encontrada. | Must       | Dado um banco sem a tabela `flexions`, quando os smoke tests rodam, então o erro lista `flexions` como ausente.                                                                                        |
| 🟡 RF-04 | O sistema deve comparar as contagens por tabela com o manifesto de integridade versionado (`manifesto-integridade.json`) e falhar com `ContagemDivergenteError` detalhando tabela, valor esperado e valor obtido.                                                                                     | Must       | Dado manifesto com `entries=143376` e banco com valor distinto, quando os smoke tests rodam, então o erro reporta a divergência exata.                                                                 |
| 🟡 RF-05 | O sistema deve expor um iterador de agregados `Verbete`, cada um contendo entry, blocos de classe gramatical, definições ordenadas por `position`, exemplos, locuções com suas definições, notas e regência verbal, em ordem estável por `sort_key`.                                                  | Must       | Dado o banco íntegro, quando a iteração completa executa, então produz exatamente o total de entries do manifesto, e o verbete de teste `abacaxi` contém suas definições e exemplos na ordem do banco. |
| 🟡 RF-06 | O sistema deve emitir log estruturado (chave=valor) ao fim da validação com os totais por tabela e a duração dos smoke tests.                                                                                                                                                                         | Should     | Dado execução íntegra, quando a validação conclui, então o log contém `entries=143376` e `duracao_ms=` com valor numérico.                                                                             |
| 🟡 RF-07 | O sistema deve expor separadamente iteradores dos pares de flexão (`flexions.entry_head → flexion`) e de conjugação (`conjugations.infinitive → conjugation`) para o componente `indice-de-flexoes`.                                                                                                  | Must       | Dado o banco íntegro, quando os iteradores executam, então produzem 175.259 e 869.119 pares respectivamente.                                                                                           |

### 6.2 Fluxo Principal (Happy Path)

1. O pipeline invoca a ingestão com o caminho do banco vindo da configuração externa.
2. O sistema verifica a existência do arquivo e abre a conexão em modo somente-leitura.
3. O sistema executa os smoke tests de esquema e compara contagens com o manifesto de integridade.
4. O sistema emite log estruturado com totais e duração.
5. O sistema entrega o iterador de agregados `Verbete` e os iteradores de flexões/conjugações ao chamador.
6. Resultado: pipeline segue para a conversão com insumo validado; nenhuma escrita ocorreu no banco.

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Atualização deliberada do banco:**

1. O mantenedor regenera o banco de origem com totais novos.
2. Os smoke tests falham com `ContagemDivergenteError`, apontando o manifesto.
3. O mantenedor atualiza `manifesto-integridade.json` em commit próprio, tornando a mudança explícita e auditável.

---

## 7. Requisitos Não-Funcionais

| ID        | Requisito                        | Valor alvo | Observação                                            |
| --------- | -------------------------------- | ---------- | ----------------------------------------------------- |
| 🟡 RNF-01 | Duração dos smoke tests          | < 5 s      | contagens usam índices existentes                     |
| 🟡 RNF-02 | Iteração completa dos agregados  | < 60 s     | streaming; sem carregar o banco inteiro em memória    |
| 🟡 RNF-03 | Pico de memória na iteração      | < 500 MB   | um agregado por vez, coleções liberadas após consumo  |
| 🟡 RNF-04 | Dependências externas de runtime | 0          | apenas `sqlite3` da biblioteca padrão do Python 3.12+ |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 camada de infraestrutura do pipeline (repositório de leitura); CLI apenas repassa o caminho configurado.

**Comportamento esperado:**
🟡 Interface pública mínima: uma classe de repositório com métodos de validação (`validar()`), iteração de verbetes (`verbetes()`) e iteração de formas (`flexoes()`, `conjugacoes()`). O chamador nunca vê SQL, cursores ou nomes de tabela.

**Estados da UI:**

- Estado vazio: n/a — componente sem UI; interface é a API interna mais logs.
- Estado de carregamento: log de início com caminho do banco.
- Estado de erro: exceção nomeada propagada; CLI converte em mensagem e exit code ≠ 0.
- Estado de sucesso: log estruturado com totais e duração.

---

## 9. Modelo de Dados

**Entidades novas ou modificadas:**

```
Verbete {
  id: int                     // entries.id
  lemma: str                  // forma canônica
  lemma_stylized: str|None    // grafia estilizada para exibição
  homonym: int|None           // número do homônimo (1, 2, …)
  ipa: str|None               // pronúncia
  etymology_html: str|None    // etimologia com marcação
  blocos: lista de BlocoClasse    // classe gramatical + definições ordenadas
  locucoes: lista de Locucao      // expressões + definições
  notas: lista de Nota            // notas do verbete
  regencias: lista de Regencia    // verb_rection
  sort_key: str               // ordenação estável
}
```

**Migrações necessárias:** Não — o banco de origem permanece intocado; nenhum dado novo é persistido por este componente.

---

## 10. Integrações e Dependências

| Dependência                                         | Tipo        | Impacto se indisponível                                                      |
| --------------------------------------------------- | ----------- | ---------------------------------------------------------------------------- |
| 🟡 `aurelio_normalized.db` local                    | Obrigatória | Falha imediata com `BancoAusenteError` e instrução de restauração via rclone |
| 🟡 `sqlite3` (stdlib Python)                        | Obrigatória | Inexistente na prática; presente em toda instalação CPython                  |
| 🟡 `manifesto-integridade.json` (versionado no git) | Obrigatória | Falha com erro nomeado orientando a regenerar o manifesto                    |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário                                              | Trigger                                                        | Comportamento esperado                                                                                |
| ---------------------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| 🟡 EC-01: Banco ausente                              | Arquivo não existe no caminho configurado                      | `BancoAusenteError` com caminho e comando de restauração; exit code ≠ 0                               |
| 🟡 EC-02: Banco bloqueado ou WAL órfão               | Outro processo segura lock; falha de abertura                  | Erro nomeado `BancoIndisponivelError` sugerindo fechar o processo concorrente; sem retry silencioso   |
| 🟡 EC-03: Esquema divergente                         | Tabela ou coluna requerida ausente                             | `EsquemaInvalidoError` listando todas as divergências de uma vez, não só a primeira                   |
| 🟡 EC-04: Contagem divergente                        | Total de tabela difere do manifesto                            | `ContagemDivergenteError` com tabela, esperado e obtido; orienta fluxo de atualização deliberada      |
| 🟡 EC-05: Referência órfã no agregado                | `definitions` apontando a bloco inexistente durante a iteração | Falha barulhenta com id do registro problemático; nunca produz verbete parcial em silêncio            |
| 🟡 EC-06: Arquivo presente com 0 bytes ou corrompido | Cópia truncada ou restauração com falha                        | `sqlite3.DatabaseError` capturada e reembalada em `BancoCorrompidoError` com instrução de restauração |

---

## 12. Segurança e Privacidade

- **Autenticação:** n/a — execução local pelo próprio mantenedor.
- **Autorização:** n/a — arquivo local com permissões do usuário.
- **Dados sensíveis:** conteúdo do Aurélio sob direitos autorais; uso estritamente pessoal; o componente não expõe dados fora do processo. Sem PII.
- **Auditoria:** log estruturado por execução com totais validados; suficiente para diagnóstico retrospectivo.

---

## 13. Plano de Rollout

- **Estratégia:** componente de build local; entra em uso quando o pipeline o invoca. Sem usuários externos, sem feature flag.
- **Como reverter (rollback):** `git revert` do commit; o banco de origem nunca é alterado, então não há estado a desfazer.
- **Monitoramento pós-deploy:** observar os logs das primeiras execuções completas do pipeline; a suíte de testes cobre os erros nomeados.

---

## 14. Open Questions

| #        | Pergunta                                                                                                                    | Impacto | Dono | Prazo                 |
| -------- | --------------------------------------------------------------------------------------------------------------------------- | ------- | ---- | --------------------- |
| 🟡 OQ-01 | O manifesto de integridade deve registrar, além das contagens, um hash por tabela para detectar mutação com contagem igual? | Baixo   | iago | antes do reversa-plan |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão                                  | Alternativas consideradas                        | Racional                                                                                            |
| ---------------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| Abertura via URI `mode=ro`               | Confiar em disciplina de código (só SELECTs)     | Garantia estrutural vence convenção; escrita torna-se impossível, não apenas proibida               |
| Manifesto de contagens versionado no git | Contagens hardcoded no código; nenhuma validação | Atualização do banco vira mudança explícita e auditável em commit próprio                           |
| Iteração por streaming                   | Carregar tudo em memória                         | 143k agregados com filhos estouram memória em dispositivos modestos; streaming mantém pico < 500 MB |
| Erros nomeados por condição              | Exceção genérica com mensagem                    | Logs e testes referenciam classes; falha barulhenta e diagnosticável é requisito do PRD             |

---

## Apêndice

### Referências

- prd.md (seções 6, 7 e 8) e ideation.md em `_reversa_sdd/`
- Esquema real levantado do banco em 2026-07-03 (sessão de specs)

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
  Arquivo: _reversa_sdd/sdd/ingestao-aurelio.md
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
