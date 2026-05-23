#!/usr/bin/env python3
"""
FAO HANDS - WebsiteApp Command
Uso:
  python scripts/websiteapp.py --url https://site-do-cliente.com.br/
  python scripts/websiteapp.py --from-brain briefing-cliente.md
  python scripts/websiteapp.py --prompt "crie um app de tarefas"

Pipeline: Scraper -> Gerar Projeto -> npm install -> Preview -> Obsidian Report
Modo --prompt: Prompt -> Planner -> Builder -> Compiler -> Build -> Deploy
"""
import os, sys, json, uuid, subprocess, argparse, time, shutil
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
from agents.websiteapp_ir import (
    run_pipeline,
    is_websiteapp_plan,
    plan_from_prompt_plan,
    build_plan_from_spec,
    save_ir,
    ir_slug_from_spec,
)

BRIEFING_BY_DOMAIN = {
    "acessosvipclientes.com.br": "acessosvip-websiteapp.md",
}


def _merge_texts_into_spec(spec: dict, extra_texts: list[str]) -> dict:
    """Une textos ao spec sem duplicar (briefing + scrape)."""
    extracted = spec.setdefault("extracted", {})
    current = extracted.get("texts", [])
    seen = {t.strip().lower() for t in current if t and t.strip()}
    merged = list(current)
    for t in extra_texts:
        t = (t or "").strip()
        if not t or len(t) < 4:
            continue
        key = t.lower()
        if key not in seen:
            seen.add(key)
            merged.append(t)
    extracted["texts"] = merged
    spec["extracted"] = extracted
    return spec


def _briefing_lines_from_content(content: str) -> list[str]:
    lines = []
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-"):
            lines.append(line.lstrip("- ").strip())
        elif ":" not in line or line.startswith("http"):
            lines.append(line)
    return lines


def load_briefing(filename: str, merge_url: bool = True) -> dict:
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

    lines = _briefing_lines_from_content(content)
    for line in content.split("\n"):
        if "https://" in line:
            url_match = [w for w in line.split() if w.startswith("https://")]
            if url_match:
                spec["url"] = url_match[0]
                break

    spec["goal"] = f"WebsiteApp: {spec.get('title', '')}"
    spec["project_name"] = f"WebsiteApp {spec.get('cliente', spec.get('title', ''))}"
    spec["client"] = spec.get("cliente", spec.get("client", "Cliente"))
    spec["extracted"] = {"texts": lines, "colors": [], "fonts": [], "animations": [], "animations_raw": {}, "sections": []}
    spec["struct"] = {"text_count": len(lines), "source": "briefing"}
    spec["_briefing"] = filename

    if merge_url and spec.get("url"):
        print(f"[WEBSITEAPP] Mesclando scrape de {spec['url']}...")
        scraper = SiteScraper(spec["url"])
        scraped = scraper.scrape_all()
        if scraped and not scraped.get("blocked"):
            scrape_texts = scraped.get("extracted", {}).get("texts", [])
            if scraped.get("hosting_placeholder"):
                print("[WEBSITEAPP] Scrape ignorado (placeholder hospedagem); briefing prevalece.")
            else:
                _merge_texts_into_spec(spec, scrape_texts)
                for k in ("colors", "fonts", "animations", "animations_raw", "sections"):
                    if scraped.get("extracted", {}).get(k):
                        spec["extracted"][k] = scraped["extracted"][k]
                spec["struct"]["scrape_method"] = scraped.get("struct", {}).get("method")
    spec["nav_items"] = [
        {"icon": "Home", "label": "Inicio", "route": "/"},
        {"icon": "Briefcase", "label": "Servicos", "route": "/servicos"},
        {"icon": "CreditCard", "label": "Planos", "route": "/planos"},
        {"icon": "Headphones", "label": "Suporte", "route": "/suporte"},
        {"icon": "User", "label": "Conta", "route": "/conta"},
    ]
    print(f"[WEBSITEAPP] Briefing carregado: {filename} ({len(lines)} linhas)")
    return spec


