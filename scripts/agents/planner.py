"""
Planner Agent — Decompõe prompt natural em Array[Task] usando Gemini Flash (grátis)
Custo: ~800 tokens/app = R$ 0,00 (Gemini grátis)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agents.base import llm_call, parse_json_response
import json

SYSTEM_PROMPT = """Você é um arquiteto de software especializado em decompor briefings de apps.

Retorne APENAS JSON válido:
{
  "name": "nome-curto-do-app",
  "description": "descrição em 1 frase",
  "type": "landing|saas|dashboard|crud|pwa|api",
  "has_auth": false,
  "has_database": false,
  "entities": [{"name": "EntityName", "fields": [{"name": "field", "type": "string|number|boolean|date|email", "required": true}]}],
  "pages": [
    {"route": "/", "title": "Home", "layout": "public|auth|dashboard"},
    {"route": "/dashboard", "title": "Dashboard", "layout": "dashboard"}
  ],
  "features": ["feature1", "feature2"],
  "tasks": [
    {"id": 1, "description": "Criar projeto base Next.js", "dependencies": [], "type": "infra"},
    {"id": 2, "description": "Criar página Home com hero e cards", "dependencies": [1], "type": "frontend"},
    {"id": 3, "description": "Criar página Dashboard com tabela", "dependencies": [1], "type": "frontend"},
    {"id": 4, "description": "Configurar Supabase e criar tabelas", "dependencies": [1], "type": "backend"},
    {"id": 5, "description": "Implementar autenticação", "dependencies": [1, 4], "type": "backend"}
  ]
}

REGRAS:
- tasks com dependencies = 0 podem rodar em paralelo
- type: infra, frontend, backend, auth, deploy
- Máximo 10 tasks
- Nomes de entidades em PascalCase
- Rotas sempre começando com /
- Se não precisa de auth, has_auth: false
- Se não precisa de banco, has_database: false
"""


def plan(prompt: str) -> dict:
    result = llm_call(prompt, SYSTEM_PROMPT)
    if result:
        parsed = parse_json_response(result)
        if parsed:
            return parsed
    return _fallback_plan(prompt)


def _fallback_plan(prompt: str) -> dict:
    words = prompt.lower().split()
    has_auth = any(w in words for w in ["login", "auth", "register", "signup", "user"])
    has_db = any(w in words for w in ["crud", "banco", "dados", "data", "database", "tabela"])
    ptype = "landing"
    if has_db:
        ptype = "crud"
    elif "dashboard" in words or "admin" in words:
        ptype = "dashboard"
    elif "saas" in words or "plano" in words or "assinatura" in words:
        ptype = "saas"
    elif "app" in words or "pwa" in words:
        ptype = "pwa"

    name = prompt.strip()[:30].replace(" ", "-").lower()[:20] or "meu-app"

    plan_dict = {
        "name": name,
        "description": prompt.strip()[:100],
        "type": ptype,
        "has_auth": has_auth,
        "has_database": has_db,
        "entities": [],
        "pages": [{"route": "/", "title": "Home", "layout": "public"}],
        "features": [prompt.strip()[:50]],
        "tasks": [
            {"id": 1, "description": "Criar projeto base Next.js", "dependencies": [], "type": "infra"},
            {"id": 2, "description": "Criar template conforme briefing", "dependencies": [1], "type": "frontend"},
        ]
    }

    if has_db:
        plan_dict["entities"] = [
            {"name": "Item", "fields": [
                {"name": "id", "type": "string", "required": True},
                {"name": "name", "type": "string", "required": True},
                {"name": "created_at", "type": "date", "required": False}
            ]}
        ]
        plan_dict["tasks"].append(
            {"id": 3, "description": "Configurar banco e CRUD básico", "dependencies": [1], "type": "backend"}
        )
    if has_auth:
        plan_dict["pages"].append({"route": "/login", "title": "Login", "layout": "public"})
        plan_dict["pages"].append({"route": "/dashboard", "title": "Dashboard", "layout": "auth"})
        plan_dict["tasks"].append(
            {"id": 4, "description": "Implementar autenticação completa", "dependencies": [1, 3] if has_db else [1], "type": "auth"}
        )

    return plan_dict
