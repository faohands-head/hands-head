"""
Compiler Agent — Transforma AppIR em código Next.js via templates
ZERO LLM — 100% template engine. Custo: R$ 0,00
Saída em JavaScript puro (LLM-friendly), sem TypeScript.
"""
import os, sys, json, uuid, textwrap
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from schemas.ir import AppIR

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = ROOT / "templates"
PROJECTS_DIR = ROOT / "projects"


def compile_ir(ir: AppIR, output_dir: str | None = None) -> str:
    if output_dir is None:
        project_id = f"app-{ir.name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:8]}"
        output_dir = str(PROJECTS_DIR / project_id)

    p = Path(output_dir)
    p.mkdir(parents=True, exist_ok=True)
    for d in ["src/app", "src/components", "src/lib", "public"]:
        (p / d).mkdir(parents=True, exist_ok=True)

    _write_package_json(p, ir)
    _write_config_files(p)
    _write_layout(p, ir)
    _write_pages(p, ir)
    _write_entities(p, ir)
    _write_globals_css(p, ir)
    _write_manifest(p, ir)

    print(f"[COMPILER] Projeto gerado: {output_dir}")
    print(f"[COMPILER] {len(ir.pages)} páginas, {len(ir.entities)} entidades")
    return output_dir


def _write_package_json(p: Path, ir: AppIR):
    deps = {
        "next": "^15.2.0", "react": "^19.0.0", "react-dom": "^19.0.0",
        "lucide-react": "^0.400.0",
    }
    if ir.auth.provider != "none":
        deps["@supabase/supabase-js"] = "^2.45.0"
        deps["@supabase/ssr"] = "^0.5.0"

    dev_deps = {
        "tailwindcss": "^3.4.17",
        "postcss": "^8.4.49",
        "autoprefixer": "^10.4.20",
    }
    (p / "package.json").write_text(json.dumps({
        "name": ir.name.lower().replace(" ", "-"),
        "version": "0.1.0", "private": True,
        "scripts": {"dev": "next dev", "build": "next build", "start": "next start"},
        "dependencies": deps,
        "devDependencies": dev_deps,
    }, indent=2))


def _write_config_files(p: Path):
    (p / "next.config.mjs").write_text("""/** @type {import('next').NextConfig} */
const nextConfig = { output: 'export', images: { unoptimized: true }, trailingSlash: true }
export default nextConfig
""")
    (p / "tailwind.config.js").write_text("""/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
        secondary: { DEFAULT: "hsl(var(--secondary))", foreground: "hsl(var(--secondary-foreground))" },
        destructive: { DEFAULT: "hsl(var(--destructive))", foreground: "hsl(var(--destructive-foreground))" },
        muted: { DEFAULT: "hsl(var(--muted))", foreground: "hsl(var(--muted-foreground))" },
        accent: { DEFAULT: "hsl(var(--accent))", foreground: "hsl(var(--accent-foreground))" },
        popover: { DEFAULT: "hsl(var(--popover))", foreground: "hsl(var(--popover-foreground))" },
        card: { DEFAULT: "hsl(var(--card))", foreground: "hsl(var(--card-foreground))" },
      },
      borderRadius: { lg: "var(--radius)", md: "calc(var(--radius) - 2px)", sm: "calc(var(--radius) - 4px)" },
    },
  },
  plugins: [],
}
""")
    (p / "postcss.config.js").write_text("""module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""")
    (p / "jsconfig.json").write_text("""{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  }
}
""")


def _write_globals_css(p: Path, ir: AppIR):
    primary = ir.theme.get("primary", "#3b82f6")
    prim = _hex_to_hsl(primary)
    ring = _hex_to_hsl(primary)
    radius = ir.theme.get("radius", "0.5rem")
    (p / "src/app/globals.css").write_text(f"""@tailwind base;
@tailwind components;
@tailwind utilities;
@layer base {{
  :root {{
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: {prim};
    --primary-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --ring: {ring};
    --radius: {radius};
  }}
}}
""")


def _write_layout(p: Path, ir: AppIR):
    (p / "src/app/layout.js").write_text(f"""export const metadata = {{
  title: '{ir.name}',
  description: '{ir.description}',
}}

export default function RootLayout({{ children }}) {{
  return <html lang="pt-BR"><body>{{children}}</body></html>
}}
""")


