# Spec: distribuicao-webdav

> Selo 🟡 PLANEJADO. Spec SDD gerada pelo reversa-spec-sdd a partir do prd.md. Todos os itens são hipóteses de projeto, não fatos de código existente.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-07-03
**Reviewers:** iago

---

## 1. Resumo

🟡 Último elo do pipeline: empacota o artefato aprovado pela validação de paridade, publica no WebDAV privado da VPS já existente (infra do projeto `koreader-notas`) e define o procedimento documentado de instalação e atualização em cada dispositivo com KOReader, com fallback manual quando a rede falta.

---

## 2. Contexto e Motivação

**Problema:**
🟡 O dicionário precisa existir, idêntico, em todos os dispositivos do usuário. Sem canal único de distribuição, cada atualização viraria cópia manual repetida por dispositivo — exatamente o atrito que o PRD lista como agravante do problema.

**Evidências:**
🟡 O PRD define como critério de aceite: artefato publicado no WebDAV, com cada dispositivo capaz de baixá-lo e atualizá-lo pelo procedimento documentado. A VPS com WebDAV já opera para sincronização do KOReader (kosync/estatísticas), com custo zero adicional.

**Por que agora:**
🟡 Fecha o ciclo da primeira entrega: sem distribuição, o artefato validado permanece no desktop, e a promessa multi-dispositivo fica por cumprir.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Publicar o artefato aprovado com um único comando, com verificação de integridade pós-upload.
- [ ] 🟡 G-02: Manter versionamento simples com checksum, permitindo voltar à versão anterior a qualquer momento.
- [ ] 🟡 G-03: Documentar procedimento de instalação/atualização por dispositivo executável em menos de 5 minutos.
- [ ] 🟡 G-04: Garantir fallback documentado de instalação sem rede (cópia local via USB).

**Métricas de sucesso:**
| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Comandos para publicar uma versão nova | inexistente | 1 | na entrega |
| 🟡 Tempo de instalação por dispositivo (procedimento documentado) | inexistente | < 5 min | na entrega |
| 🟡 Versões anteriores recuperáveis no WebDAV | 0 | ≥ 2 | contínuo |
| 🟡 Uploads com checksum conferido pós-publicação | n/a | 100% | contínuo |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Distribuição pública ou a terceiros — o WebDAV é privado e autenticado; restrição de direitos autorais do PRD.
- 🟡 NG-02: Atualização automática nos dispositivos (daemon, agendador ou plugin no KOReader) — o gatilho de atualização é humano nesta entrega.
- 🟡 NG-03: Provisionar ou administrar a VPS e o servidor WebDAV — infraestrutura existente do projeto `koreader-notas`; reutilizar, não construir.
- 🟡 NG-04: Sincronizar outros conteúdos (livros, notas, estatísticas) — escopo restrito ao artefato do dicionário.

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 iago-mantenedor-futuro, publicando uma versão nova após regenerar o artefato.
**Usuário secundário:** 🟡 iago-leitor, atualizando o dicionário num dispositivo seguindo o procedimento do README.

**Jornada atual (sem a feature):**
🟡 O artefato validado fica no desktop; levá-lo a cada dispositivo exige cabo, gerenciador de arquivos e memória do caminho certo — atrito que desestimula atualizações.

**Jornada futura (com a feature):**
🟡 O mantenedor roda o comando de publicação uma vez; em cada dispositivo, o leitor baixa e extrai o pacote pelo procedimento de 5 minutos, ou copia via USB quando offline.

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID       | Requisito                                                                                                                                                                                                           | Prioridade | Critério de Aceite                                                                                                                          |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 🟡 RF-01 | O sistema deve recusar a publicação quando o `parity-report.json` correspondente ao artefato estiver ausente ou com veredito reprovado.                                                                             | Must       | Dado relatório reprovado, quando a publicação é invocada, então termina com exit code ≠ 0 e mensagem citando o gate de paridade.            |
| 🟡 RF-02 | O sistema deve empacotar `dist/aurelio-stardict/` em `aurelio-stardict-vAAAAMMDD.zip` acompanhado de arquivo `.sha256`, incluindo o `parity-report.json` dentro do pacote.                                          | Must       | Dado build aprovado, quando o empacotamento roda, então o zip contém os quatro arquivos StarDict mais o relatório, e o checksum confere.    |
| 🟡 RF-03 | O sistema deve enviar pacote e checksum ao WebDAV da VPS por HTTPS autenticado, com credenciais lidas de configuração externa (variável de ambiente ou arquivo fora do git), nunca hardcoded.                       | Must       | Dado upload concluído, quando o repositório é inspecionado, então nenhuma credencial aparece em código ou histórico git.                    |
| 🟡 RF-04 | O sistema deve verificar o upload baixando o checksum publicado e comparando com o local; divergência apaga o upload parcial e reporta falha.                                                                       | Must       | Dado upload truncado pela rede, quando a verificação roda, então a publicação é declarada falha e o arquivo parcial é removido do servidor. |
| 🟡 RF-05 | O sistema deve atualizar o ponteiro de versão corrente (`manifest.json` no WebDAV com nome do pacote, checksum e data) somente após verificação bem-sucedida, preservando no servidor as 2 versões anteriores.      | Must       | Dado histórico com 3 versões, quando uma nova é publicada, então a mais antiga é removida e o `manifest.json` aponta à nova.                |
| 🟡 RF-06 | O sistema deve registrar no README o procedimento por dispositivo: URL do `manifest.json`, download do pacote, extração em `koreader/data/dict/` e reinício do KOReader, com o fallback USB descrito passo a passo. | Must       | Dado um dispositivo virgem, quando o procedimento é seguido, então o dicionário aparece na lista do KOReader em menos de 5 minutos.         |
| 🟡 RF-07 | O sistema deve emitir log estruturado da publicação: versão, bytes enviados, duração, resultado da verificação.                                                                                                     | Should     | Dado publicação íntegra, quando conclui, então o log contém `versao=`, `bytes=`, `duracao_s=` e `verificacao=ok`.                           |

