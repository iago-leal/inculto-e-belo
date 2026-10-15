# Permissões e papéis — inculto-e-belo

> Gerado pelo reversa-detective em 2026-07-03; re-extraído em 2026-10-15

## Veredito

🟢 **Não há RBAC nem ACL técnico:** o sistema é local, de um só usuário e sem autenticação. O controle de acesso é jurídico e operacional. A única conta envolvida é a do próprio usuário no Readest, que sincroniza o dicionário importado na nuvem privada.

## 1. Papéis reais

| Papel | Quem | O que pode |
|-------|------|------------|
| Mantenedor | iago (único) | Tudo: consultar, gerar e validar artefatos, atualizar o manifesto, fazer e restaurar backup |
| Leitor | iago nos dispositivos pessoais: KOReader no Mac e no Boox; Readest no Mac e nos dispositivos da conta | Consumir os artefatos derivados |
| Terceiros | Ninguém | **Nada.** Nenhum artefato é distribuído |

## 2. Matriz de restrições efetivas

| Recurso | Regra | Mecanismo | Confidência |
|---------|-------|-----------|-------------|
| Conteúdo do Aurélio (banco e derivados) | Uso estritamente pessoal; publicação proibida | Direitos autorais (RB-11); `bookname` com «uso pessoal» | 🟢 |
| `aurelio_normalized.db` | Nunca versionado | `.gitignore` | 🟢 |
| `dist/` e `spike/*/dist/` | Nunca versionados | `.gitignore` | 🟢 |
| Escrita no banco | Proibida no ciclo forward | Conexão `mode=ro` no repositório e no spike (RB-10) | 🟢 |
| Artefato do Readest na nuvem | Permitido só na nuvem privada da conta do usuário; isso não constitui publicação | Decisão do usuário (RN-08 da 003); sincronização do próprio Readest | 🟢 |
| Testes versionados | Sem conteúdo do Aurélio, só dados sintéticos | Convenção verificada em `pipeline/tests/conftest.py` | 🟢 |
| Código de busca do Readest (AGPL-3.0) | Usado localmente, não redistribuído | Cache fora do git (`.gitignore`) | 🟢 |
| Artefato reprovado do Readest | Não importar; guardado só para diagnóstico | `dist/readest.reprovado/` e exit 3 | 🟢 |
| Artefato reprovado do KOReader | Não instalar | Exit 3 com mensagem; sem bloqueio físico | 🟡 |
| Rede | Só na primeira obtenção da conferência (GitHub, npm) | Cache local íntegro dispensa a rede | 🟢 |
| Backup no Drive | Acesso pela conta pessoal via rclone | Credencial rclone local | 🟢 |
| Artefatos do Reversa | Agentes só escrevem em `.reversa/`, `_reversa_sdd/`, `_reversa_forward/`, `_reversa_docs/`; o código, só no coding sob `.reversa/reversa-config.json` | Regra do framework e gancho `check-legacy-policy.mjs` | 🟢 |
