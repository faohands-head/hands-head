"""
Etapa 1 — Mede quantos textos do scrape aparecem no projeto gerado.
Uso:
  python scripts/validate_preservation.py --url https://exemplo.com --project projects/websiteapp-...
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from website_scraper import SiteScraper


NOISE_FRAGMENTS = (
    "permissão",
    "permissao",
    "octal",
    "cpanel",
    "gerenciador de arquivos",
    "file manager",
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _is_noise(text: str) -> bool:
    low = text.lower()
    return any(n in low for n in NOISE_FRAGMENTS)


def _text_in_blob(text: str, blob: str) -> bool:
    n = _normalize(text)
    if len(n) < 8:
        return n in blob
    if n in blob:
        return True
    # Substring parcial (primeiros 24 chars) para textos truncados no UI
    head = n[:24]
    if len(head) >= 12 and head in blob:
        return True
    words = [w for w in n.split() if len(w) >= 4]
    if len(words) >= 2:
        hits = sum(1 for w in words[:6] if w in blob)
        if hits >= max(2, len(words[:6]) - 1):
            return True
    return False


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


def measure(
    url: str,
    project_dir: Path,
    min_len: int = 8,
    source_texts: list[str] | None = None,
) -> dict:
    method = ""
    blocked = False
    hosting_placeholder = False

    if source_texts is None:
        scraper = SiteScraper(url)
        scraper.fetch()
        scraper.extract_texts()
        scraper.hosting_placeholder = scraper.is_hosting_placeholder()
        scraper.filter_noise_texts()
        raw = scraper.texts
        method = scraper.method_used
        blocked = scraper.blocked
        hosting_placeholder = scraper.hosting_placeholder
    else:
        raw = list(source_texts)

    originals = [t.strip() for t in raw if t and len(t.strip()) >= min_len and not _is_noise(t)]
    originals = list(dict.fromkeys(originals))
    blob = _normalize(_project_text_blob(project_dir))

    found = sum(1 for t in originals if _text_in_blob(t, blob))
    total = len(originals) or 1
    pct = round(100.0 * found / total, 1)

    missing = [t for t in originals if not _text_in_blob(t, blob)][:20]
    return {
        "url": url,
        "project": str(project_dir),
        "method": method,
        "blocked": blocked,
        "hosting_placeholder": hosting_placeholder,
        "total_texts": total,
        "found": found,
        "percent": pct,
        "missing_sample": missing,
    }


def main():
    p = argparse.ArgumentParser(description="Preservação de conteúdo scrape → projeto")
    p.add_argument("--url", required=True)
    p.add_argument("--project", required=True, help="Caminho do projeto gerado")
    p.add_argument("--strict", action="store_true", help="Exit 1 se abaixo de min-percent")
    p.add_argument("--min-percent", type=float, default=95.0)
    p.add_argument("--texts-file", help="JSON com lista de textos fonte (briefing)")
    args = p.parse_args()

    project_dir = Path(args.project)
    if not project_dir.is_absolute():
        project_dir = ROOT / project_dir
    if not project_dir.exists():
        print(f"Projeto não encontrado: {project_dir}", file=sys.stderr)
        sys.exit(2)

    source_texts = None
    if args.texts_file:
        tf = Path(args.texts_file)
        if not tf.is_absolute():
            tf = ROOT / tf
        data = json.loads(tf.read_text(encoding="utf-8"))
        source_texts = data if isinstance(data, list) else data.get("texts", [])

    r = measure(args.url, project_dir, source_texts=source_texts)
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
