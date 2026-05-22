"""
FAO HANDS Brain - Integração com Obsidian vault
Lê/escreve diretamente no filesystem (markdown) + opcional REST API
"""
import os, json
from pathlib import Path
from datetime import datetime

VAULT = Path(__file__).resolve().parent.parent / "vault"
OBSIDIAN_API = "http://localhost:27123"
API_KEY = "fao-hands-brain-key-2026"

class Brain:
    def __init__(self):
        self.vault = VAULT
        self._api = None

    @property
    def api(self):
        if self._api is None:
            try:
                import requests
                self._api = requests.Session()
                self._api.headers.update({"x-api-key": API_KEY})
                self._api.get(f"{OBSIDIAN_API}/vault/", timeout=2)
            except:
                self._api = False
        return self._api if self._api else None

    def test(self):
        return self.vault.exists()

    def read(self, path):
        """Lê arquivo do vault (via disco ou API)"""
        full = self.vault / path
        if full.exists():
            return full.read_text(encoding="utf-8")
        if self.api:
            try:
                r = self.api.get(f"{OBSIDIAN_API}/vault/{path}", timeout=5)
                return r.text if r.status_code == 200 else None
            except:
                pass
        return None

    def write(self, path, content):
        """Escreve arquivo no vault"""
        full = self.vault / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        return True

    def list_dir(self, path=""):
        dir_path = self.vault / path
        if dir_path.exists():
            return [str(f.relative_to(self.vault)) for f in dir_path.rglob("*") if f.is_file()]
        return []

    def search(self, term):
        results = []
        for f in self.vault.rglob("*.md"):
            if term.lower() in f.read_text(encoding="utf-8", errors="ignore").lower():
                results.append(str(f.relative_to(self.vault)))
        return results

    def get_briefing(self, name=None):
        if name:
            return self.read(f"briefings/{name}")
        files = sorted((self.vault / "briefings").glob("*.md")) if (self.vault / "briefings").exists() else []
        if files:
            return files[-1].read_text(encoding="utf-8")
        return None

    def list_briefings(self):
        brief_dir = self.vault / "briefings"
        if brief_dir.exists():
            return [f.name for f in brief_dir.glob("*.md")]
        return []

    def save_report(self, project_name, data):
        date = datetime.now().strftime("%Y-%m-%d")
        content = f"""---
projeto: {project_name}
data: {date}
status: concluido
---

# Relatório: {project_name}

## Briefing
{data.get('briefing', 'N/A')}

## Tipo
{data.get('type', 'N/A')}

## Tasks ({len(data.get('tasks', []))})
"""
        for i, t in enumerate(data.get('tasks', []), 1):
            content += f"{i}. {t.get('description', 'N/A')}\n"

        content += f"""
## Tempo
{data.get('elapsed', 'N/A')} segundos

## Diretório
{data.get('dir', 'N/A')}
"""
        path = f"reports/{project_name}-{date}.md"
        self.write(path, content)
        return path

    def save_spec(self, project_name, spec):
        content = f"""---
projeto: {project_name}
data: {datetime.now().strftime("%Y-%m-%d")}
---

# Especificação: {project_name}

```json
{json.dumps(spec, indent=2)}
```
"""
        self.write(f"specs/{project_name}.md", content)
