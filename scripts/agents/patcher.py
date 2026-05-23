"""
Patcher Agent — Edita componentes específicos sem regenerar app inteiro
Custo: ~400 tokens/edição = R$ 0,00056 (DeepSeek)
Estratégia: extrai nó do IR, envia contexto mínimo, reaplica
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agents.base import llm_call, parse_json_response
from schemas.ir import AppIR

SYSTEM_PROMPT = """Você é um especialista em editar componentes de apps.

Recebe um nó do IR (App schemas) e uma solicitação de mudança.
Retorne APENAS o nó modificado no mesmo formato JSON.

Disponível: hero, card-grid, data-table, form, chart, stats, content, cta, features, pricing, footer, navbar, section-header
"""


def patch_ir(ir: AppIR, instruction: str) -> AppIR:
    """Edita o IR baseado em instrução em linguagem natural"""
    prompt = json.dumps({
        "current_ir": {
            "name": ir.name,
            "description": ir.description,
            "pages": [{"route": p.route, "title": p.title, "layout": p.layout,
                        "sections": [{"id": s.id, "components": [
                            {"type": c.type, "props": c.props} for c in s.components
                        ]} for s in p.sections]} for p in ir.pages],
            "entities": [{"name": e.name, "fields": [{"name": f.name, "type": f.type} for f in e.fields]} for e in ir.entities],
        },
        "change_request": instruction
    }, ensure_ascii=False)

    result = llm_call(prompt, SYSTEM_PROMPT)
    if result:
        parsed = parse_json_response(result)
        if parsed:
            try:
                return AppIR.from_dict(parsed)
            except Exception:
                pass

    return ir


def patch_page(ir: AppIR, route: str, instruction: str) -> AppIR:
    """Edita apenas uma página específica"""
    page = next((p for p in ir.pages if p.route == route), None)
    if not page:
        return ir

    prompt = json.dumps({
        "page": {"route": page.route, "title": page.title, "layout": page.layout,
                 "sections": [{"id": s.id, "components": [
                     {"type": c.type, "props": c.props} for c in s.components
                 ]} for s in page.sections]},
        "change_request": instruction
    }, ensure_ascii=False)

    result = llm_call(prompt, SYSTEM_PROMPT)
    if result:
        parsed = parse_json_response(result)
        if parsed and "sections" in parsed:
            from schemas.ir import Section, Component
            page.sections = [
                Section(id=s.get("id", "section"), components=[
                    Component(**{k: v for k, v in c.items() if k in ("type", "props")})
                    for c in s.get("components", [])
                ]) for s in parsed["sections"]
            ]

    return ir