### 6.2 Fluxo Principal (Happy Path)

1. O mantenedor invoca o comando de publicação apontando o diretório do artefato aprovado.
2. O sistema confere o gate de paridade e empacota artefato, relatório e checksum.
3. O sistema envia pacote e checksum ao WebDAV autenticado.
4. O sistema baixa o checksum publicado, confere a integridade e atualiza o `manifest.json`.
5. O sistema remove a versão excedente mais antiga e emite o log de publicação.
6. Resultado: qualquer dispositivo alcança a versão corrente pelo procedimento do README.

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Instalação offline (fallback):**

1. O leitor copia o zip do desktop ao dispositivo via cabo USB.
2. O leitor extrai em `koreader/data/dict/` conforme a seção de fallback do README.
3. Resultado: dicionário operante sem nenhuma dependência de rede.

**Fluxo Alternativo B — Retorno à versão anterior:**

1. O mantenedor aponta o `manifest.json` de volta ao pacote anterior preservado no servidor.
2. Os dispositivos reinstalam pela versão apontada; nenhum rebuild é necessário.

---

## 7. Requisitos Não-Funcionais

| ID        | Requisito                                    | Valor alvo                  | Observação                                                             |
| --------- | -------------------------------------------- | --------------------------- | ---------------------------------------------------------------------- |
| 🟡 RNF-01 | Transporte                                   | HTTPS com autenticação      | WebDAV privado; nunca HTTP puro                                        |
| 🟡 RNF-02 | Duração da publicação (upload + verificação) | < 10 min em banda doméstica | pacote estimado < 250 MB                                               |
| 🟡 RNF-03 | Dependências novas                           | 0 preferencialmente         | avaliar `curl` (presente no macOS) antes de qualquer biblioteca WebDAV |
| 🟡 RNF-04 | Retenção de versões no servidor              | corrente + 2 anteriores     | equilíbrio entre rollback e disco da VPS                               |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 CLI de publicação (camada de apresentação), orquestração de empacotar→enviar→verificar→apontar (aplicação) e adaptador WebDAV (infraestrutura, único ponto que conhece HTTP).

**Comportamento esperado:**
🟡 O adaptador WebDAV expõe operações mínimas (enviar, baixar, remover, listar) atrás de interface própria; a orquestração é testável com adaptador em memória. O procedimento por dispositivo é documentação viva no README, tratada como entregável com critério de aceite próprio (RF-06).

**Estados da UI:**

- Estado vazio: n/a — CLI.
- Estado de carregamento: log de progresso do upload por percentual.
- Estado de erro: erro nomeado com causa (gate, rede, verificação) e exit code ≠ 0.
- Estado de sucesso: log estruturado com versão publicada e URL do manifest.

---

## 9. Modelo de Dados

**Entidades novas ou modificadas:**

```
ManifestDistribuicao {           // manifest.json no WebDAV
  versao_corrente: str           // aurelio-stardict-vAAAAMMDD.zip
  sha256: str
  publicado_em: str (ISO 8601)
  anteriores: list[{versao: str, sha256: str}]
}
```

**Migrações necessárias:** Não — estado vive no WebDAV como arquivos; regenerável a partir de uma republicação.

---

## 10. Integrações e Dependências

