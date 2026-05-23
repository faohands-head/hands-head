"""
Builder Agent — Transforma Tasks → AppIR (estrutura completa) usando DeepSeek
Custo: ~1.300 tokens/app = R$ 0,00182 (DeepSeek)
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agents.base import llm_call, parse_json_response
from schemas.ir import AppIR

SYSTEM_PROMPT = """Você é um engenheiro de software que transforma planos de app em uma Representação Intermediária (IR).

Retorne APENAS JSON válido neste formato EXATO:
{
  "name": "nome-do-app",
  "description": "descrição",
  "pages": [
    {
      "route": "/",
      "title": "Home",
      "layout": "public",
      "sections": [
        {
          "id": "hero",
          "components": [
            {"type": "hero", "props": {"title": "Título", "subtitle": "Subtítulo", "cta": "Começar"}},
            {"type": "card-grid", "props": {"columns": 3, "items": [{"title": "Card 1", "text": "Descrição"}]}}
          ]
        },
        {
          "id": "footer",
          "components": [
            {"type": "footer", "props": {"text": "© 2026"}}
          ]
        }
      ]
    }
  ],
  "entities": [
    {"name": "Item", "fields": [{"name": "id", "type": "string", "required": true}, {"name": "name", "type": "string", "required": true}]}
  ],
  "datasource": {"type": "static", "config": {}},
  "auth": {"provider": "none", "pages": [], "entities": []},
  "theme": {"primary": "#3b82f6", "radius": "0.5rem"}
}

TIPOS DE COMPONENTES DISPONÍVEIS:
- hero: title, subtitle, cta, image
- card-grid: columns, items[{title, text, icon}]
- data-table: columns[{key, label}], rows[{...}], actions[create,edit,delete]
- form: fields[{name, type, label, required}], submit_label
- chart: type(bar|line|pie), data[{label, value}]
- stats: items[{label, value, icon, change}]
- content: paragraphs[string]
- cta: title, text, button_label, button_url
- features: items[{icon, title, text}]
- pricing: plans[{name, price, features[], cta}]
- footer: text, links[{label, url}]
- navbar: brand, links[{label, url}]
- section-header: title, subtitle, alignment(center|left)
"""


def build(plan: dict) -> AppIR:
    prompt = json.dumps(plan, indent=2, ensure_ascii=False)
    result = llm_call(prompt, SYSTEM_PROMPT)

    if result:
        parsed = parse_json_response(result)
        if parsed:
            return AppIR.from_dict(parsed)

    return _fallback_build(plan)


def _fallback_build(plan: dict) -> AppIR:
    """Gera AppIR mínima sem LLM — template padrão"""
    from schemas.ir import AppIR, Page, Section, Component, Entity, Field, DataSource, Auth

    pages = []
    for p in plan.get("pages", []):
        sections = []
        if p["route"] == "/":
            sections.append(Section(id="hero", components=[
                Component("hero", {"title": plan.get("description", "App"), "subtitle": "Gerado por FAO HANDS", "cta": "Começar"}),
                Component("card-grid", {"columns": 3, "items": [
                    {"title": "Feature 1", "text": "Descrição da feature 1"},
                    {"title": "Feature 2", "text": "Descrição da feature 2"},
                ]}),
            ]))
        elif p["route"] == "/dashboard":
            sections.append(Section(id="stats", components=[
                Component("stats", {"items": [
                    {"label": "Usuários", "value": "0", "icon": "Users", "change": "+0%"},
                    {"label": "Receita", "value": "R$ 0", "icon": "DollarSign", "change": "+0%"},
                ]}),
            ]))
            sections.append(Section(id="table", components=[
                Component("data-table", {"columns": [{"key": "name", "label": "Nome"}], "rows": []}),
            ]))
        sections.append(Section(id="footer", components=[
            Component("footer", {"text": f"© 2026 {plan.get('name', 'App')}. Todos os direitos reservados."})
        ]))
        pages.append(Page(route=p["route"], title=p.get("title", "Page"), layout=p.get("layout", "public"), sections=sections))

    entities = []
    for e in plan.get("entities", []):
        entities.append(Entity(
            name=e["name"],
            fields=[Field(**{k: v for k, v in f.items() if k in Field.__dataclass_fields__}) for f in e.get("fields", [])]
        ))

    return AppIR(
        name=plan.get("name", "App"),
        description=plan.get("description", ""),
        pages=pages,
        entities=entities,
        datasource=DataSource(type="static" if not plan.get("has_database") else "supabase"),
        auth=Auth(provider="supabase" if plan.get("has_auth") else "none"),
    )
