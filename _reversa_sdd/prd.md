# PRD: Aurélio no KOReader (inculto-e-belo)

> Selo 🟡 PLANEJADO. Documento gerado a partir de ideation + personas.

**Versão:** 1.0
**Data:** 2026-07-03T20:04:45Z
**Autor:** reversa-drafter
**Status:** rascunho

---

## 1. Problema

🟡 Falta um dicionário de português brasileiro de qualidade utilizável no KOReader. Os dicionários StarDict de português em circulação têm cobertura pobre, verbetes truncados ou origem duvidosa — nenhum se compara ao Aurélio normalizado (~143k verbetes em SQLite) que o projeto já possui. O ativo existe, mas está preso num formato que nenhum leitor consome; a consulta durante a leitura ou funciona ao toque, offline e imediata, ou quebra o fluxo. Agrava o problema o fato de o dicionário precisar existir, idêntico, em todos os dispositivos com KOReader do usuário, sem instalação manual repetida.

### Quem sente

🟡
- **iago-leitor**, no momento do toque numa palavra desconhecida durante leitura literária de imersão, em qualquer dispositivo com KOReader, frequentemente offline.
- **iago-mantenedor-futuro**, ao retomar o projeto após meses de pausa (memória fria) para regenerar o dicionário, atualizar o banco ou construir a próxima aplicação — e ao distribuir o artefato entre dispositivos.

---

## 2. Personas-alvo

🟡 Referência completa em [`personas.md`](./personas.md). Resumo:

- **iago-leitor**: 🟡 médico e leitor literário, intermediário em KOReader (usa, não fuça); dor: dicionários PT fracos ou truncados que quebram o fluxo de leitura.
- **iago-mantenedor-futuro**: 🟡 o mesmo Iago 12 meses à frente, single maintainer intermitente, avançado em desenvolvimento assistido por IA; dor: projeto irretomável por README desatualizado, setup irreproduzível e ausência de testes.

---

## 3. Métricas de sucesso

🟡 Derivadas do `ideation.md` (métrica confirmada: uso diário real) e das premissas/jornadas:

| Métrica | Unidade | Alvo | Prazo |
|---|---|---|---|
| 🟡 Latência do lookup (toque → verbete) | segundos | < 1 | na entrega |
| 🟡 Funcionamento offline | % das consultas | 100 | na entrega |
| 🟡 Operação sem manutenção | dias corridos | 90 | 3 meses após instalação |
| 🟡 Verbetes preservados na conversão | verbetes | ~143k (100% do banco) | na entrega |
| 🟡 Retomada fria (clone → pipeline operante) | minutos | < 10, guiado só pelo README | contínuo |

---

## 4. Escopo (in)

🟡
- 🟡 Pipeline de conversão do `aurelio_normalized.db` (SQLite) para formato de dicionário lido **nativamente** pelo KOReader.
- 🟡 Preservação integral dos ~143k verbetes, com validação automatizada de integridade e contagem na saída.
- 🟡 Suporte a lookup de palavras flexionadas (plurais, verbos conjugados), na medida do que o formato-alvo permitir.
- 🟡 Publicação do artefato no WebDAV da VPS já existente e procedimento documentado de instalação/atualização por dispositivo.
- 🟡 Qualidade estrutural como entrega: specs SDD, testes (TDD) com suíte rápida, README de retomada, setup reproduzível com lock file, logs/erros explícitos.

---

## 5. Não-objetivos (out)

🟡 Confirmados pelo usuário:

- 🟡 **Distribuição pública do dicionário** — nada de publicar o artefato à comunidade nesta fase (licença do conteúdo do Aurélio).
- 🟡 **Outras aplicações além do KOReader** — app web, CLI de consulta, integração Anki etc. ficam para ciclos futuros; esta entrega é só o dicionário no KOReader.

---

## 6. Restrições

🟡

| Tipo | Descrição |
|---|---|
| 🟡 Técnica | 🟡 Python 3 + `sqlite3` da biblioteca padrão; dependências mínimas e pinadas (filtro de longevidade); OOP, TDD e SDD como método; consumir apenas formatos que o KOReader lê nativamente (sem código Lua). |
| 🟡 Prazo | 🟡 [INDEFINIDO, validar com usuário] — nenhum prazo declarado nas fontes. |
| 🟡 Compliance | 🟡 Conteúdo do Aurélio sob direitos autorais: uso estritamente pessoal; nenhum artefato distribuível publicamente. |
| 🟡 Orçamento | 🟡 Custo zero: ferramentas gratuitas/open source; infraestrutura (VPS/WebDAV) já existente e paga. |

