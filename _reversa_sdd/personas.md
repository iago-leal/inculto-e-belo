# Personas e Jornadas

> Selo 🟡 PLANEJADO em todos os itens.

## Persona 1: iago-leitor

- **Perfil:** 🟡 Médico e leitor literário, usuário final do dicionário em qualquer dispositivo com KOReader (Boox hoje, outros amanhã).
- **Contexto:** 🟡 Leitura literária de imersão (ficção, ensaística, clássicos) em qualquer dispositivo com KOReader, em lazer e estudo, frequentemente offline; a dor aparece ao encontrar palavra desconhecida ou duvidosa e tocar nela. O dicionário precisa estar presente em todos os dispositivos, idêntico.
- **Nível técnico:** 🟡 Intermediário, em KOReader — usa, não fuça: consegue copiar uma pasta de dicionário, mas não quer depurar formatos nem mexer em Lua.
- **Dor principal:** 🟡 Os dicionários de português disponíveis no KOReader são fracos, truncados ou de origem duvidosa; a consulta ou funciona ao toque, offline e imediata, ou quebra o fluxo de leitura.
- **Objetivo final:** 🟡 Domínio pleno do léxico e da norma culta — o dicionário no e-reader como instrumento de formação continuada, ligado ao projeto maior de gramática normativa.

### Jornada principal
1. 🟡 Abrir o livro no KOReader (em qualquer dispositivo)
2. 🟡 Encontrar palavra desconhecida ou duvidosa durante a leitura
3. 🟡 Tocar na palavra (long-press) para invocar o dicionário
4. 🟡 Ver o verbete do Aurélio no popup, offline, mesmo com a palavra flexionada
5. 🟡 Ler as acepções e resolver a dúvida lexical
6. 🟡 Fechar o popup e retomar a leitura no mesmo ponto

---

## Persona 2: iago-mantenedor-futuro

- **Perfil:** 🟡 O mesmo Iago, 12 meses à frente — single maintainer intermitente que reabre o projeto com memória fria.
- **Contexto:** 🟡 Três cenários: retomada fria para manutenção pontual (regenerar o dicionário, atualizar o banco, reagir a mudança no KOReader); retomada para construir a próxima aplicação sobre o mesmo banco sem quebrar o pipeline existente; e distribuição — manter o dicionário sincronizado entre os dispositivos sem instalar manualmente um a um.
- **Nível técnico:** 🟡 Avançado, em desenvolvimento assistido por IA — trabalha com agentes (Claude Code), domina Python/SQLite em nível de arquitetura e revisão, mas depende de docs, specs e testes para se reorientar.
- **Dor principal:** 🟡 Projeto irretomável — README desatualizado, setup irreproduzível e ausência de testes que provem a saúde do pipeline transformam qualquer manutenção em arqueologia.
- **Objetivo final:** 🟡 Ativo perene multi-aplicação — banco + pipeline como base estável sobre a qual as próximas aplicações nascem sem retrabalho; o conversor KOReader é só o primeiro consumidor.

### Jornada principal
1. 🟡 Reabrir o projeto após meses de pausa
2. 🟡 Ler o README para reorientar-se (gate de retomada)
3. 🟡 Recriar o ambiente com o setup reproduzível (lock file)
4. 🟡 Rodar a suíte de testes para confirmar a saúde do pipeline
5. 🟡 Executar o pipeline de conversão (banco SQLite → dicionário KOReader)
6. 🟡 Validar o artefato gerado (integridade e contagem de verbetes)
7. 🟡 Publicar o dicionário no WebDAV da VPS
8. 🟡 Baixar/atualizar o dicionário em cada dispositivo a partir do WebDAV

---

## Notas

- 🟡 O WebDAV citado na jornada da Persona 2 é infraestrutura **já existente** (VPS do ecossistema de leitura, projeto `koreader-notas`) — canal de distribuição a reutilizar, não a construir.
- 🟡 A jornada da Persona 2 tem 8 passos (um além do padrão de 7) por decisão do usuário, para dar visibilidade à etapa de distribuição multi-dispositivo via WebDAV.

---
Gerado por reversa-researcher em 2026-07-03T19:30:34Z
Fonte: ideation.md
