"""
Valida AppIR v1.0.0 (JSON no vault ou dict).
Uso: py -3 scripts/validate_ir.py vault/specs/websiteapp-acessosvipclientes-com-br-56722640-ir.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from schemas.ir import AppIR


def validate(data: dict) -> list[str]:
    errors = []
    if data.get("ir_version") != "1.0.0":
        errors.append("ir_version deve ser 1.0.0")
    if not data.get("name"):
        errors.append("name obrigatorio")
    if data.get("app_type") == "websiteapp":
        sections = data.get("websiteapp_sections") or {}
        if not sections:
            errors.append("websiteapp_sections vazio")
        nav = data.get("navigation") or []
        for item in nav:
            route = item.get("route", "/")
            if route not in sections:
                errors.append(f"rota {route} sem secoes em websiteapp_sections")
        texts = data.get("source_texts") or []
        if not texts:
            errors.append("source_texts vazio")
    return errors


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not path:
        print("Uso: validate_ir.py <caminho-ir.json>")
        sys.exit(2)
    if not path.is_absolute():
        path = ROOT / path
    data = json.loads(path.read_text(encoding="utf-8"))
    AppIR.from_dict(data)
    errors = validate(data)
    if errors:
        for e in errors:
            print(f"ERRO: {e}")
        sys.exit(1)
    print(f"IR valido: {path.name} | rotas={len(data.get('websiteapp_sections', {}))} textos={len(data.get('source_texts', []))}")
    sys.exit(0)


if __name__ == "__main__":
    main()
