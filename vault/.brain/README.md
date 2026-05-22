# 🧠 FAO HANDS — Cérebro Central

Bem-vindo ao cérebro do **FAO HANDS**.

## Estrutura

| Pasta | Função |
|-------|--------|
| `briefings/` | Escreva aqui o briefing do projeto. O Manager lê daqui. |
| `specs/` | Especificações técnicas, arquitetura, decisões. |
| `reports/` | Relatórios gerados pelo FAO HANDS após cada execução. |
| `.brain/` | Este documento e configurações internas. |

## Fluxo

1. **Você** escreve o briefing em `briefings/`
2. **FAO HANDS** (Manager) lê o briefing, decompõe em tasks
3. **Engineer Agents** (Claude/Ollama) executam as tasks
4. **FAO HANDS** escreve o relatório em `reports/`
5. **Você** consulta os resultados no Obsidian
