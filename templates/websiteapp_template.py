"""
WebsiteApp Template v2 — Gera projeto Next.js com UI rica, navegação funcional e conteúdo inteligente
"""
import json

def add_to_project(project_dir: str, spec: dict):
    from pathlib import Path
    p = Path(project_dir)

    nav_items = spec.get("nav_items", [
        {"icon": "Home", "label": "Inicio", "route": "/"},
        {"icon": "Briefcase", "label": "Servicos", "route": "/servicos"},
        {"icon": "CreditCard", "label": "Planos", "route": "/planos"},
        {"icon": "Headphones", "label": "Suporte", "route": "/suporte"},
        {"icon": "User", "label": "Conta", "route": "/conta"},
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

    # Route pages to create
    routes = {n.get("route", "/"): n["label"] for n in nav_items}

    icon_imports = ", ".join(n["icon"] for n in nav_items)
    nav_items_ts = "[" + ", ".join(f'{{ icon: {n["icon"]}, label: "{n["label"]}", route: "{n.get("route", "/")}" }}' for n in nav_items) + "]"
    sidebar_icons = ", ".join(n["icon"] for n in nav_items[:6])

    # Determine primary color from scraped colors
    primary_color = "#3b82f6"
    for c in colors:
        if c.startswith("#") and len(c) == 7 and c not in ("#ffffff", "#000000"):
            primary_color = c
            break

    # Bottom Nav
    _write_file(p, "src/components/layout/BottomNav.tsx", _BOTTOM_NAV_T % (icon_imports, nav_items_ts))

    # Sidebar
    _write_file(p, "src/components/layout/Sidebar.tsx", _SIDEBAR_T % (sidebar_icons, nav_items_ts, client))

    # Layout
    _write_file(p, "src/app/layout.tsx", _LAYOUT_T % (project_name, goal, project_name))

    # Globals CSS
    primary_hsl = _hex_to_hsl(primary_color)
    _write_file(p, "src/app/globals.css", _GLOBALS_CSS_T.replace("__PRIMARY__", primary_hsl).replace("__RING__", primary_hsl))

    # Categorize and structure content
    content_data = _categorize_texts(texts, sections_raw, client, animations)

    # Generate each route page
    for route, label in routes.items():
        page_content = _build_page_for_route(route, label, content_data, client, project_name)
        if route == "/":
            page_dir = p / "src/app"
        else:
            page_dir = p / "src/app" / route.strip("/")
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "page.tsx").write_text(_PAGE_T % json.dumps(page_content, ensure_ascii=False), encoding="utf-8")

    # PWA
    _write_file(p, "public/manifest.json", json.dumps({
        "name": project_name, "short_name": project_name[:15], "description": goal,
        "start_url": "/", "display": "standalone",
        "background_color": "#ffffff", "theme_color": primary_color,
        "icons": [{"src": "/icon-192.svg", "sizes": "192x192", "type": "image/svg+xml"},
                  {"src": "/icon-512.svg", "sizes": "512x512", "type": "image/svg+xml"}]
    }))
    _write_file(p, "public/sw.js", _SW_T)

    # Icons
    initials = "".join(w[0].upper() for w in client.split()[:2] if w)
    _write_file(p, "public/icon-192.svg", _SVG_192_T % primary_color)
    _write_file(p, "public/icon-512.svg", _SVG_512_T % primary_color)

    print(f"[WEBSITEAPP] Projeto gerado: {project_name}")
    print(f"[WEBSITEAPP] {len(texts)} textos, {len(animations)} animacoes, {len(colors)} cores, {len(routes)} paginas")


def _write_file(p, relpath, content):
    (p / relpath).write_text(content, encoding="utf-8")


def _deduplicate(texts):
    seen = set()
    result = []
    for t in texts:
        key = t.strip().lower()[:50]
        if key not in seen:
            seen.add(key)
            result.append(t)
    return result


def _categorize_texts(texts, sections_raw, client, animations):
    texts = _deduplicate(texts)
    categories = {
        "headlines": [],
        "features": [],
        "highlights": [],
        "long": [],
        "short": [],
        "cta": [],
        "stats": [],
        "all": [],
    }

    cta_keywords = ["comece", "saiba mais", "cadastre", "entre", "acesse", "assine", "compre", "contato", "whatsapp", "demonstracao", "demonstração"]
    stat_patterns = ["mil", "milh", "anos", "%", "numero", "mais de", "top", "r$", "500"]
    service_keywords = ["gestao", "gestão", "acesso", "integracao", "integração", "relatorio", "relatório", "suporte", "entrada", "saida", "saída"]
    plan_keywords = ["plano", "basico", "básico", "profissional", "enterprise", "sla"]

    for t in texts:
        t_stripped = t.strip()
        lower = t_stripped.lower()
        if len(t_stripped) < 3:
            continue
        categories["all"].append(t_stripped)
        if any(kw in lower for kw in plan_keywords):
            categories["features"].append(t_stripped)
        elif any(kw in lower for kw in service_keywords):
            categories["highlights"].append(t_stripped)
        elif any(kw in lower for kw in cta_keywords):
            categories["cta"].append(t_stripped)
        elif any(kw in lower for kw in stat_patterns):
            categories["stats"].append(t_stripped)
        elif len(t_stripped) > 80:
            categories["long"].append(t_stripped)
        elif len(t_stripped) > 35:
            categories["highlights"].append(t_stripped)
        else:
            categories["short"].append(t_stripped)

    if not categories["headlines"] and categories["all"]:
        categories["headlines"] = categories["all"][:2]

    return categories


def _content_paragraphs(content_data, max_items=40):
    """Garante que a maior parte dos textos apareca em paragrafos."""
    used = set()
    pool = []
    for key in ("long", "highlights", "short", "cta", "stats", "features", "all"):
        for t in content_data.get(key, []):
            k = t.strip().lower()
            if k not in used:
                used.add(k)
                pool.append(t)
    return pool[:max_items]


def _build_page_for_route(route, label, content_data, client, project_name):
    sections = []

    if route == "/":
        headline = content_data["all"][0] if content_data["all"] else f"Bem-vindo ao {client}"
        subtitle = content_data["all"][1] if len(content_data["all"]) > 1 else ""
        sections.append({"type": "hero", "title": headline, "text": subtitle, "className": "bg-gradient-to-br from-primary/5 via-background to-background"})

        if content_data["stats"]:
            stat_items = []
            for s in content_data["stats"][:4]:
                stat_items.append({"label": s[:40], "value": s[:20]})
            sections.append({"type": "stats", "items": stat_items, "className": ""})

        card_items = []
        seen_cards = set()
        for t in content_data["highlights"][:4] + content_data["headlines"][:4]:
            key = t.strip().lower()[:30]
            if key not in seen_cards:
                seen_cards.add(key)
                card_items.append({"title": t[:50], "text": t[:150]})
        if card_items:
            sections.append({"type": "cards", "items": card_items, "className": ""})

        cta_text = content_data["cta"][0] if content_data["cta"] else None
        if cta_text:
            sections.append({"type": "cta", "title": cta_text[:60], "text": cta_text, "button_label": "Saiba Mais", "button_url": "#contato", "className": "bg-muted/30"})
        elif content_data["headlines"]:
            sections.append({"type": "cta", "title": content_data["headlines"][0][:60], "text": content_data["headlines"][0], "button_label": "Saiba Mais", "button_url": "#contato", "className": "bg-muted/30"})

        paragraphs = _content_paragraphs(content_data, max_items=30)
        if paragraphs:
            sections.append({"type": "content", "paragraphs": paragraphs, "className": ""})

    elif route == "/servicos":
        sections.append({"type": "hero", "title": "Nossos Servicos", "text": "Conheca tudo o que oferecemos", "className": ""})
        card_items = []
        for t in content_data["highlights"][:8] + content_data["short"][:8] + content_data["features"][:6]:
            card_items.append({"title": t[:80], "text": t})
        if card_items:
            sections.append({"type": "cards", "items": card_items, "className": ""})
        svc_paras = _content_paragraphs(content_data, max_items=20)
        if svc_paras:
            sections.append({"type": "content", "paragraphs": svc_paras, "className": ""})

    elif route == "/planos":
        sections.append({"type": "hero", "title": "Planos e Precos", "text": "Escolha o plano ideal para voce", "className": ""})
        plan_texts = [t for t in content_data["features"] + content_data["all"] if "plano" in t.lower()]
        if not plan_texts:
            plan_texts = content_data["highlights"][:6]
        price_items = []
        if plan_texts:
            for i, t in enumerate(plan_texts[:3]):
                name = t.split(":")[0][:40] if ":" in t else f"Plano {i + 1}"
                price_items.append({
                    "name": name,
                    "price": "Sob consulta",
                    "features": [t[:120]],
                    "cta": "Contratar",
                })
        else:
            for name in ["Basico", "Profissional", "Enterprise"]:
                price_items.append({"name": name, "price": "Sob consulta", "features": [], "cta": "Contratar"})
        if price_items:
            sections.append({"type": "pricing", "plans": price_items, "className": ""})
        plan_paras = _content_paragraphs(content_data, max_items=15)
        if plan_paras:
            sections.append({"type": "content", "paragraphs": plan_paras, "className": ""})

    elif route == "/suporte":
        sections.append({"type": "hero", "title": "Fale Conosco", "text": "Estamos aqui para ajudar", "className": ""})
        sections.append({"type": "form", "fields": [{"name": "nome", "type": "text", "label": "Nome", "required": True}, {"name": "email", "type": "email", "label": "E-mail", "required": True}, {"name": "mensagem", "type": "textarea", "label": "Mensagem", "required": True}], "submit_label": "Enviar Mensagem", "className": "max-w-lg mx-auto"})
        sup_paras = content_data["cta"][:6] + _content_paragraphs(content_data, max_items=10)
        if sup_paras:
            sections.append({"type": "content", "paragraphs": sup_paras, "className": ""})

    elif route == "/conta":
        sections.append({"type": "hero", "title": "Minha Conta", "text": "Gerencie seu perfil e preferencias", "className": ""})
        sections.append({"type": "form", "fields": [{"name": "nome", "type": "text", "label": "Nome"}, {"name": "email", "type": "email", "label": "E-mail"}, {"name": "telefone", "type": "tel", "label": "Telefone"}], "submit_label": "Atualizar Cadastro", "className": "max-w-lg mx-auto"})

    sections.append({"type": "footer", "text": f"(c) 2026 {client}. Todos os direitos reservados.", "className": ""})
    return sections


def _full_text_blob_from_sections(sections: list) -> str:
    """Serializa secoes para checagem de preservacao (debug)."""
    parts = []
    for s in sections:
        for k in ("title", "text", "button_label"):
            if s.get(k):
                parts.append(str(s[k]))
        for item in s.get("items", []) or []:
            parts.extend([str(item.get("title", "")), str(item.get("text", ""))])
        for p in s.get("paragraphs", []) or []:
            parts.append(str(p))
        for plan in s.get("plans", []) or []:
            parts.append(str(plan.get("name", "")))
            parts.extend(plan.get("features", []) or [])
    return " ".join(parts)


def _hex_to_hsl(hex_color):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) < 6:
        return "221.2 83.2% 53.3%"
    try:
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    except ValueError:
        return "221.2 83.2% 53.3%"
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    h = s = 0
    l = (mx + mn) / 2
    if mx != mn:
        d = mx - mn
        s = d / (1 - abs(2 * l - 1))
        if mx == r:
            h = 60 * (((g - b) / d) % 6)
        elif mx == g:
            h = 60 * (((b - r) / d) + 2)
        else:
            h = 60 * (((r - g) / d) + 4)
    return f"{round(h)} {round(s * 100)}% {round(l * 100)}%"


