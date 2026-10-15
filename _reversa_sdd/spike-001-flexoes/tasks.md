# spike-001-flexoes, Tarefas de Implementação

> Gerado pelo reversa-writer em 2026-10-15. O spike está concluído; as tarefas descrevem como reproduzi-lo.

## Pré-requisitos
- [ ] `uv` e o banco na raiz do repositório
- [ ] `uv sync` em `spike/001-flexoes/`

## Tarefas

- [ ] T-01, Conexão somente-leitura e carga dos headwords
  - Origem no legado: `spike/001-flexoes/gerar_spike.py:78`, `:88`
  - Critério de pronto: 137.784 lemas únicos
  - Confiança: 🟢
- [ ] T-02, Split e mapa com descartes classificados
  - Origem no legado: `spike/001-flexoes/gerar_spike.py:100`, `:112`
  - Critério de pronto: 774.003 formas gravadas; EC-04 aborta com exit 2
  - Confiança: 🟢
- [ ] T-03, Corpo trivial e verbete completo do roteiro
  - Origem no legado: `spike/001-flexoes/gerar_spike.py:195`, `:208`
  - Critério de pronto: os 22 lemas do roteiro com verbete integral
  - Confiança: 🟢
- [ ] T-04, Geração via PyGlossary e relatório
  - Origem no legado: `spike/001-flexoes/gerar_spike.py:314`
  - Critério de pronto: quatro arquivos e `relatorio-cobertura.json` em `dist/`
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, 🟡 Sem testes automatizados; a verificação foi a execução do piloto e da escala real, registrada no `spike-report.md` da 001

## Ordem Sugerida
T-01 → T-02 → T-03 → T-04.

## Lacunas Pendentes (🔴)
Nenhuma.
