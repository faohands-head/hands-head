---
tipo: spec
operacao: roadmap
status: em_producao
created: 2026-05-23
---

# Plano produto FAO HANDS — 2026

## Norte-estrela

Website comum → **WebApp real** (App Shell, PWA, IR v1.0.0, patch incremental, deploy repetível).

**Cliente golden:** `websiteapp-acessosvipclientes-com-br-56722640`

## Etapas

| # | Nome | Status | Meta |
|---|------|--------|------|
| 0 | Fundação e higiene | **em andamento** | Git limpo, manifest, segurança |
| 1 | Pipeline URL confiável | pendente | Preservação ≥95% VIP |
| 2 | IR como contrato único | pendente | URL/prompt/briefing → AppIR |
| 3 | App Shell produção | pendente | PWA + shell responsivo |
| 4 | Agentes + Patch | pendente | JSON Patch sem rebuild |
| 5 | Ops e automação | pendente | CI, n8n, vault sync |
| 6 | Produto comercial | pendente | 1º cliente pago |

## Etapa 0 — checklist

- [x] Remote git sem PAT embutido
- [x] `brain.py` usa `OBSIDIAN_API_KEY` do ambiente
- [x] `.env.example` + `requirements.txt` + `specs/seguranca.md`
- [x] `projects.json` alinhado ao disco
- [x] Fatal Model duplicados → `projects/_archive/`
- [ ] Rotacionar API keys (ação manual do operador)
- [ ] Commit + push `main`

## Próximo passo imediato (Etapa 1)

```powershell
cd C:\FaoFluxo\FAO-HANDS
python scripts\validate_preservation.py --url https://acessosvipclientes.com.br/ --slug websiteapp-acessosvipclientes-com-br-56722640
```

(criar script na Etapa 1)
