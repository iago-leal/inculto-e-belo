# Regression watch — 003-dicionario-readest

> Gerado por `/reversa-coding` em 2026-10-15 (modo autônomo).
> A re-extração (`/reversa`, step-04) verifica cada item e registra o veredito no histórico abaixo.

## Watch items

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|-------------------------|-----------------------------|---------------------|-------------------|
| W001 | `_reversa_sdd/domain.md` §3 (RB-11) | Artefato do Readest de uso estritamente pessoal: `bookname` com «uso pessoal», `dist/` fora do git, nenhum conteúdo do Aurélio em `pipeline/tests/`; armazenamento só na nuvem privada da conta do usuário, que não constitui publicação (RN-08 da 003) | redação | Domain sem a ressalva da nuvem privada, artefato publicado ou compartilhado fora da conta, ou definição do Aurélio em teste versionado |
| W002 | `_reversa_sdd/domain.md` §4 (invariantes) | Baseline do alvo Readest sobre o banco de 2026-07-03: 887.546 chaves, 160.302 no `.idx`, 727.244 no `.syn`, 22.913 páginas combinadas, 16.910 sequências distintas, 261 formas sem letra descartadas | presença | Extração ou build com números diferentes sem commit correspondente do `manifesto-integridade.json` |
| W003 | `_reversa_sdd/domain.md` §3 (RB-12) | Alvo Readest determinístico: duas gerações sobre o mesmo banco com bytes idênticos nos quatro arquivos; `.ifo` com a data do manifesto e a impressão digital do conteúdo; três relatórios JSON por execução | presença | `.ifo` com data de build, bytes diferentes entre gerações ou relatório ausente |
| W004 | `_reversa_sdd/domain.md` §3 (RB-02) | Fusão no consumidor: o banco mantém homônimos em linhas próprias; a página do Readest une homônimos e homógrafos (lemas e formas) só no artefato | redação | Fusão aplicada no banco ou artigo do Readest diferente do `renderizar_artigo` do KOReader |
| W005 | `_reversa_sdd/architecture.md` §2 (P-03, P-04) | Componentes `agrupamento-readest` (domínio puro), `escrita_readest` (sem PyGlossary), `paridade_readest` (sem importar agrupamento nem escritor) e `conferencia-readest` (Node só por subprocesso) existem em `pipeline/` com essas fronteiras | presença | Re-extração não encontrar os módulos, ou encontrar a validação importando o agrupamento, ou PyGlossary no alvo Readest |
| W006 | `_reversa_sdd/domain.md` §3 (RB-10) | Banco somente-leitura também no alvo Readest; `entries.most_used` apenas lida | redação | Qualquer escrita no `.db` a partir de `pipeline/` |

## Observações (origem 🟡, sem peso de regressão)

- **O-01** — Gate do Readest (RN-07 da 003): nenhum artefato do Readest entregue sem validação e conferência aprovadas; promoção por rename, reprovado em `dist/readest.reprovado/`. Vigiar se alguém passar a importar direto do diretório de preparo.
- **O-02** — Conferência fixada no Readest `v0.12.16` (commit `3cc39ad7…`), com três reescritas mecânicas verificadas por hash; uma versão nova do Readest que mude a busca exige atualizar `fonte-readest.json` (README, seção "Atualizar a versão fixada do Readest").
- **O-03** — Ordem dos artigos depende de `entries.most_used` (L-04, critério editorial inferido): se a marca mudar de sentido numa versão nova do banco, a ordem das páginas combinadas muda sem erro.
- **O-04** — Divisor `<hr>` como fronteira de artigos (D-10): se o banco passar a conter `<hr>` no HTML, a validação reprova com o nome da chave; vigiar RB-03.
- **O-05** — Importação no Readest do Mac (RF-08, T021) concluída em 2026-10-15: arquivos importados com hash idêntico ao do artefato, dicionário habilitado e sincronizado na conta. Resta sem conferência visual explícita o divisor `<hr>` no tema escuro; se ele não aparecer, o ajuste é de estilo da página, sem efeito na busca.
- **O-06** — Peculiaridade do banco visível nas páginas: «a» registrado como forma de «bretão» faz a página de «a» mostrar «bretão» (comportamento exigido por RN-02; corrigir o dado foge ao escopo).

## Histórico de re-extrações

_(vazio — preenchido pelo step-04 do `/reversa` nas próximas extrações)_

## Arquivadas

_(vazio)_
