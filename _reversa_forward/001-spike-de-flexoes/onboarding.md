# Onboarding: como executar o spike de flexões

> Identificador: `001-spike-de-flexoes`
> Público: o mantenedor (ou o eu-de-daqui-a-12-meses) executando o spike pela primeira vez.
> Pré-requisitos de hardware: MacBook (geração) e Boox Air 4C com KOReader instalado (medição).

## 1. Preparar o ambiente

1. Confirme que o banco está presente e íntegro:

   ```sh
   cd ~/dev/inculto-e-belo
   sqlite3 -readonly aurelio_normalized.db "PRAGMA integrity_check; SELECT COUNT(*) FROM entries;"
   # esperado: ok / 143376
   ```

   Se o `.db` não existir (clone limpo), restaure do backup: `rclone copy gdrive:inculto-e-belo/aurelio_normalized.db .`

2. Instale as dependências pinadas do spike (a pasta `spike/001-flexoes/` é criada pelo `/reversa-coding`):

   ```sh
   cd spike/001-flexoes
   uv sync   # lê pyproject.toml + uv.lock (PyGlossary 5.4.1 pinado)
   ```

## 2. Gerar o artefato

3. Rode o piloto primeiro (valida a premissa do `.syn` via PyGlossary com ~10 verbetes, termina em segundos):

   ```sh
   uv run python gerar_spike.py --piloto
   # verificar na saída: synwordcount > 0 no .ifo do piloto
   ```

4. Rode a geração em escala real, medindo memória e tempo (RF-07):

   ```sh
   /usr/bin/time -l uv run python gerar_spike.py 2> medicao-geracao.txt
   ```

5. Confira o resultado da geração:
   - `dist/` contém `.ifo`, `.idx`, `.dict.dz`, `.syn`;
   - o `.ifo` declara `wordcount=137784` e `synwordcount ≥ 900000`;
   - `dist/relatorio-cobertura.json` fecha a conta: entrada = gravadas + descartes;
   - `medicao-geracao.txt` tem `maximum resident set size` (pico de memória) e tempo total.

## 3. Instalar no Boox Air 4C

6. Conecte o Boox ao MacBook por USB (modo transferência de arquivos/MTP).
7. Copie a pasta do artefato para o cartão do dispositivo, dentro de `koreader/data/dict/` (crie `dict/` se não existir).
8. Ejete o dispositivo, abra o KOReader e confirme que o dicionário "Aurélio spike (uso pessoal)" aparece em Configurações → Dicionário. Feche e reabra o KOReader antes de medir (sessão fria — evita cache quente).

## 4. Executar o roteiro (a medição que decide)

9. Abra `_reversa_forward/001-spike-de-flexoes/roteiro.md` (gerado na fase de codificação) — 20 linhas: forma → lema esperado.
10. Abra um livro qualquer no KOReader e, para cada palavra do roteiro:
    - localize (ou digite na busca do dicionário, se a palavra não ocorrer no livro — anote qual via usou);
    - dispare o cronômetro no toque e pare quando o popup exibir o verbete;
    - registre: verbete aberto (sim/não, qual) e latência em segundos.
11. **Regra da faixa limítrofe (RF-03):** medição entre 0,8 s e 1,2 s obriga remedição filmando a tela (câmera do celular, 60 fps); conte os frames entre toque e popup e use esse valor no relatório.
12. Para as 2 formas capitalizadas do roteiro: toque a forma como aparece em início de frase e registre se o verbete abriu (responde OQ-02).
13. Observação oportunista (RF-08): nos verbetes completos, anote como o popup renderiza negrito, itálico e listas.

## 5. Redigir o veredito

14. Preencha `_reversa_forward/001-spike-de-flexoes/spike-report.md`:
    - dados brutos das 20 palavras (do `roteiro.md`);
    - mediana das latências e máximo individual;
    - aplique RN-05 mecanicamente: **NO-GO se mediana ≥ 1 s ou qualquer palavra ≥ 3 s; senão GO**;
    - respostas explícitas: OQ-01 e OQ-02 de `indice-de-flexoes`; OQ-01 (memória) e OQ-02 (HTML) de `conversao-formato`.
15. Em NO-GO: acione apenas o 1º fallback (reduzir a cobertura do `.syn` — o script aceita o corte, ver README do spike), regenere, reinstale e repita os passos 9–14, registrando a segunda rodada no relatório.

## 6. Verificação de saúde (como saber que deu certo)

- [ ] `relatorio-cobertura.json` com invariante fechada e órfãs ≈ 22 lemas
- [ ] `.ifo` com `wordcount=137784` e `synwordcount ≥ 900000`
- [ ] 20/20 linhas do roteiro com resultado e latência preenchidos, sem pendência de remedição
- [ ] `spike-report.md` com veredito GO ou NO-GO e as 4 OQs respondidas