def _write_pages(p: Path, ir: AppIR):
    for page in ir.pages:
        route = page.route.strip("/") or "page"
        if page.route == "/":
            page_dir = p / "src/app"
        else:
            page_dir = p / "src/app" / route
        page_dir.mkdir(parents=True, exist_ok=True)

        (page_dir / "page.js").write_text(_render_page(page, ir))


def _render_page(page, ir) -> str:
    components_code = []
    for section in page.sections:
        for comp in section.components:
            code = _render_component(comp)
            if code:
                components_code.append(textwrap.indent(code, "      "))

    all_code = "\n\n".join(components_code)
    icons_import = _get_icons(page)
    auth_import = _get_auth_imports(ir)
    return f"""'use client'
import React from 'react'
{icons_import}{auth_import}export default function {page.title.replace(" ", "")}() {{
  return (
    <main className="min-h-screen bg-background">
{all_code}
    </main>
  )
}}
"""


def _get_icons(page) -> str:
    icons = set()
    for section in page.sections:
        for comp in section.components:
            for item in comp.props.get("items", []):
                if item.get("icon"):
                    icons.add(item["icon"])
    if not icons:
        return ""
    return f"import {{ {', '.join(sorted(icons))} }} from 'lucide-react'\n"


def _get_auth_imports(ir) -> str:
    if ir.auth.provider != "none":
        return 'import { useSession } from "@/lib/auth"\n'
    return ""


