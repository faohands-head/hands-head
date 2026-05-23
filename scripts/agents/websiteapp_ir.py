"""
WebsiteApp IR pipeline — spec/briefing/URL → Plan → AppIR → render (Etapa 2)
Sem LLM no caminho WebsiteApp (determinístico). Prompt/CRUD pode usar builder LLM depois.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from schemas.ir import AppIR, Page, DEFAULT_NAV

ROOT = Path(__file__).resolve().parent.parent.parent
VAULT_SPECS = ROOT / "vault" / "specs"


def ir_slug_from_spec(spec: dict, out_dir: str | None = None) -> str:
    if out_dir:
        return Path(out_dir).name
    domain = spec.get("domain") or (spec.get("url", "").replace("https://", "").split("/")[0])
    if domain:
        return f"websiteapp-{domain.replace('.', '-')}"
    client = spec.get("client", "app").lower().replace(" ", "-")
    return f"websiteapp-{client}"[:60]


def build_plan_from_spec(spec: dict) -> dict:
    """IntentObject / plano estruturado a partir do spec (scrape ou briefing)."""
    texts = spec.get("extracted", {}).get("texts", [])
    nav = spec.get("nav_items") or list(DEFAULT_NAV)
    colors = spec.get("extracted", {}).get("colors", [])
    primary = "#3b82f6"
    for c in colors:
        if isinstance(c, str) and c.startswith("#") and len(c) == 7 and c.lower() not in ("#ffffff", "#000000"):
            primary = c
            break

    return {
        "name": spec.get("project_name", spec.get("client", "WebsiteApp")),
        "description": spec.get("goal", ""),
        "type": "websiteapp",
        "has_auth": False,
        "has_database": False,
        "url": spec.get("url", ""),
        "client": spec.get("client", "Cliente"),
        "source": spec.get("struct", {}).get("source", "scraper"),
        "hosting_placeholder": spec.get("hosting_placeholder", False),
        "pages": [{"route": n.get("route", "/"), "title": n.get("label", "Page"), "layout": "app_shell"} for n in nav],
        "nav_items": nav,
        "content_texts": texts,
        "theme": {"primary": primary, "radius": "0.5rem"},
        "features": texts[:30],
    }


def build_ir_from_spec(spec: dict, plan: dict | None = None) -> AppIR:
    """Structure Agent determinístico: spec → AppIR com seções WebsiteApp."""
    import sys
    sys.path.insert(0, str(ROOT / "templates"))
    from websiteapp_template import categorize_texts, build_page_sections

    plan = plan or build_plan_from_spec(spec)
    texts = plan.get("content_texts") or spec.get("extracted", {}).get("texts", [])
    nav = plan.get("nav_items") or spec.get("nav_items") or list(DEFAULT_NAV)
    client = plan.get("client", spec.get("client", "Cliente"))
    project_name = plan.get("name", spec.get("project_name", client))

    sections_raw = spec.get("extracted", {}).get("sections", [])
    animations = spec.get("extracted", {}).get("animations", [])
    content_data = categorize_texts(texts, sections_raw, client, animations)

    websiteapp_sections = {}
    pages = []
    for item in nav:
        route = item.get("route", "/")
        label = item.get("label", "Page")
        websiteapp_sections[route] = build_page_sections(route, label, content_data, client, project_name)
        pages.append(Page(route=route, title=label, layout="app_shell", sections=[]))

    return AppIR(
        name=project_name,
        description=plan.get("description", ""),
        pages=pages,
        entities=[],
        theme=plan.get("theme", {"primary": "#3b82f6", "radius": "0.5rem"}),
        ir_version="1.0.0",
        app_type="websiteapp",
        url=plan.get("url", spec.get("url", "")),
        client=client,
        navigation=nav,
        source_texts=list(texts),
        websiteapp_sections=websiteapp_sections,
    )


def save_ir(ir: AppIR, slug: str) -> Path:
    VAULT_SPECS.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w\-]", "-", slug).strip("-")[:80]
    path = VAULT_SPECS / f"{safe}-ir.json"
    path.write_text(json.dumps(ir.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[IR] Salvo: {path.relative_to(ROOT)}")
    return path


def load_ir(slug_or_path: str) -> AppIR:
    p = Path(slug_or_path)
    if not p.exists():
        p = VAULT_SPECS / f"{slug_or_path}-ir.json"
        if not p.exists():
            p = VAULT_SPECS / slug_or_path
    data = json.loads(p.read_text(encoding="utf-8"))
    return AppIR.from_dict(data)


def ir_to_render_spec(ir: AppIR) -> dict:
    """Converte AppIR → spec dict para websiteapp_template."""
    return {
        "url": ir.url,
        "domain": urlparse_host(ir.url),
        "client": ir.client or ir.name,
        "project_name": ir.name,
        "goal": ir.description,
        "nav_items": ir.navigation or list(DEFAULT_NAV),
        "extracted": {
            "texts": ir.source_texts,
            "colors": [ir.theme.get("primary", "#3b82f6")],
            "fonts": [],
            "animations": [],
            "animations_raw": {},
            "sections": [],
        },
        "_sections_by_route": ir.websiteapp_sections,
        "ir_version": ir.ir_version,
        "_ir_path": f"vault/specs/{ir_slug_from_spec({'client': ir.client})}-ir.json",
    }


def urlparse_host(url: str) -> str:
    if not url:
        return ""
    return url.replace("https://", "").replace("http://", "").split("/")[0]


def plan_from_prompt_plan(plan_dict: dict, prompt: str) -> dict:
    """Adapta saída do planner (--prompt) para pipeline WebsiteApp."""
    texts = [prompt.strip()] + list(plan_dict.get("features", []))
    nav = list(DEFAULT_NAV)
    return {
        "name": plan_dict.get("name", "app"),
        "description": plan_dict.get("description", prompt[:100]),
        "type": plan_dict.get("type", "websiteapp"),
        "has_auth": plan_dict.get("has_auth", False),
        "has_database": plan_dict.get("has_database", False),
        "url": "",
        "client": plan_dict.get("name", "App"),
        "source": "prompt",
        "pages": plan_dict.get("pages", []),
        "nav_items": nav,
        "content_texts": texts,
        "theme": {"primary": "#3b82f6", "radius": "0.5rem"},
        "features": texts,
    }


def is_websiteapp_plan(plan: dict) -> bool:
    if plan.get("type") in ("websiteapp", "pwa", "landing", "saas"):
        return not plan.get("has_database")
    return False


def run_pipeline(spec: dict, out_dir: str | None = None) -> tuple[AppIR, Path]:
    plan = build_plan_from_spec(spec)
    ir = build_ir_from_spec(spec, plan)
    slug = ir_slug_from_spec(spec, out_dir)
    ir_path = save_ir(ir, slug)
    render_spec = ir_to_render_spec(ir)
    render_spec.update({k: spec[k] for k in ("_briefing", "struct", "hosting_placeholder") if k in spec})
    spec.clear()
    spec.update(render_spec)
    spec["_ir_saved"] = str(ir_path)
    return ir, ir_path
