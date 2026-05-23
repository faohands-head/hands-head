---
tipo: spec
operacao: github
status: em_producao
created: 2026-05-22
---

# GitHub — Ampliar Operacao FAO HANDS

## Repositorio
`https://github.com/faohands-head/hands-head`

## Estrutura Proposta

```
faohands-head/hands-head
│
├── .github/
│   ├── workflows/          # GitHub Actions
│   │   ├── deploy.yml      # Auto-deploy para preview
│   │   ├── test.yml        # Testar build do projeto
│   │   └── sync-obsidian.yml # Sincronizar vault
│   ├── ISSUE_TEMPLATE/     # Templates de issues
│   └── CODEOWNERS          # Donos dos codigos
│
├── scripts/                # Scripts do FAO HANDS
│   ├── website_scraper.py
│   ├── websiteapp.py
│   ├── websiteapp.ps1
│   └── brain.py
│
├── templates/              # Templates de projeto
│   ├── websiteapp_template.py
│   └── __init__.py
│
├── vault/                  # Obsidian vault (documentacao)
│   ├── briefings/
│   ├── reports/
│   └── specs/
│
├── projects/               # Projetos gerados (git submodules?)
│   └── websiteapp-cliente-x/
│
└── README.md               # Documentacao principal
```

## Fluxo com GitHub

```
CLIENTE
  │
  ├─► [1] Briefing no Obsidian
  │        │
  │        ▼
  │    Commit vault/ → GitHub
  │
  ├─► [2] Rodar websiteapp
  │        │
  │        ▼
  │    Gera projeto em projects/
  │    Commit projeto → GitHub Pages preview
  │
  ├─► [3] GitHub Actions
  │        │
  │        ├─► Build automatico
  │        ├─► Deploy preview (GitHub Pages / Vercel)
  │        ├─► Testar compilacao
  │        └─► Notificar no Obsidian
  │
  └─► [4] Cliente ve preview
           │
           ▼
       Feedback → Issue → Novo ciclo
```

## Beneficios

| Recurso | Ganho |
|---------|-------|
| Git versionado | Nunca perder projeto, rollback facil |
| GitHub Actions | Build + test + deploy automatico |
| GitHub Pages | Preview publico para cliente ver |
| Issues | Feedback tracking, bug reports |
| Projects (Kanban) | Gerenciar multiplos clientes |
| Wiki | Documentacao viva do sistema |
| Templates | Scaffolding de novos projetos |
| Submodules | Projetos independentes dentro do ecossistema |
| Code review | Qualidade antes de entregar |
| Acoes agendadas | Scraping periodico de sites |

## Acao Imediata

```powershell
# 1. Iniciar git no FAO-HANDS
cd C:\FaoFluxo\FAO-HANDS
git init
git add .
git commit -m "feat: initial FAO HANDS structure"

# 2. Conectar ao GitHub
git remote add origin https://github.com/faohands-head/hands-head.git
git push -u origin main

# 3. Configurar Actions (build + test)
# 4. GitHub Pages para previews
# 5. Issues para tracking de clientes
```

## Proximos Passos

1. Subir codigo existente para GitHub
2. Criar GitHub Actions: build + lint + test
3. GitHub Pages para cada projeto gerado
4. Usar Issues para cada cliente (Issue = Projeto)
5. Criar template de Issue para novos clientes
6. Automatizar deploy via Actions apos `websiteapp --url`
7. Webhook: quando briefing no Obsidian for salvo, gatilhar geracao