def _render_component(comp) -> str:
    p = comp.props
    t = comp.type
    out = []

    if t == "hero":
        out.append('<section className="text-center py-20 px-4">')
        out.append(f'  <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">{p.get("title", "Title")}</h1>')
        if p.get("subtitle"):
            out.append(f'  <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">{p["subtitle"]}</p>')
        if p.get("cta"):
            url = p.get("cta_url", "#")
            out.append(f'  <a href="{url}" className="inline-flex items-center justify-center rounded-lg bg-primary px-8 py-3 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90">{p["cta"]}</a>')
        out.append('</section>')

    elif t == "card-grid":
        items = p.get("items", [])
        cols = {1: "md:grid-cols-1", 2: "md:grid-cols-2", 3: "md:grid-cols-3", 4: "md:grid-cols-4"}.get(p.get("columns", 3), "md:grid-cols-3")
        out.append('<section className="max-w-5xl mx-auto px-4 py-12">')
        out.append(f'  <div className="grid gap-6 {cols}">')
        for i, item in enumerate(items):
            card = f'<div key={{{i}}} className="bg-card rounded-xl p-6 border shadow-sm hover:shadow-md transition-shadow">'
            if item.get("icon"):
                icon = item["icon"]
                card += '<div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-3">'
                card += f'{{React.createElement({icon}, {{className: "w-5 h-5 text-primary"}})}}'
                card += '</div>'
            card += f'<h3 className="font-semibold mb-2">{item["title"]}</h3>'
            card += f'<p className="text-sm text-muted-foreground">{item.get("text", "")}</p>'
            card += '</div>'
            out.append(f'    {card}')
        out.append('  </div>')
        out.append('</section>')

    elif t == "data-table":
        cols_def = p.get("columns", [{"key": "name", "label": "Nome"}])
        rows = p.get("rows", [])
        out.append('<section className="max-w-5xl mx-auto px-4 py-12">')
        out.append('  <div className="rounded-xl border bg-card overflow-hidden">')
        out.append('    <table className="w-full">')
        thead = '<thead><tr className="border-b bg-muted/50">'
        for c in cols_def:
            thead += f'<th className="text-left p-4 text-sm font-medium">{c["label"]}</th>'
        thead += '</tr></thead>'
        out.append(f'      {thead}')
        if rows:
            tbody = '<tbody>'
            for row in rows[:20]:
                tbody += '<tr className="border-b last:border-0 hover:bg-muted/30">'
                for c in cols_def:
                    val = row.get(c["key"], "")
                    tbody += f'<td className="p-4 text-sm">{val}</td>'
                tbody += '</tr>'
            tbody += '</tbody>'
        else:
            tbody = '<tbody><tr><td colSpan={99} className="p-8 text-center text-muted-foreground">Nenhum registro encontrado</td></tr></tbody>'
        out.append(f'      {tbody}')
        out.append('    </table>')
        out.append('  </div>')
        out.append('</section>')

    elif t == "form":
        fields = p.get("fields", [])
        out.append('<section className="max-w-xl mx-auto px-4 py-12">')
        out.append('  <form className="bg-card rounded-xl border p-6 space-y-4 shadow-sm">')
        out.append(f'    <h2 className="text-xl font-semibold mb-4">{p.get("submit_label", "Formul\u00e1rio")}</h2>')
        for f in fields:
            fname = f.get("name", "field")
            flabel = f.get("label", fname)
            ftype = f.get("type", "text")
            required = " required" if f.get("required") else ""
            iclass = 'className="flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"'
            out.append(f'    <div key="{fname}">')
            out.append(f'      <label className="text-sm font-medium mb-1 block">{flabel}</label>')
            if ftype == "textarea":
                out.append(f'      <textarea {iclass} name="{fname}"{required}></textarea>')
            else:
                out.append(f'      <input type="{ftype}" {iclass} name="{fname}"{required} />')
            out.append('    </div>')
        out.append(f'    <button type="submit" className="inline-flex items-center justify-center rounded-lg bg-primary px-8 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90">{p.get("submit_label", "Enviar")}</button>')
        out.append('  </form>')
        out.append('</section>')

    elif t == "stats":
        items = p.get("items", [])
        out.append('<section className="max-w-5xl mx-auto px-4 py-8">')
        out.append('  <div className="grid gap-4 grid-cols-2 md:grid-cols-4">')
        for item in items:
            stat = '<div className="bg-card rounded-xl border p-4 shadow-sm">'
            stat += f'<p className="text-sm text-muted-foreground">{item["label"]}</p>'
            stat += f'<p className="text-2xl font-bold mt-1">{item["value"]}</p>'
            if item.get("change"):
                stat += f'<span className="text-xs text-green-600">{item["change"]}</span>'
            stat += '</div>'
            out.append(f'    {stat}')
        out.append('  </div>')
        out.append('</section>')

    elif t == "chart":
        data = p.get("data", [])
        max_val = max((d.get("value", 0) for d in data), default=1)
        out.append('<section className="max-w-3xl mx-auto px-4 py-12">')
        out.append('  <div className="bg-card rounded-xl border p-6 shadow-sm">')
        out.append(f'    <h3 className="font-semibold mb-4">{p.get("title", "Gr\u00e1fico")}</h3>')
        out.append('    <div className="flex items-end justify-center gap-4 h-32">')
        for d in data:
            h = d["value"] / max_val * 120
            h_inner = d["value"] / max_val * 100
            out.append('      <div className="flex flex-col items-center gap-1">')
            out.append(f'        <div className="w-8 bg-primary/20 rounded-t" style={{{{height: "{h}px"}}}}>')
            out.append(f'          <div className="w-full bg-primary rounded-t" style={{{{height: "{h_inner}%"}}}}></div>')
            out.append('        </div>')
            out.append(f'        <span className="text-xs text-muted-foreground">{d["label"]}</span>')
            out.append('      </div>')
        out.append('    </div>')
        out.append('  </div>')
        out.append('</section>')

    elif t == "features":
        items = p.get("items", [])
        out.append('<section className="max-w-5xl mx-auto px-4 py-12">')
        out.append('  <div className="grid gap-8 md:grid-cols-3">')
        for item in items:
            feat = '<div className="text-center">'
            if item.get("icon"):
                icon = item["icon"]
                feat += f'<div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-4">{{<{icon} className="w-6 h-6 text-primary" />}}</div>'
            feat += f'<h3 className="font-semibold mb-2">{item["title"]}</h3>'
            feat += f'<p className="text-sm text-muted-foreground">{item.get("text", "")}</p>'
            feat += '</div>'
            out.append(f'    {feat}')
        out.append('  </div>')
        out.append('</section>')

    elif t == "cta":
        out.append('<section className="text-center py-16 px-4 bg-muted/30">')
        out.append(f'  <h2 className="text-3xl font-bold mb-4">{p.get("title", "Pronto para come\u00e7ar?")}</h2>')
        if p.get("text"):
            out.append(f'  <p className="text-muted-foreground mb-8 max-w-xl mx-auto">{p["text"]}</p>')
        url = p.get("button_url", "#")
        label = p.get("button_label", "Come\u00e7ar")
        out.append(f'  <a href="{url}" className="inline-flex items-center justify-center rounded-lg bg-primary px-8 py-3 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90">{label}</a>')
        out.append('</section>')

    elif t == "pricing":
        plans = p.get("plans", [])
        out.append('<section className="max-w-5xl mx-auto px-4 py-12">')
        ncols = min(len(plans), 3) if plans else 1
        out.append(f'  <div className="grid gap-6 md:grid-cols-{ncols}">')
        for plan in plans:
            card = '<div className="bg-card rounded-xl border p-6 shadow-sm flex flex-col">'
            card += f'<h3 className="text-lg font-semibold">{plan["name"]}</h3>'
            card += f'<p className="text-3xl font-bold mt-2">{plan["price"]}</p>'
            features = plan.get("features", [])
            if features:
                card += '<ul className="mt-4 space-y-2 flex-1">'
                for feat in features:
                    card += f'<li className="text-sm text-muted-foreground">\u2713 {feat}</li>'
                card += '</ul>'
            card += f'<a href="#" className="mt-6 inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90">{plan.get("cta", "Assinar")}</a>'
            card += '</div>'
            out.append(f'    {card}')
        out.append('  </div>')
        out.append('</section>')

    elif t == "content":
        paragraphs = p.get("paragraphs", [])
        out.append('<section className="max-w-3xl mx-auto px-4 py-12">')
        out.append('  <div className="prose prose-gray max-w-none">')
        for par in paragraphs:
            out.append(f'    <p className="text-muted-foreground mb-4">{par}</p>')
        out.append('  </div>')
        out.append('</section>')

    elif t == "section-header":
        align = p.get("alignment", "center")
        al_cls = "text-center" if align == "center" else "text-left"
        out.append(f'<div className="{al_cls} mb-8">')
        out.append(f'  <h2 className="text-3xl font-bold">{p.get("title", "Se\u00e7\u00e3o")}</h2>')
        if p.get("subtitle"):
            out.append(f'  <p className="text-muted-foreground mt-2">{p["subtitle"]}</p>')
        out.append('</div>')

    elif t == "navbar":
        links = p.get("links", [])
        brand = p.get("brand", "Brand")
        out.append('<nav className="sticky top-0 z-50 bg-background/80 backdrop-blur border-b">')
        out.append('  <div className="max-w-5xl mx-auto flex items-center justify-between px-4 h-14">')
        out.append(f'    <span className="font-bold">{brand}</span>')
        out.append('    <div className="flex gap-6">')
        for link in links:
            out.append(f'      <a href="{link["url"]}" className="text-sm text-muted-foreground hover:text-foreground transition-colors">{link["label"]}</a>')
        out.append('    </div>')
        out.append('  </div>')
        out.append('</nav>')

    elif t == "footer":
        links = p.get("links", [])
        text = p.get("text", "\u00a9 2026")
        out.append('<footer className="border-t py-8 mt-12">')
        out.append('  <div className="max-w-5xl mx-auto px-4 text-center text-sm text-muted-foreground">')
        for link in links:
            out.append(f'    <a href="{link["url"]}" className="text-sm text-muted-foreground hover:text-foreground">{link["label"]}</a>')
        out.append(f'    <p className="inline">{text}</p>')
        out.append('  </div>')
        out.append('</footer>')

    return "\n".join(out)