| Dependência                                 | Tipo                      | Impacto se indisponível                                                       |
| ------------------------------------------- | ------------------------- | ----------------------------------------------------------------------------- |
| 🟡 WebDAV na VPS (projeto `koreader-notas`) | Obrigatória para publicar | Erro claro de conectividade; fallback USB cobre a instalação nos dispositivos |
| 🟡 `parity-report.json` aprovado            | Obrigatória               | Publicação recusada pelo gate (RF-01)                                         |
| 🟡 Credenciais WebDAV em config externa     | Obrigatória               | `CredencialAusenteError` orientando onde configurá-las                        |
| 🟡 `curl` ou cliente HTTP equivalente       | Obrigatória               | Presente por padrão no macOS; ausência gera erro nomeado na pré-checagem      |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário                                          | Trigger                                 | Comportamento esperado                                                                                       |
| ------------------------------------------------ | --------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 🟡 EC-01: WebDAV indisponível                    | VPS fora do ar, DNS, timeout de conexão | Erro claro com causa e sugestão do fallback USB; nenhum retry automático prolongado (1 nova tentativa única) |
| 🟡 EC-02: Upload truncado                        | Queda de rede no meio do envio          | Verificação de checksum detecta; arquivo parcial removido do servidor; publicação declarada falha            |
| 🟡 EC-03: Credencial ausente ou recusada         | Config externa vazia ou 401 do servidor | `CredencialAusenteError` ou `CredencialRecusadaError`, cada um com instrução específica                      |
| 🟡 EC-04: Disco cheio na VPS                     | Servidor recusa escrita (507/500)       | Erro nomeado sugerindo remover versões antigas; ponteiro corrente permanece na versão anterior íntegra       |
| 🟡 EC-05: Publicação concorrente                 | Duas execuções simultâneas do comando   | Arquivo de lock local impede a segunda execução com mensagem clara                                           |
| 🟡 EC-06: `manifest.json` corrompido no servidor | JSON inválido ao baixar                 | Reconstrução do manifest a partir da listagem de pacotes e checksums presentes no servidor                   |

---

## 12. Segurança e Privacidade

- **Autenticação:** WebDAV com usuário/senha sobre HTTPS; credenciais fora do git.
- **Autorização:** área privada do WebDAV, sem listagem pública — condição imposta pelos direitos autorais do conteúdo.
- **Dados sensíveis:** o pacote contém a obra sob copyright; publicá-lo em local público violaria a restrição de compliance do PRD. A URL não deve circular fora dos dispositivos do usuário.
- **Auditoria:** `manifest.json` mais logs de publicação registram quem publicou o quê e quando (single user, registro por data).

---

## 13. Plano de Rollout

- **Estratégia:** primeira publicação após o spike de flexões aprovado e a primeira validação de paridade íntegra; instalação dispositivo a dispositivo pelo procedimento do README.
- **Como reverter (rollback):** fluxo alternativo B — reapontar o `manifest.json` à versão anterior preservada; para o código, `git revert`.
- **Monitoramento pós-deploy:** conferir em cada dispositivo, na primeira sessão de leitura, que a versão instalada casa com o checksum do manifest.

---

## 14. Open Questions

| #        | Pergunta                                                                                                                                                              | Impacto | Dono | Prazo                                    |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ---- | ---------------------------------------- |
| 🟡 OQ-01 | Qual o caminho e o mecanismo de autenticação exatos do WebDAV na VPS do `koreader-notas` (basic auth? subpasta dedicada?)?                                            | Médio   | iago | verificar na infra antes do reversa-plan |
| 🟡 OQ-02 | O KOReader dos dispositivos consegue baixar e extrair zip localmente, ou o procedimento exige um gerenciador de arquivos externo por plataforma (Kindle vs. Android)? | Médio   | iago | testar no spike de instalação            |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão                                     | Alternativas consideradas                             | Racional                                                                                                                           |
| ------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Reutilizar o WebDAV existente da VPS        | Syncthing; rclone para nuvem; repositório git com LFS | Infra já operante, custo zero, mesmo canal que o KOReader já usa; construir canal novo violaria o princípio de reutilização do PRD |
| Zip único com checksum e relatório embutido | Sincronizar o diretório StarDict arquivo a arquivo    | Atomicidade da versão: ou o dispositivo tem o pacote inteiro íntegro, ou não tem nada parcial                                      |
| Gatilho de atualização humano               | Cron no dispositivo; plugin Lua de auto-update        | Não-objetivo explícito do PRD (sem código Lua); frequência de atualização é baixa e o custo do automatismo não se paga             |
| Retenção corrente + 2                       | Guardar todas as versões; guardar só a corrente       | Rollback real com disco previsível na VPS                                                                                          |

---

## Apêndice

### Referências

- prd.md (seções 4, 7, 8 e 9) em `_reversa_sdd/`
- Infra WebDAV documentada no projeto `~/dev/koreader-notas`

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
  Arquivo: _reversa_sdd/sdd/distribuicao-webdav.md
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