---

## 7. Dependências externas

🟡
- 🟡 **KOReader** (dispositivos do usuário) — consumidor final; define os formatos de dicionário aceitos e o comportamento de lookup/flexões.
- 🟡 **WebDAV na VPS existente** (projeto `koreader-notas`) — canal de distribuição; reutilizar, não construir.
- 🟡 **`aurelio_normalized.db`** — insumo único; fica fora do git, backup no Drive via rclone; o pipeline pressupõe sua presença local.
- 🟡 **Ferramenta de geração do formato-alvo** (ex.: PyGlossary) — [INDEFINIDO, validar com usuário]: decidir na fase de specs se entra dependência externa ou implementação própria, sob o filtro de longevidade.

---

## 8. Riscos

🟡 Derivados das premissas do `ideation.md`, das jornadas e das restrições:

| Risco | Impacto | Probabilidade | Mitigação proposta |
|---|---|---|---|
| 🟡 Perda ou truncamento de verbetes na conversão | 🟡 alto | 🟡 média | 🟡 Validação automatizada no pipeline: contagem total + amostragem de verbetes comparada à origem (teste de paridade). |
| 🟡 KOReader não encontra palavras flexionadas | 🟡 alto | 🟡 média | 🟡 Protótipo de validação cedo (spike) antes do pipeline completo; avaliar índice de sinônimos/formas do formato-alvo. |
| 🟡 Banco normalizado com defeitos de integridade | 🟡 médio | 🟡 baixa | 🟡 Smoke tests de esquema e contagem na entrada do pipeline; falha barulhenta com erro nomeado. |
| 🟡 Mudança de comportamento/formato em versão futura do KOReader | 🟡 médio | 🟡 baixa | 🟡 Preferir formato aberto, estável e documentado; registrar versão testada do KOReader no README. |
| 🟡 Retomada fria falhar (projeto vira arqueologia) | 🟡 médio | 🟡 média | 🟡 README como gate de retomada, lock file, suíte de testes < 2 min, microdecisões registradas. |
| 🟡 WebDAV indisponível no momento da atualização | 🟡 baixo | 🟡 baixa | 🟡 Instalação manual (cópia de pasta) documentada como fallback. |

---

## 9. Critérios de aceite (alto nível)

🟡
- 🟡 **Dado** um livro aberto no KOReader com o dicionário instalado, **quando** o leitor toca (long-press) numa palavra — inclusive flexionada —, **então** o verbete correspondente do Aurélio aparece no popup em menos de 1 segundo, sem conexão de rede.
- 🟡 **Dado** o repositório reaberto após meses de pausa, **quando** o mantenedor segue apenas o README, **então** recria o ambiente, roda a suíte de testes com sucesso e regenera o dicionário em menos de 10 minutos.
- 🟡 **Dado** um artefato de dicionário validado pelo pipeline, **quando** publicado no WebDAV da VPS, **então** cada dispositivo com KOReader consegue baixá-lo/atualizá-lo pelo procedimento documentado.
- 🟡 **Dado** o banco de origem com ~143k verbetes, **quando** o pipeline de conversão executa, **então** o artefato final contém 100% dos verbetes, comprovado por validação automatizada.

---

## Pendências de cobertura

🟡
- 🟡 **Prazo** — nenhum declarado; assumido "sem prazo" até validação (seção 6).
- 🟡 **Ferramenta de geração do formato-alvo** — dependência externa vs. implementação própria, a decidir na spec (seção 7).
- 🟡 **Não-objetivos não confirmados** — "editar/corrigir conteúdo do banco" e "plugin/código Lua no KOReader" foram oferecidos mas não selecionados pelo usuário; o segundo consta como restrição técnica, o primeiro segue sem decisão explícita.
- 🟡 **Alvo quantitativo para cobertura de flexões** — a premissa exige que o lookup funcione com formas flexionadas, mas não há número definido (ex.: % de palavras tocadas resolvidas).

---

Gerado por reversa-drafter em 2026-07-03T20:04:45Z
Fontes: ideation.md, personas.md
