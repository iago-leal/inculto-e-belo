# Permissões e papéis — inculto-e-belo

> Gerado pelo reversa-detective em 2026-07-03

## Veredito

🟢 **Não há RBAC/ACL técnico:** sistema local, single-user, sem autenticação — o "controle de acesso" é jurídico e operacional.

## 1. Papéis reais

| Papel      | Quem                                           | O que pode                                                   |
| ---------- | ---------------------------------------------- | ------------------------------------------------------------ |
| Mantenedor | iago (único)                                   | Tudo: consultar, regenerar artefatos, fazer/restaurar backup |
| Leitor     | iago nos dispositivos pessoais (Boox/KOReader) | Consumir artefatos derivados (dicionário StarDict)           |
| Terceiros  | —                                              | **Nada.** Nenhum artefato é distribuído                      |

## 2. Matriz de restrições efetivas

| Recurso                                 | Regra                                                                                      | Mecanismo                                                                     | Confidência |
| --------------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- | ----------- |
| Conteúdo do Aurélio (banco e derivados) | Uso estritamente pessoal; publicação proibida                                              | Direitos autorais (PRD §6; RB-11 do domain.md) — restrição legal, não técnica | 🟢          |
| `aurelio_normalized.db`                 | Nunca versionado em repositório público                                                    | `.gitignore` (allowlist estrutural)                                           | 🟢          |
| Escrita no banco                        | Proibida no ciclo forward (somente-leitura)                                                | Convenção + conexões `mode=ro` planejadas (RB-10)                             | 🟢          |
| Backup no Drive                         | Acesso pela conta pessoal do mantenedor via rclone                                         | Credencial rclone local                                                       | 🟢          |
| Artefatos do Reversa                    | Agentes só escrevem em `.reversa/`, `_reversa_sdd/`, `_reversa_forward/`, `_reversa_docs/` | Regra absoluta do framework (CLAUDE.md/AGENTS.md)                             | 🟢          |