def generate_project(spec, out_dir: str | None = None):
    """Gera o projeto Next.js com template websiteapp"""
    if out_dir:
        rel = Path(out_dir)
        if rel.is_absolute():
            project_dir = rel
        else:
            parts = rel.parts
            if parts and parts[0].lower() == "projects":
                rel = Path(*parts[1:])
            project_dir = PROJECTS_DIR / rel
        project_dir.mkdir(parents=True, exist_ok=True)
        for sub in ("src", "public"):
            sub_path = project_dir / sub
            if sub_path.exists():
                shutil.rmtree(sub_path)
    else:
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
            "next": "^15.2.0", "react": "^19.0.0", "react-dom": "^19.0.0",
            "lucide-react": "^0.400.0",
            "framer-motion": "^11.15.0",
        },
        "devDependencies": {
            "typescript": "^5.8.2",
            "@types/react": "^19.0.0",
            "@types/node": "^20.0.0"
        }
    }, indent=2))

    # Config files
    (project_dir / "next.config.mjs").write_text("""const nextConfig = {
  output: 'export',
  images: { unoptimized: true },
  trailingSlash: true,
}
export default nextConfig
""")
    (project_dir / "tsconfig.json").write_text("""{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": false,
    "noEmit": true,
    "incremental": true,
    "module": "esnext",
    "esModuleInterop": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] },
    "plugins": [{ "name": "next" }]
  },
  "include": ["next-env.d.ts", ".next/types/**/*.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
""")
    (project_dir / "tailwind.config.js").write_text("""/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
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
    (project_dir / "postcss.config.js").write_text("""module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""")
    # Add Tailwind deps to package.json
    pkg = json.loads((project_dir / "package.json").read_text())
    pkg["devDependencies"]["tailwindcss"] = "^3.4.17"
    pkg["devDependencies"]["postcss"] = "^8.4.49"
    pkg["devDependencies"]["autoprefixer"] = "^10.4.20"
    (project_dir / "package.json").write_text(json.dumps(pkg, indent=2))

    # Components via template
    try:
        sys.path.insert(0, str(TEMPLATES_DIR))
        from websiteapp_template import add_to_project
        add_to_project(str(project_dir), spec)
    except Exception as e:
        print(f"[WEBSITEAPP] AVISO: Template parcialmente aplicado ({e})")

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

    ir_path = spec.get("_ir_saved", spec.get("_ir_path", "N/A"))
    report = f"""---
tipo: report
operacao: websiteapp
cliente: {client}
url: {spec.get('url', '')}
status: gerado
ir_version: {spec.get('ir_version', '1.0.0')}
created: {today}
---

# Report: {pname}

## Origem
- URL: {spec.get('url', 'N/A')}
- Briefing: {spec.get('_briefing', 'N/A')}
- IR: `{ir_path}`

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


def update_manifest(spec, project_dir):
    """Adiciona projeto ao manifest projects.json"""
    from datetime import date
    manifest_path = CAID_DIR / "projects" / "projects.json"
    pname = spec.get("project_name", "WebsiteApp")
    slug = project_dir.name
    client = spec.get("client", pname)
    entry = {
        "name": client,
        "slug": slug,
        "url": f"https://faohands-head.github.io/hands-head/previews/{slug}/",
        "status": "built",
        "created": str(date.today()),
        "source": "briefing" if spec.get("_briefing") else "scraper",
    }
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    else:
        manifest = {"projects": []}
    # Remove duplicatas pelo slug
    manifest["projects"] = [p for p in manifest["projects"] if p.get("slug") != slug]
    manifest["projects"].append(entry)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"[WEBSITEAPP] Manifest atualizado: {slug}")


