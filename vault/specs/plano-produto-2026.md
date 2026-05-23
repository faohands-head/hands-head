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
| 0 | Fundação e higiene | **concluida** | Git limpo, manifest, segurança |
| 1 | Pipeline URL confiável | **em andamento** | VIP briefing 100% preservação |
| 2 | IR como contrato único | **concluida** | URL/prompt/briefing → AppIR |
| 3 | App Shell produção | **em andamento** | PWA + shell responsivo |
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
- [x] Commit + push `main` (`b237ccd`)

## Próximo passo imediato (Etapa 1)

```powershell
cd C:\FaoFluxo\FAO-HANDS
python scripts\validate_preservation.py --url https://acessosvipclientes.com.br/ --slug websiteapp-acessosvipclientes-com-br-56722640
```

```powershell
py -3 scripts\validate_preservation.py --url https://acessosvipclientes.com.br/ --project websiteapp-acessosvipclientes-com-br-56722640 --texts-file vault/briefings/acessosvip-websiteapp.md
# Ou rebuild:
py -3 scripts\websiteapp.py --from-brain acessosvip-websiteapp.md --out-dir websiteapp-acessosvipclientes-com-br-56722640 --no-install --strict
```

- [x] `validate_preservation.py` com match fuzzy + filtro cPanel
- [x] Briefing merge quando site = placeholder hospedagem
- [x] Golden VIP regenerado: **100%** (16/16 textos)
- [ ] Preservação com scrape real quando DNS apontar para site real

## Etapa 2 — checklist

- [x] `AppIR` v1.0.0 com `navigation`, `source_texts`, `websiteapp_sections`
- [x] `agents/websiteapp_ir.py` — Plan → Structure determinístico
- [x] IR salvo em `vault/specs/<slug>-ir.json`
- [x] `websiteapp.py` sempre passa pelo IR antes do render
- [x] `--prompt` modo WebsiteApp usa mesmo pipeline
- [x] `validate_ir.py` para checagem do JSON