# --- Template strings ---

_BOTTOM_NAV_T = """'use client'
import React, { useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { %s } from 'lucide-react'

const items: { icon: React.ElementType; label: string; route: string }[] = %s

export default function BottomNav() {
  const router = useRouter()
  const pathname = usePathname()
  const activeIndex = items.findIndex(i => i.route === pathname)
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 h-16 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 safe-area-bottom">
      <div className="flex items-center justify-around max-w-lg mx-auto h-full px-2">
        {items.map((item, i) => (
          <button key={i} onClick={() => router.push(item.route)}
            className={`flex flex-col items-center gap-0.5 px-3 py-1 rounded-xl transition-all duration-200
              ${activeIndex === i ? 'text-primary scale-110' : 'text-muted-foreground hover:text-foreground'}`}>
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
import { useRouter, usePathname } from 'next/navigation'
import { X, Menu, %s } from 'lucide-react'

const items: { icon: React.ElementType; label: string; route: string }[] = %s

export default function Sidebar() {
  const [open, setOpen] = useState(false)
  const router = useRouter()
  const pathname = usePathname()
  return (
    <>
      <button onClick={() => setOpen(true)}
        className="fixed top-4 left-4 z-50 p-2 rounded-xl bg-background/80 backdrop-blur border shadow-sm hover:bg-muted transition-colors">
        <Menu className="w-5 h-5" />
      </button>
      {open && <div className="fixed inset-0 bg-black/40 z-40" onClick={() => setOpen(false)} />}
      <aside className={"fixed top-0 left-0 h-full w-72 bg-background border-r z-50 transform transition-transform duration-300 shadow-2xl " + (open ? 'translate-x-0' : '-translate-x-full')}>
        <div className="flex items-center justify-between p-4 border-b">
          <span className="font-bold text-lg">%s</span>
          <button onClick={() => setOpen(false)} className="hover:bg-muted p-1 rounded-lg transition-colors"><X className="w-5 h-5" /></button>
        </div>
        <nav className="p-2">
          {items.map((item, i) => {
            const isActive = pathname === item.route
            return (
              <a key={i} href={item.route} onClick={(e) => { e.preventDefault(); router.push(item.route); setOpen(false) }}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-colors mb-1 ${isActive ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-muted text-foreground'}`}>
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </a>
            )
          })}
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
      <body className={inter.className + ' pb-16 md:pb-0 antialiased'}>
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
    --primary: __PRIMARY__;
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
    --ring: __RING__;
    --radius: 0.5rem;
  }
  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: __PRIMARY__;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: __RING__;
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
import { ArrowRight, CheckCircle } from 'lucide-react'

const sections: any = %s

export default function Page() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
      <Sidebar />
      <main className="max-w-5xl mx-auto px-4 pt-20 pb-24 md:pb-12">
        {sections.map((section: any, i: number) => (
          <section key={i} className={'mb-16 ' + (section.className || '')}>
            {section.type === 'hero' && (
              <header className="text-center mb-12 py-8">
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">{section.title}</h1>
                {section.text && <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">{section.text}</p>}
              </header>
            )}
            {section.type === 'cards' && section.items && (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {section.items.map((item: any, j: number) => (
                  <div key={j} className="group bg-card rounded-2xl p-6 shadow-sm border hover:shadow-lg hover:border-primary/20 transition-all duration-300">
                    <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                      <CheckCircle className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="font-semibold mb-2 text-lg">{item.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{item.text}</p>
                  </div>
                ))}
              </div>
            )}
            {section.type === 'content' && section.paragraphs && (
              <div className="max-w-3xl mx-auto">
                <div className="space-y-6">
                  {section.paragraphs.map((p, j) => (
                    <p key={j} className="text-muted-foreground leading-relaxed text-lg">{p}</p>
                  ))}
                </div>
              </div>
            )}
            {section.type === 'stats' && section.items && (
              <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
                {section.items.map((item, j) => (
                  <div key={j} className="bg-card rounded-xl border p-6 shadow-sm hover:shadow-md transition-shadow text-center">
                    <p className="text-2xl font-bold text-primary">{item.value}</p>
                    <p className="text-sm text-muted-foreground mt-1">{item.label}</p>
                  </div>
                ))}
              </div>
            )}
            {section.type === 'cta' && (
              <div className="rounded-2xl border bg-card p-8 md:p-12 text-center shadow-sm">
                <h2 className="text-2xl md:text-3xl font-bold mb-4">{section.title}</h2>
                {section.text && <p className="text-muted-foreground mb-8 max-w-xl mx-auto">{section.text}</p>}
                <a href={section.button_url || '#contato'}
                  className="inline-flex items-center gap-2 rounded-xl bg-primary px-8 py-3 text-sm font-medium text-primary-foreground shadow transition-all hover:bg-primary/90 hover:shadow-lg hover:scale-105 active:scale-100">
                  {section.button_label || 'Saiba Mais'}
                  <ArrowRight className="w-4 h-4" />
                </a>
              </div>
            )}
            {section.type === 'pricing' && section.plans && (
              <div className="grid gap-6 md:grid-cols-3">
                {section.plans.map((plan, j) => (
                  <div key={j} className={`bg-card rounded-xl border p-6 shadow-sm flex flex-col hover:shadow-lg transition-shadow ${j === 1 ? 'border-primary ring-1 ring-primary' : ''}`}>
                    {j === 1 && <span className="text-xs font-semibold text-primary bg-primary/10 px-3 py-1 rounded-full self-start mb-3">Mais Popular</span>}
                    <h3 className="text-lg font-semibold">{plan.name}</h3>
                    <p className="text-3xl font-bold mt-2">{plan.price}</p>
                    {plan.features && plan.features.length > 0 && (
                      <ul className="mt-4 space-y-2 flex-1">
                        {plan.features.map((feat, k) => (
                          <li key={k} className="text-sm text-muted-foreground flex items-start gap-2">
                            <CheckCircle className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                            {feat}
                          </li>
                        ))}
                      </ul>
                    )}
                    <a href={plan.cta_url || '#contato'} className="mt-6 inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground shadow transition-all hover:bg-primary/90 hover:shadow-md">
                      {plan.cta || 'Contratar'}
                    </a>
                  </div>
                ))}
              </div>
            )}
            {section.type === 'form' && section.fields && (
              <div className="max-w-lg mx-auto bg-card rounded-xl border p-8 shadow-sm">
                <form className="space-y-4">
                  {section.fields.map((f, j) => (
                    <div key={j}>
                      <label className="text-sm font-medium mb-1.5 block">{f.label}</label>
                      {f.type === 'textarea'
                        ? <textarea className="flex min-h-[100px] w-full rounded-lg border bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors" name={f.name} required={f.required} />
                        : <input type={f.type} className="flex h-10 w-full rounded-lg border bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors" name={f.name} required={f.required} />}
                    </div>
                  ))}
                  <button type="submit" className="inline-flex items-center justify-center rounded-lg bg-primary px-8 py-2.5 text-sm font-medium text-primary-foreground shadow transition-all hover:bg-primary/90 hover:shadow-md w-full">
                    {section.submit_label || 'Enviar'}
                  </button>
                </form>
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