def generate_from_prompt(prompt_text: str, no_install=False, out_dir: str | None = None, strict: bool = False):
    """Pipeline: Prompt -> Planner -> Builder -> Compiler | WebsiteApp IR"""
    from agents.planner import plan as planner_plan
    from agents.builder import build as builder_build
    from agents.compiler import compile_ir

    print("\n[1/4] PLANNER (Intent): Decompondo prompt...")
    plan_dict = planner_plan(prompt_text)
    print(f"  Nome: {plan_dict.get('name')}")
    print(f"  Tipo: {plan_dict.get('type')}")
    print(f"  Tasks: {len(plan_dict.get('tasks', []))}")
    print(f"  Paginas: {len(plan_dict.get('pages', []))}")
    print(f"  Auth: {plan_dict.get('has_auth')}")
    print(f"  DB: {plan_dict.get('has_database')}")

    if is_websiteapp_plan(plan_dict):
        print("\n[2-4/4] WEBSITEAPP IR: Plan -> Structure -> Render (sem LLM builder)")
        wp = plan_from_prompt_plan(plan_dict, prompt_text)
        spec = {
            "project_name": wp["name"],
            "client": wp["client"],
            "goal": wp["description"],
            "extracted": {"texts": wp["content_texts"], "colors": [], "fonts": [], "animations": [], "sections": []},
            "nav_items": wp["nav_items"],
            "struct": {"source": "prompt"},
        }
        ir, ir_path = run_pipeline(spec, out_dir=out_dir)
        project_dir = generate_project(spec, out_dir=out_dir)
        if strict:
            from validate_preservation import measure
            r = measure("", Path(project_dir), source_texts=ir.source_texts)
            print(f"\n[WEBSITEAPP] Preservacao: {r['percent']}%")
            if r["percent"] < 95.0:
                sys.exit(1)
        if not no_install:
            install_and_preview(project_dir)
        update_manifest(spec, project_dir)
        save_obsidian(spec, project_dir)
        return project_dir

    print("\n[2/4] BUILDER (Structure): Transformando plano em IR...")
    ir = builder_build(plan_dict)
    slug = ir_slug_from_spec({"client": plan_dict.get("name", "app")})
    save_ir(ir, slug)
    print(f"  Páginas no IR: {len(ir.pages)}")
    print(f"  Entidades: {len(ir.entities)}")
    for p in ir.pages:
        print(f"    {p.route} ({p.layout}) — {len(p.sections)} seções")
    for e in ir.entities:
        print(f"    {e.name} ({len(e.fields)} campos)")

    print("\n[3/4] COMPILER: Gerando código Next.js via templates...")
    project_dir = compile_ir(ir)
    project_path = Path(project_dir)

    print("\n[4/4] Instalação e build...")
    manifest_entry = {
        "name": ir.name,
        "slug": project_path.name,
        "url": f"https://faohands-head.github.io/hands-head/previews/{project_path.name}/",
        "status": "generated",
        "created": str(time.strftime("%Y-%m-%d")),
        "source": "prompt",
        "description": ir.description,
        "pages": [p.route for p in ir.pages],
        "entities": [e.name for e in ir.entities],
    }

    if not no_install:
        print("\n  Instalando dependencias...")
        r = subprocess.run("npm install --legacy-peer-deps", cwd=project_dir, shell=True,
                          capture_output=True, text=True, timeout=120)
        if r.returncode == 0:
            print("  npm install OK")
            print("\n  Buildando...")
            r2 = subprocess.run("npm run build", cwd=project_dir, shell=True,
                               capture_output=True, text=True, timeout=120)
            if r2.returncode == 0:
                manifest_entry["status"] = "built"
                out_dir = project_path / "out"
                preview_dir = CAID_DIR / "previews" / project_path.name
                if out_dir.exists():
                    shutil.copytree(out_dir, preview_dir, dirs_exist_ok=True)
                    print(f"  Build disponivel em: {preview_dir}")
            else:
                print(f"  Build AVISO: {r2.stderr[:300]}")
        else:
            print(f"  npm install AVISO: {r.stderr[:300]}")

    update_manifest_raw(manifest_entry)
    print(f"\n  Projeto: {project_dir}")
    print(f"  Preview: http://localhost:3001")
    print(f"  Comando: cd {project_dir} && npm run dev")
    return project_dir


