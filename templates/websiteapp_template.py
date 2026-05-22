"""WebsiteApp Template - Gera projeto Next.js com conteudo real do site"""
import json

def add_to_project(project_dir: str, spec: dict):
    from pathlib import Path
    p = Path(project_dir)

    nav_items = spec.get("nav_items", [
        {"icon": "Home", "label": "Inicio"},
        {"icon": "Briefcase", "label": "Servicos"},
        {"icon": "CreditCard", "label": "Planos"},
        {"icon": "Headphones", "label": "Suporte"},
        {"icon": "User", "label": "Conta"},
    ])
    client = spec.get("client", "Cliente")
    project_name = spec.get("project_name", client)
    goal = spec.get("goal", "WebsiteApp")

    texts = spec.get("extracted", {}).get("texts", [])
    sections_raw = spec.get("extracted", {}).get("sections", [])
    colors = spec.get("extracted", {}).get("colors", [])
    fonts = spec.get("extracted", {}).get("fonts", [])
    animations = spec.get("extracted", {}).get("animations", [])
    animations_raw = spec.get("extracted", {}).get("animations_raw", {})

    (p / "src/app").mkdir(parents=True, exist_ok=True)
    (p / "public").mkdir(parents=True, exist_ok=True)
    (p / "src/components/layout").mkdir(parents=True, exist_ok=True)
    (p / "src/components/ui").mkdir(parents=True, exist_ok=True)

    icon_imports = ", ".join(n["icon"] for n in nav_items)
    nav_items_str = json.dumps(nav_items)
    sidebar_icons = ", ".join(n["icon"] for n in nav_items[:6])

    # Bottom Nav
    _write_file(p, "src/components/layout/BottomNav.tsx", _BOTTOM_NAV_T % (icon_imports, nav_items_str))

    # Sidebar
    _write_file(p, "src/components/layout/Sidebar.tsx", _SIDEBAR_T % (sidebar_icons, nav_items_str, client))

    # Layout
    _write_file(p, "src/app/layout.tsx", _LAYOUT_T % (project_name, goal, project_name))

    # Globals CSS
    primary_color = "#3b82f6"
    for c in colors:
        if c.startswith("#") and c not in ("#ffffff", "#000000"):
            primary_color = c
            break
    _write_file(p, "src/app/globals.css", _GLOBALS_CSS_T)

    # Main page
    page_content = _build_page_content(texts, sections_raw, client)
    _write_file(p, "src/app/page.tsx", _PAGE_T % json.dumps(page_content, ensure_ascii=False))

    # PWA
    _write_file(p, "public/manifest.json", json.dumps({
        "name": project_name, "short_name": project_name[:15], "description": goal,
        "start_url": "/", "display": "standalone",
        "background_color": "#ffffff", "theme_color": primary_color,
        "icons": [{"src": "/icon-192.svg", "sizes": "192x192", "type": "image/svg+xml"},
                  {"src": "/icon-512.svg", "sizes": "512x512", "type": "image/svg+xml"}]
    }))
    _write_file(p, "public/sw.js", _SW_T)

    # SVG icons
    initials = "".join(w[0].upper() for w in client.split()[:2] if w)
    _write_file(p, "public/icon-192.svg", _SVG_192_T % primary_color)
    _write_file(p, "public/icon-512.svg", _SVG_512_T % primary_color)

    print(f"[WEBSITEAPP] Projeto gerado: {project_name}")
    print(f"[WEBSITEAPP] {len(texts)} textos, {len(animations)} animacoes, {len(colors)} cores preservados")


def _write_file(p, relpath, content):
    (p / relpath).write_text(content, encoding="utf-8")


def _build_page_content(texts, sections_raw, client):
    content = []
    title = texts[0] if texts else client
    subtitle = texts[1] if len(texts) > 1 else ""
    content.append({"type": "hero", "title": title, "text": subtitle, "className": ""})
    card_items = []
    for t in texts[2:8]:
        card_items.append({"title": t[:60], "text": t[:200]})
    if card_items:
        content.append({"type": "cards", "items": card_items, "className": ""})
    paragraphs = [t for t in texts[8:] if len(t) > 20]
    if paragraphs:
        content.append({"type": "content", "paragraphs": paragraphs[:10], "className": ""})
    content.append({"type": "footer", "text": f"(c) 2026 {client}. Todos os direitos reservados.", "className": ""})
    return content


# --- Templates string (%%s = substituicao) ---

