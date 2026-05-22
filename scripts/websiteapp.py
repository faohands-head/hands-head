#!/usr/bin/env python3
"""
FAO HANDS - WebsiteApp Command
Uso:
  python scripts/websiteapp.py --url https://site-do-cliente.com.br/
  python scripts/websiteapp.py --from-brain briefing-cliente.md

Pipeline: Scraper -> Gerar Projeto -> npm install -> Preview -> Obsidian Report
"""
import os, sys, json, uuid, subprocess, argparse
from pathlib import Path

CAID_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = CAID_DIR / "projects"
SCRIPTS_DIR = CAID_DIR / "scripts"
TEMPLATES_DIR = CAID_DIR / "templates"
VAULT_DIR = CAID_DIR / "vault"

sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(TEMPLATES_DIR))

from website_scraper import SiteScraper
from brain import Brain


def load_briefing(filename: str) -> dict:
    """Carrega briefing do Obsidian vault"""
    brain = Brain()
    content = brain.read(f"briefings/{filename}")
    if not content:
        print(f"[WEBSITEAPP] Briefing nao encontrado: briefings/{filename}")
        sys.exit(1)

    # Parse frontmatter
    spec = {"title": filename.replace(".md", "").replace("-", " ").title(), "client": "Cliente"}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    spec[k.strip()] = v.strip()
            content = parts[2]

    # Extract first meaningful lines as texts
    lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("#") and not l.startswith("-")]
    # Extract URL if present
    for line in content.split("\n"):
        if "https://" in line:
            url_match = [w for w in line.split() if w.startswith("https://")]
            if url_match:
                spec["url"] = url_match[0]
                break

    spec["goal"] = f"WebsiteApp: {spec.get('title', '')}"
    spec["project_name"] = f"WebsiteApp {spec.get('cliente', spec.get('title', ''))}"
    spec["extracted"] = {"texts": lines[:50], "colors": [], "fonts": [], "animations": [], "animations_raw": {}, "sections": []}
    spec["struct"] = {"text_count": len(lines)}
    spec["nav_items"] = [
        {"icon": "Home", "label": "Inicio"},
        {"icon": "Briefcase", "label": "Servicos"},
        {"icon": "CreditCard", "label": "Planos"},
        {"icon": "Headphones", "label": "Suporte"},
        {"icon": "User", "label": "Conta"},
    ]
    print(f"[WEBSITEAPP] Briefing carregado: {filename} ({len(lines)} linhas)")
    return spec


def generate_project(spec):
    """Gera o projeto Next.js com template websiteapp"""
    domain = spec.get("domain", spec.get("url", "cliente").replace("https://", "").split("/")[0])
    project_id = f"websiteapp-{domain.replace('.', '-')}-{uuid.uuid4().hex[:8]}"
    project_dir = PROJECTS_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    project_name = spec.get("project_name", "WebsiteApp")

    # Package.json
    (project_dir / "package.json").write_text(json.dumps({
        "name": project_name, "version": "0.1.0", "private": True,
        "scripts": {"dev": "next dev", "build": "next build", "start": "next start", "lint": "next lint"},
        "dependencies": {
            "next": "^14.2.0", "react": "^18.3.0", "react-dom": "^18.3.0",
            "lucide-react": "^0.400.0", "class-variance-authority": "^0.7.0",
            "clsx": "^2.1.0", "tailwind-merge": "^2.3.0", "tailwindcss-animate": "^1.0.7",
            "@radix-ui/react-slot": "^1.0.2", "@radix-ui/react-dialog": "^1.0.5",
            "@radix-ui/react-dropdown-menu": "^2.0.6",
        },
        "devDependencies": {
            "@types/node": "^20.0.0", "@types/react": "^18.3.0",
            "@types/react-dom": "^18.3.0", "typescript": "^5.4.0",
            "tailwindcss": "^3.4.0", "postcss": "^8.4.0", "autoprefixer": "^10.4.0",
        }
    }, indent=2))

    # Config files
    (project_dir / "tsconfig.json").write_text('{"compilerOptions":{"target":"es5","lib":["dom","dom.iterable","esnext"],"allowJs":true,"skipLibCheck":true,"strict":true,"noEmit":true,"esModuleInterop":true,"module":"esnext","moduleResolution":"bundler","resolveJsonModule":true,"isolatedModules":true,"jsx":"preserve","incremental":true,"plugins":[{"name":"next"}],"paths":{"@/*":["./src/*"]}},"include":["next-env.d.ts","**/*.ts","**/*.tsx",".next/types/**/*.ts"],"exclude":["node_modules"]}')
    (project_dir / "next.config.mjs").write_text("""/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: { unoptimized: true },
  trailingSlash: true,
}
export default nextConfig
""")
    (project_dir / "postcss.config.js").write_text("module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }")
    (project_dir / "tailwind.config.ts").write_text(_TAILWIND_CONFIG)
    (project_dir / "next-env.d.ts").write_text('/// <reference types="next" />\n/// <reference types="next/image-types/global" />\n')

    # Components via template
    from websiteapp_template import add_to_project
    add_to_project(str(project_dir), spec)

    print(f"[WEBSITEAPP] Projeto criado: {project_dir}")
    return project_dir


