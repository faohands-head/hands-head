---
tipo: spec
operacao: websiteapp
status: planejamento
created: 2026-05-22
---

# Operação WebsiteApp — Plano

## Missão

Dado o link de um site cliente (`https://...`), o FAO HANDS deve:

1. **Scraper total** — extrair TODO o conteúdo do site original (textos, CSS, animações, imagens, cores, fontes, layout)
2. **Preservar tudo** — nenhum texto/conteúdo original é perdido ou resumido
3. **Envelopar em WebsiteApp** — adicionar BottomNav, Sidebar, PWA, layout app-style
4. **Gerar projeto Next.js** completo com shadcn/ui + Tailwind

## Fluxo

```
Cliente envia link
       │
       ▼
┌─────────────────────────────┐
│  FASE 1: SUCK              │
│  - Baixar HTML completo     │
│  - Extrair CSS (inline +    │
│    arquivos + <style>)      │
│  - Extrair animações (CSS   │
│    keyframes, transitions)  │
│  - Extrair textos           │
│  - Extrair assets (imagens, │
│    SVGs, fonts)             │
│  - Mapear estrutura:        │
│    header, sections,        │
│    footer, navegação        │
│  - Identificar paleta de    │
│    cores (CSS vars,         │
│    classes, estilos)        │
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  FASE 2: PARSE              │
│  - Interpretar seções       │
│  - Extrair hierarquia:      │
│    Hero → Serviços →        │
│    Planos → Contato etc     │
│  - Preservar keyframes e    │
│    animações                │
│  - Preservar identidade     │
│    visual (cores, fontes)   │
│  - Gerar spec markdown no   │
│    Obsidian com tudo extraído│
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  FASE 3: TRANSFORM          │
│  - Criar template com:      │
│    - BottomNav (5 ícones)   │
│    - Sidebar (hamburger)    │
│    - PWA (manifest + sw)    │
│    - Layout app-style       │
│  - Injetar TODO conteúdo    │
│    original nas páginas     │
│  - Adaptar CSS para Tailwind│
│  - Converter animações para │
│    Tailwind/CSS modules     │
│  - Garantia: nada perdido   │
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  FASE 4: GERAR              │
│  - Next.js + Tailwind       │
│  - shadcn/ui components     │
│  - PWA completo             │
│  - npm install              │
│  - npm run dev → preview    │
│  - Relatório no Obsidian    │
└─────────────────────────────┘
```

## Ferramentas de Scraper

| Ferramenta | Função |
|-----------|--------|
| `curl` / `Invoke-WebRequest` | Baixar HTML e assets |
| `htmlq` ou regex | Extrair seções, textos, classes |
| Análise manual do CSS | keyframes, animações, variáveis |
| `Select-String` / regex | Extrair paleta de cores, fontes |

## Regras de Ouro

1. **ZERO perda de conteúdo** — nenhum texto original é cortado, resumido ou substituído
2. **Preservar animações** — keyframes CSS são convertidos para Tailwind/CSS modules
3. **Preservar identidade visual** — cores, fontes, sombras, espaçamentos
4. **Adicionar, não substituir** — app-style é uma camada extra, não uma troca
5. **Acessibilidade** — manter aria-labels, roles, semântica HTML

## Entregáveis

1. ✅ Spec de extração no Obsidian
2. ✅ Projeto Next.js gerado com TODO conteúdo preservado
3. ✅ BottomNav + Sidebar + PWA
4. ✅ Preview em localhost:3001
5. ✅ Relatório no Obsidian

## Próximo Cliente

Para executar:
```powershell
python scripts\caid.py --website https://acessosvipclientes.com.br/
```

Ou pelo launcher:
```powershell
scripts\websiteapp.ps1
```