_BOTTOM_NAV_T = """'use client'

import React, { useState } from 'react'
import { %s } from 'lucide-react'

const items: { icon: React.ElementType; label: string }[] = %s

export default function BottomNav() {
  const [active, setActive] = useState(0)
  return (
    <nav className="fixed bottom-0 left-0 right-10 flex justify-center z-50 h-16 border-t bg-background safe-area-bottom pb-1">
      <div className="flex items-center justify-around max-w-lg w-full px-2">
        {items.map((item, i) => (
          <button key={i} onClick={() => setActive(i)}
            className={`flex flex-col items-center gap-0.5 px-3 py-1 rounded-xl transition-all duration-200
              ${active === i ? 'text-primary scale-110' : 'text-muted-foreground hover:text-foreground'}`}>
            <item.icon className="w-5 h-5" />
            <span className="text-[10px] font-medium">{item.label}</span>
          </button>
        ))}
      </div>
    </nav>
  )
}
"""

_SIDEBAR_T = """'use client'

import React, { useState } from 'react'
import { X, Menu, %s } from 'lucide-react'

const items: { icon: React.ElementType; label: string }[] = %s

export default function Sidebar() {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button onClick={() => setOpen(true)}
        className="fixed top-4 left-4 z-50 p-2 rounded-xl bg-background/80 backdrop-blur border shadow-sm">
        <Menu className="w-5 h-5" />
      </button>
      {open && <div className="fixed inset-0 bg-black/40 z-40" onClick={() => setOpen(false)} />}
      <aside className={"fixed top-0 left-0 h-full w-72 bg-background border-r z-50 transform transition-transform duration-300 shadow-2xl " + (open ? 'translate-x-0' : '-translate-x-full')}>
        <div className="flex items-center justify-between p-4 border-b">
          <span className="font-bold text-lg">%s</span>
          <button onClick={() => setOpen(false)}><X className="w-5 h-5" /></button>
        </div>
        <nav className="p-2">
          {items.map((item, i) => (
            <a key={i} href="#" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-muted transition-colors">
              <item.icon className="w-5 h-5 text-muted-foreground" />
              <span>{item.label}</span>
            </a>
          ))}
        </nav>
      </aside>
    </>
  )
}
"""

_LAYOUT_T = """import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '%s',
  description: '%s',
  manifest: '/manifest.json',
  appleWebApp: { capable: true, statusBarStyle: 'default', title: '%s' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={inter.className + ' pb-16 md:pb-0'}>
        {children}
      </body>
    </html>
  )
}
"""

_GLOBALS_CSS_T = """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
"""

_PAGE_T = """'use client'

import BottomNav from '@/components/layout/BottomNav'
import Sidebar from '@/components/layout/Sidebar'

const sections = %s

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
      <Sidebar />
      <main className="max-w-5xl mx-auto px-4 pt-20 pb-24 md:pb-12">
        {sections.map((section, i) => (
          <section key={i} className={'mb-16 ' + (section.className || '')}>
            {section.type === 'hero' && (
              <header className="text-center mb-12">
                <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">{section.title}</h1>
                <p className="text-xl text-muted-foreground max-w-3xl mx-auto">{section.text}</p>
              </header>
            )}
            {section.type === 'cards' && (
              <div className="grid gap-6 md:grid-cols-3">
                {section.items.map((item, j) => (
                  <div key={j} className="bg-card rounded-2xl p-6 shadow-sm border hover:shadow-md transition-shadow">
                    <h3 className="font-semibold mb-2">{item.title}</h3>
                    <p className="text-sm text-muted-foreground">{item.text}</p>
                  </div>
                ))}
              </div>
            )}
            {section.type === 'content' && (
              <div className="prose prose-gray max-w-none">
                {section.paragraphs.map((p, j) => (
                  <p key={j} className="text-muted-foreground mb-4">{p}</p>
                ))}
              </div>
            )}
            {section.type === 'footer' && (
              <footer className="border-t pt-8 mt-12 text-center text-sm text-muted-foreground">
                <p>{section.text}</p>
              </footer>
            )}
          </section>
        ))}
      </main>
      <BottomNav />
    </div>
  )
}
"""

_SW_T = """const C='v1',U=['/','/index.html'];self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(U)))});self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))})"""

_SVG_192_T = """<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192">
  <rect width="192" height="192" rx="32" fill="%s"/>
  <text x="96" y="120" font-family="Arial,sans-serif" font-size="80" font-weight="bold" fill="white" text-anchor="middle">AV</text>
</svg>"""

_SVG_512_T = """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="64" fill="%s"/>
  <text x="256" y="300" font-family="Arial,sans-serif" font-size="200" font-weight="bold" fill="white" text-anchor="middle">AV</text>
</svg>"""