def install_and_preview(project_dir):
    """Instala dependencias e inicia preview"""
    print("\n[WEBSITEAPP] Instalando dependencias...")
    r = subprocess.run("npm install --legacy-peer-deps", cwd=project_dir, shell=True, capture_output=True, text=True, timeout=120)
    if r.returncode == 0:
        print("[WEBSITEAPP] npm install OK")
    else:
        print(f"[WEBSITEAPP] npm install AVISO: {r.stderr[:300]}")

    print(f"\n[WEBSITEAPP] Preview: http://localhost:3001")
    print(f"[WEBSITEAPP] Comando: cd {project_dir} && npm run dev")


def save_obsidian(spec, project_dir):
    """Salva relatorio + spec no Obsidian"""
    from datetime import date
    brain = Brain()
    today = str(date.today())
    client = spec.get("client", spec.get("url", "Cliente"))
    pname = spec.get("project_name", "WebsiteApp")
    texts = spec.get("extracted", {}).get("texts", [])

    report = f"""---
tipo: report
operacao: websiteapp
cliente: {client}
url: {spec.get('url', '')}
status: gerado
created: {today}
---

# Report: {pname}

## Origem
- URL: {spec.get('url', 'N/A')}
- Briefing: {spec.get('_briefing', 'N/A')}

## Extracao
- Textos extraidos: {len(texts)}
- Cores: {len(spec.get('extracted', {}).get('colors', []))}
- Fontes: {len(spec.get('extracted', {}).get('fonts', []))}
- Animacoes CSS: {len(spec.get('extracted', {}).get('animations', []))}

## Projeto
- Diretorio: `{project_dir}`
- Preview: `http://localhost:3001`

## Textos Extraidos
{chr(10).join('- ' + t[:100] for t in texts[:20])}
"""
    report_name = f"reports/WebsiteApp {pname}-{today}.md"
    brain.write(report_name, report)
    print(f"[WEBSITEAPP] Relatorio: {report_name}")


def main():
    parser = argparse.ArgumentParser(description="FAO HANDS - WebsiteApp Generator")
    parser.add_argument("--url", help="URL do site do cliente")
    parser.add_argument("--from-brain", help="Nome do briefing no Obsidian (vault/briefings/)")
    parser.add_argument("--no-install", action="store_true", help="Pula npm install")
    args = parser.parse_args()

    if not args.url and not args.from_brain:
        parser.print_help()
        print("\nInforme --url ou --from-brain")
        sys.exit(1)

    print("=" * 50)
    print("  FAO HANDS - WebsiteApp Operation")
    print("=" * 50)

    if args.from_brain:
        spec = load_briefing(args.from_brain)
        spec["_briefing"] = args.from_brain
    else:
        print(f"\nURL: {args.url}")
        s = SiteScraper(args.url)
        spec = s.scrape_all()
        if not spec:
            print("[WEBSITEAPP] ERRO: Nao foi possivel extrair o site")
            sys.exit(1)
        if spec.get("blocked"):
            print(f"\n[WEBSITEAPP] O site {args.url} bloqueou a extracao (Cloudflare/WAF).")
            print(f"[WEBSITEAPP] O projeto sera gerado com dados parciais.")
            print(f"[WEBSITEAPP] Para resultado completo, use: --from-brain briefing-cliente.md")
            choice = input("Deseja continuar mesmo assim? (s/N): ")
            if choice.lower() != "s":
                print("[WEBSITEAPP] Abortado. Crie um briefing no Obsidian e use --from-brain.")
                sys.exit(0)

    print("\n--- Gerando Projeto ---")
    project_dir = generate_project(spec)

    if not args.no_install:
        print("\n--- Instalando Dependencias ---")
        install_and_preview(project_dir)

    print("\n--- Obsidian ---")
    save_obsidian(spec, project_dir)

    print("\n" + "=" * 50)
    print("  PRONTO!")
    print("=" * 50)
    print(f"\n  Projeto: {project_dir}")
    print(f"  Preview: cd {project_dir} && npm run dev")
    print(f"  http://localhost:3001\n")


_TAILWIND_CONFIG = """import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
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
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
export default config
"""

if __name__ == "__main__":
    main()