def update_manifest_raw(entry: dict):
    """Adiciona entrada ao manifest projects.json"""
    manifest_path = CAID_DIR / "projects" / "projects.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    else:
        manifest = {"projects": []}
    slug = entry.get("slug")
    manifest["projects"] = [p for p in manifest["projects"] if p.get("slug") != slug]
    manifest["projects"].append(entry)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"  Manifest atualizado: {slug}")


def main():
    parser = argparse.ArgumentParser(description="FAO HANDS - WebsiteApp Generator")
    parser.add_argument("--url", help="URL do site do cliente")
    parser.add_argument("--from-brain", help="Nome do briefing no Obsidian (vault/briefings/)")
    parser.add_argument("--prompt", help="Gera app via prompt natural (Mini-Base44)")
    parser.add_argument("--no-install", action="store_true", help="Pula npm install")
    parser.add_argument("--out-dir", help="Regenerar em pasta existente (ex: projects/websiteapp-...)")
    parser.add_argument("--strict", action="store_true", help="Falha se preservacao < 95%% apos gerar")
    args = parser.parse_args()

    if args.prompt:
        generate_from_prompt(args.prompt, args.no_install, out_dir=args.out_dir, strict=args.strict)
        return

    if not args.url and not args.from_brain:
        parser.print_help()
        print("\nInforme --url, --from-brain ou --prompt")
        sys.exit(1)

    print("=" * 50)
    print("  FAO HANDS - WebsiteApp Operation")
    print("=" * 50)

    if args.from_brain:
        spec = load_briefing(args.from_brain)
    else:
        print(f"\nURL: {args.url}")
        s = SiteScraper(args.url)
        spec = s.scrape_all()
        domain = args.url.replace("https://", "").split("/")[0].lower()
        if spec and (spec.get("hosting_placeholder") or len(spec.get("extracted", {}).get("texts", [])) < 5):
            brief = BRIEFING_BY_DOMAIN.get(domain)
            if brief:
                print(f"[WEBSITEAPP] Mesclando briefing automatico: {brief}")
                brain_spec = load_briefing(brief, merge_url=False)
                _merge_texts_into_spec(spec, brain_spec.get("extracted", {}).get("texts", []))
                spec["client"] = brain_spec.get("client", spec.get("client"))
                spec["project_name"] = brain_spec.get("project_name", spec.get("project_name"))
                spec["_briefing"] = brief
        if spec:
            spec["nav_items"] = [
                {"icon": "Home", "label": "Inicio", "route": "/"},
                {"icon": "Briefcase", "label": "Servicos", "route": "/servicos"},
                {"icon": "CreditCard", "label": "Planos", "route": "/planos"},
                {"icon": "Headphones", "label": "Suporte", "route": "/suporte"},
                {"icon": "User", "label": "Conta", "route": "/conta"},
            ]
            spec.setdefault("client", spec.get("cliente", domain.split(".")[0].title()))
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

    texts_n = len(spec.get("extracted", {}).get("texts", []))
    print(f"\n[WEBSITEAPP] Textos para geracao: {texts_n}")

    print("\n--- IR Pipeline (v1.0.0) ---")
    ir, ir_path = run_pipeline(spec, out_dir=args.out_dir)
    print(f"[IR] {len(ir.source_texts)} textos | {len(ir.websiteapp_sections)} rotas | {ir_path.name}")

    print("\n--- Gerando Projeto (via IR) ---")
    project_dir = generate_project(spec, out_dir=args.out_dir)

    if args.strict:
        from validate_preservation import measure
        r = measure(spec.get("url", ""), Path(project_dir), source_texts=spec.get("extracted", {}).get("texts", []))
        print(f"\n[WEBSITEAPP] Preservacao: {r['percent']}% ({r['found']}/{r['total_texts']})")
        if r["percent"] < 95.0:
            print("[WEBSITEAPP] ERRO: preservacao abaixo de 95%. Ajuste briefing/template.")
            sys.exit(1)

    if not args.no_install:
        print("\n--- Instalando Dependencias ---")
        install_and_preview(project_dir)

    print("\n--- Dashboard ---")
    update_manifest(spec, project_dir)

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
  plugins: [],
}
export default config
"""

if __name__ == "__main__":
    main()
