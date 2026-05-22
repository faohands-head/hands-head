---
projeto: AcessosVIP
data: 2026-05-22
---

# Especificação: AcessosVIP

```json
{
  "project_type": "websiteapp",
  "project_name": "AcessosVIP",
  "goal": "Transformar o website atual em um WebsiteApp com experi\u00eancia de aplicativo no navegador, tanto no desktop quanto no celular.",
  "pages": [
    "In\u00edcio",
    "Servi\u00e7os",
    "Planos",
    "Suporte",
    "Conta",
    "Dashboard"
  ],
  "components": [
    "Bottom navigation bar",
    "Hamburger menu",
    "Cards e sombras suaves",
    "Sidebar retr\u00e1til",
    "PWA elements (service worker, manifest.json)",
    "Lucide icons"
  ],
  "features": [
    "Responsividade 100%",
    "Modo escuro opcional",
    "Service worker para funcionar offline",
    "Manifest.json para instalar como app no celular",
    "Design moderno com cards e sombras suaves"
  ],
  "tasks": [
    {
      "id": 1,
      "description": "Desenvolver a estrutura da aplica\u00e7\u00e3o usando Next.js + Tailwind + shadcn/ui.",
      "dependencies": [],
      "type": "code"
    },
    {
      "id": 2,
      "description": "Implementar a navega\u00e7\u00e3o mobile com Bottom navigation bar e Hamburger menu.",
      "dependencies": [
        1
      ],
      "type": "code"
    },
    {
      "id": 3,
      "description": "Desenvolver a navega\u00e7\u00e3o desktop com Sidebar retr\u00e1til ou Bottom nav adaptada.",
      "dependencies": [
        1,
        2
      ],
      "type": "code"
    },
    {
      "id": 4,
      "description": "Estilizar a aplica\u00e7\u00e3o com cores do cliente e sombras suaves.",
      "dependencies": [
        1,
        2,
        3
      ],
      "type": "design"
    },
    {
      "id": 5,
      "description": "Implementar componentes app-style como navega\u00e7\u00e3o inferior, sheet/drawer.",
      "dependencies": [
        1,
        2,
        3,
        4
      ],
      "type": "code"
    },
    {
      "id": 6,
      "description": "Adicionar Lucide icons para a bottom nav bar.",
      "dependencies": [
        1,
        5
      ],
      "type": "code"
    },
    {
      "id": 7,
      "description": "Implementar PWA elements (service worker e manifest.json).",
      "dependencies": [
        1,
        5
      ],
      "type": "code"
    },
    {
      "id": 8,
      "description": "Desenvolver a p\u00e1gina de In\u00edcio.",
      "dependencies": [
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "type": "code"
    },
    {
      "id": 9,
      "description": "Desenvolver a p\u00e1gina de Servi\u00e7os.",
      "dependencies": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8
      ],
      "type": "code"
    },
    {
      "id": 10,
      "description": "Desenvolver a p\u00e1gina de Planos.",
      "dependencies": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9
      ],
      "type": "code"
    },
    {
      "id": 11,
      "description": "Desenvolver a p\u00e1gina de Suporte.",
      "dependencies": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10
      ],
      "type": "code"
    },
    {
      "id": 12,
      "description": "Desenvolver a p\u00e1gina de Conta.",
      "dependencies": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11
      ],
      "type": "code"
    },
    {
      "id": 13,
      "description": "Desenvolver o Dashboard administrativo com cards, gr\u00e1ficos e tabelas.",
      "dependencies": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12
      ],
      "type": "code"
    },
    {
      "id": 14,
      "description": "Testar a aplica\u00e7\u00e3o em diferentes navegadores e dispositivos.",
      "dependencies": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13
      ],
      "type": "test"
    },
    {
      "id": 15,
      "description": "Optimizar a performance e o desempenho da aplica\u00e7\u00e3o.",
      "dependencies": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14
      ],
      "type": "code"
    },
    {
      "id": 16,
      "description": "Liberar a aplica\u00e7\u00e3o para o primeiro cliente real.",
      "dependencies": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "type": "release"
    }
  ]
}
```