def _write_entities(p: Path, ir: AppIR):
    if not ir.entities:
        return
    if ir.datasource.type == "supabase":
        _write_supabase_client(p, ir)
    for entity in ir.entities:
        _write_api_route(p, entity)


def _write_supabase_client(p: Path, ir: AppIR):
    (p / "src/lib/auth.js").write_text("""import { createBrowserClient } from '@supabase/ssr'

const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

export function useSession() {
  return { user: null, loading: false }
}
""")


def _write_api_route(p: Path, entity):
    name = entity.name.lower()
    (p / "src/app/api" / name).mkdir(parents=True, exist_ok=True)
    (p / "src/app/api" / name / "route.js").write_text(f"""import {{ NextResponse }} from 'next/server'

const items = []

export async function GET() {{
  return NextResponse.json(items)
}}

export async function POST(request) {{
  const body = await request.json()
  const item = {{ id: crypto.randomUUID(), ...body, created_at: new Date().toISOString() }}
  items.push(item)
  return NextResponse.json(item, {{ status: 201 }})
}}
""")


def _write_manifest(p: Path, ir: AppIR):
    primary = ir.theme.get("primary", "#3b82f6")
    (p / "public").mkdir(parents=True, exist_ok=True)
    (p / "public/manifest.json").write_text(json.dumps({
        "name": ir.name, "short_name": ir.name[:15],
        "start_url": "/", "display": "standalone",
        "background_color": "#ffffff", "theme_color": primary,
        "icons": [{"src": "/icon.svg", "sizes": "192x192", "type": "image/svg+xml"}]
    }))


def _hex_to_hsl(hex_color: str) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
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
