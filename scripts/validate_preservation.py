"""
Etapa 1 — Mede quantos textos do scrape aparecem no projeto gerado.
Uso:
  python scripts/validate_preservation.py --url https://exemplo.com --project projects/websiteapp-...
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from website_scraper import SiteScraper


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _project_text_blob(project_dir: Path) -> str:
    parts = []
    for pattern in ("**/*.jsx", "**/*.js", "**/*.tsx", "**/*.html", "**/*.json"):
        for f in project_dir.glob(pattern):
            if "node_modules" in f.parts or ".next" in f.parts:
                continue
            try:
                parts.append(f.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    return "\n".join(parts)


def measure(url: str, project_dir: Path, min_len: int = 12) -> dict:
    scraper = SiteScraper(url)
    scraper.fetch()
    source_texts = [_normalize(t) for t in scraper.texts if len(t.strip()) >= min_len]
    blob = _normalize(_project_text_blob(project_dir))

    found = sum(1 for t in source_texts if t in blob)
    total = len(source_texts) or 1
    pct = round(100.0 * found / total, 1)

    missing = [t for t in source_texts if t not in blob][:20]
    return {
        "url": url,
        "project": str(project_dir),
        "method": scraper.method_used,
        "blocked": scraper.blocked,
        "total_texts": total,
        "found": found,
        "percent": pct,
        "missing_sample": missing,
    }


def main():
    p = argparse.ArgumentParser(description="Preservação de conteúdo scrape → projeto")
    p.add_argument("--url", required=True)
    p.add_argument("--project", required=True, help="Caminho do projeto gerado")
    p.add_argument("--strict", action="store_true", help="Exit 1 se < 95%")
    p.add_argument("--min-percent", type=float, default=95.0)
    args = p.parse_args()

    project_dir = Path(args.project)
    if not project_dir.is_absolute():
        project_dir = ROOT / project_dir
    if not project_dir.exists():
        print(f"Projeto não encontrado: {project_dir}", file=sys.stderr)
        sys.exit(2)

    r = measure(args.url, project_dir)
    print(f"URL: {r['url']}")
    print(f"Projeto: {r['project']}")
    print(f"Scraper: {r['method']} blocked={r['blocked']}")
    print(f"Preservação: {r['found']}/{r['total_texts']} = {r['percent']}%")
    if r["missing_sample"]:
        print("Amostra ausente:")
        for t in r["missing_sample"][:10]:
            print(f"  - {t[:80]}")

    if args.strict and r["percent"] < args.min_percent:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
