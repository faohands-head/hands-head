# FAO HANDS

Orquestrador que transforma qualquer website em WebsiteApp (app-style + PWA).

## Como usar

```powershell
# De um link
python scripts\websiteapp.py --url https://site-cliente.com.br

# De um briefing no Obsidian
python scripts\websiteapp.py --from-brain briefing-cliente.md

# Launcher interativo
scripts\websiteapp.ps1
```

## Pipeline

1. **Scraper** → extrai HTML + CSS + textos + animacoes + cores
2. **Gera** → projeto Next.js + Tailwind + shadcn/ui + BottomNav + Sidebar + PWA
3. **Instala** → npm install --legacy-peer-deps
4. **Preview** → http://localhost:3001
5. **Relatorio** → salva no Obsidian vault

## Bypass Cloudflare

O scraper tenta 3 metodos em sequencia:
- `cloudscraper` → TLS fingerprint bypass
- `requests` → fallback basico
- `Playwright` → Chromium real com stealth (resolve JS challenges)

Se todos falharem, use `--from-brain` com briefing manual.

## Estrutura

```
FAO-HANDS/
├── scripts/          # Scraper + generator + CLI
├── templates/        # WebsiteApp template
├── projects/         # Projetos gerados
├── vault/            # Obsidian (briefings, reports, specs)
└── README.md
```

## Setup

```powershell
cd C:\FaoFluxo\FAO-HANDS
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
copy .env.example .env
# Edite .env com suas chaves (nunca commitar)
```

Roadmap: `vault/specs/plano-produto-2026.md` · Segurança: `vault/specs/seguranca.md`

**Cliente golden:** `projects/websiteapp-acessosvipclientes-com-br-56722640`

## Requisitos

- Python 3.12+
- Node.js 18+
- Playwright (`pip install playwright && playwright install chromium`)
