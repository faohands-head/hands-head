---
tipo: spec
operacao: seguranca
status: em_producao
created: 2026-05-23
---

# Segurança — FAO HANDS

## Variáveis de ambiente (`.env` local, nunca commitar)

| Variável | Uso |
|----------|-----|
| `GEMINI_API_KEY` | Intent / planner |
| `DEEPSEEK_API_KEY` | Structure / builder |
| `TOGETHER_API_KEY` | Renderer (Qwen via Together) |
| `OBSIDIAN_API_KEY` | Plugin Local REST API (Obsidian) |
| `OBSIDIAN_API_URL` | Padrão `http://localhost:27123` |

Copie `.env.example` para `.env` e preencha na máquina.

## Ações obrigatórias (Etapa 0)

1. **Rotacionar** todas as chaves que já estiveram em disco ou em URL do Git.
2. **Git remote** sem token — usar `https://github.com/faohands-head/hands-head.git` + credential manager.
3. **Obsidian** — gerar nova API key no plugin Local REST API; não versionar `data.json` com chaves.
4. **n8n** — não expor host ngrok em repositório público sem revisão.

## O que o agente pode escrever no vault

- `vault/reports/*` — relatórios de geração
- Atualização de `status` em briefings (via operador ou script)

## O que não versionar

- `.env`, `node_modules/`, `.next/`, `out/`, `.cache/`
- Certificados TLS do plugin Obsidian
