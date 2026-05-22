#!/usr/bin/env python3
"""
FAO HANDS
Multi-agent CAID system - Obsidian Brain + OpenHands + templates + preview
"""
import os, sys, json, uuid, time, subprocess, requests, shutil
from pathlib import Path

CAID_DIR = Path(__file__).resolve().parent.parent
PROJECTS = CAID_DIR / "projects"
INSTRUCTIONS = CAID_DIR / "instructions"

OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "qwen2.5-coder:7b"

sys.path.insert(0, str(CAID_DIR / "scripts"))
from brain import Brain

TYPES = {
    "landing": "Landing Page institucional com seções hero, serviços, depoimentos, contato e WhatsApp",
    "saas": "Página SaaS com planos/preços, features, login, dashboard link",
    "dashboard": "Dashboard administrativo com cards, gráficos, tabelas e sidebar",
    "pwa": "Aplicação PWA com suporte offline, service worker e manifest",
    "websiteapp": "WebsiteApp com navegação tipo app (bottom nav com ícones, hamburger menu, sidebar retrátil, PWA, design revolucionário desktop e mobile)"
}

os.makedirs(PROJECTS, exist_ok=True)
os.makedirs(INSTRUCTIONS, exist_ok=True)

def llm(prompt, system=""):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate",
            json={"model": LLM_MODEL, "prompt": prompt, "system": system, "stream": False}, timeout=120)
        return r.json().get("response", "")
    except:
        return ""

def parse_json(text):
    try:
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
        return json.loads(text.strip())
    except:
        return None

def run_cmd(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=True)

def get_free_port(start=4000):
    import socket
    port = start
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
            port += 1

class CAID:
    def __init__(self, briefing=None, briefing_file=None):
        self.brain = Brain()
        self.start_time = time.time()
        self.uid = uuid.uuid4().hex[:8]
        self.spec = {}
        self.tasks = []
        self.briefing_file = briefing_file
        
        if briefing_file:
            self.briefing = self.brain.read(f"briefings/{briefing_file}") or ""
        else:
            self.briefing = briefing or ""
        
    def step1_decompose(self):
        print("\n[1/6] Decompondo briefing...")
        sys_prompt = "Você é um arquiteto de software. Decomponha tarefas em subtarefas paralelizáveis."
        prompt = f"""Briefing: {self.briefing}
        
Tipos disponíveis: {json.dumps(TYPES)}

Retorne JSON:
{{
  "project_type": "landing|saas|dashboard|pwa",
  "project_name": "nome-curto",
  "goal": "objetivo em frase",
  "pages": ["paginas"],
  "components": ["componentes"],
  "features": ["funcionalidades"],
  "tasks": [{{"id": 1, "description": "...", "dependencies": [], "type": "code"}}]
}}"""
        out = parse_json(llm(prompt, sys_prompt))
        if not out:
            out = {"project_type": "landing", "project_name": f"projeto-{self.uid}", "goal": self.briefing,
                   "pages": ["home"], "components": ["Hero"], "features": [], 
                   "tasks": [{"id":1,"description":"Criar projeto base","dependencies":[],"type":"code"}]}
        self.spec = out
        self.tasks = out.get("tasks", [])
        print(f"  Tipo: {self.spec.get('project_type')}")
        print(f"  Nome: {self.spec.get('project_name')}")
        print(f"  Tasks: {len(self.tasks)}")
        return out

    def step2_create_project(self):
        print("\n[2/6] Criando projeto...")
        name = self.spec["project_name"].replace(" ", "-").lower()
        self.project_dir = PROJECTS / f"{name}-{self.uid}"
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Gera boilerplate via template
        self._generate_boilerplate()
        
        # Init git
        run_cmd("git init", self.project_dir)
        run_cmd("git checkout -b main", self.project_dir)
        (self.project_dir / ".gitkeep").write_text("")
        run_cmd("git add .", self.project_dir)
        run_cmd('git commit -m "chore: init project"', self.project_dir)
        print(f"  Projeto: {self.project_dir}")
        return True

    def _generate_boilerplate(self):
        """Gera projeto Next.js + Tailwind + shadcn/ui"""
        p = self.project_dir
        ptype = self.spec.get("project_type", "landing")
        
        # Importa e executa template base
        sys.path.insert(0, str(CAID_DIR / "templates"))
        from base import create_nextjs_project, install_deps
        create_nextjs_project(str(p), self.spec["project_name"], [ptype])
        
        # Template específico
        try:
            mod = __import__(ptype)
            mod.add_to_project(str(p), self.spec)
            print(f"  Template {ptype} aplicado")
        except Exception as e:
            print(f"  Template {ptype} não disponível ({e}), usando landing")
            from landing import add_to_project
            add_to_project(str(p), self.spec)
        
        install_deps(str(p))
        print(f"  Boilerplate {ptype} gerado")

    def step3_create_worktrees(self):
        print("\n[3/6] Criando worktrees...")
        parallel = [t for t in self.tasks if not t.get("dependencies")]
        self.worktrees = {}
        
        for task in parallel:
            branch = f"feature/task-{task['id']}"
            wt = self.project_dir / f"wt-{task['id']}"
            run_cmd(f"git branch {branch}", self.project_dir)
            run_cmd(f"git worktree add {wt} {branch}", self.project_dir)
            self.worktrees[task["id"]] = {"dir": str(wt), "branch": branch}
            
            # Instrução JSON
            inst = {"task_id": task["id"], "description": task["description"],
                    "worktree": str(wt), "branch": branch, "spec": self.spec}
            (INSTRUCTIONS / f"task-{task['id']}.json").write_text(json.dumps(inst, indent=2))
        
        print(f"  {len(self.worktrees)} worktrees criadas")
        return True

    def step4_execute_tasks(self):
        print("\n[4/6] Executando tasks via Claude Code + Ollama...")
        for tid, wt in self.worktrees.items():
            task = next((t for t in self.tasks if t["id"] == tid), {})
            desc = task.get("description", "implementar")
            print(f"  Task {tid}: {desc} em {wt['dir']}")
            
            prompt = f"""Você está no diretório {wt['dir']}.
Projeto: {self.spec.get('project_name')}
Tipo: {self.spec.get('project_type')}
Contexto: {self.spec.get('goal', '')}

Sua tarefa: {desc}

Implemente os arquivos necessários neste diretório. Use git add e git commit após finalizar."""
            
            try:
                r = subprocess.run(
                    ["ollama", "launch", "claude", "--model", LLM_MODEL],
                    input=prompt, text=True, capture_output=True, timeout=300,
                    cwd=wt["dir"]
                )
                print(f"    Claude: ok ({len(r.stdout)} chars)")
            except subprocess.TimeoutExpired:
                print(f"    Claude: timeout (>300s)")
            except Exception as e:
                print(f"    Claude: {e}")
            
            run_cmd("git add .", wt["dir"])
            r = run_cmd(f'git diff --cached --quiet', wt["dir"])
            if r.returncode != 0:
                run_cmd(f'git commit -m "feat: task {tid}"', wt["dir"])
                print(f"    Commit task {tid}")
        
        self._step5_merge()
        self._step6_preview()
        self._save_to_brain()
        
        elapsed = time.time() - self.start_time
        print(f"\n✅ CONCLUÍDO em {elapsed:.0f}s")
        print(f"   Projeto: {self.project_dir}")
        return True
    
    def _save_to_brain(self):
        if self.brain.test():
            report = {"project": self.spec.get("project_name"), "briefing": self.briefing,
                      "type": self.spec.get("project_type"), "tasks": self.tasks,
                      "elapsed": round(time.time() - self.start_time, 1), "dir": str(self.project_dir)}
            self.brain.save_report(self.spec.get("project_name", "projeto"), report)
            self.brain.save_spec(self.spec.get("project_name", "projeto"), self.spec)
            print("  Salvo no Obsidian (briefings/reports/specs)")
        else:
            print("  Obsidian não disponível (plugin REST ativo?)")

    def _step5_merge(self):
        print("\n[5/6] Integrando branches...")
        for tid, wt in self.worktrees.items():
            branch = wt["branch"]
            run_cmd(f"git checkout main", self.project_dir)
            r = run_cmd(f"git merge {branch} --no-edit", self.project_dir)
            if "CONFLICT" in r.stdout:
                run_cmd("git add .", self.project_dir)
                run_cmd(f'git commit -m "fix: merge task {tid}"', self.project_dir)
            print(f"  Merge {branch} → main")

    def _step6_preview(self):
        print("\n[6/6] Iniciando preview...")
        port = get_free_port(4000)
        
        # Cria docker-compose para preview
        compose = {
            "version": "3.8",
            "services": {
                self.spec["project_name"]: {
                    "build": {"context": str(self.project_dir), "dockerfile": "Dockerfile"},
                    "ports": [f"{port}:3000"],
                    "environment": ["NODE_ENV=production"]
                }
            }
        }
        (self.project_dir / "docker-compose.yml").write_text(json.dumps(compose, indent=2))
        
        # Dockerfile
        (self.project_dir / "Dockerfile").write_text("""FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "dev"]
""")
        
        print(f"  Preview: http://localhost:{port}")
        print(f"  Para iniciar: cd {self.project_dir} && docker-compose up")

    def run(self):
        print("=" * 60)
        print("🚀 FAO HANDS - Multi-Agent Orchestrator")
        print("=" * 60)
        print(f"Briefing: {self.briefing}")
        
        self.step1_decompose()
        self.step2_create_project()
        self.step3_create_worktrees()
        self.step4_execute_tasks()
        
        report = {"project": self.spec.get("project_name"), "briefing": self.briefing,
                  "type": self.spec.get("project_type"), "tasks": len(self.tasks),
                  "elapsed": round(time.time() - self.start_time, 1), "dir": str(self.project_dir)}
        (self.project_dir / "caid-report.json").write_text(json.dumps(report, indent=2))
        return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FAO HANDS - Orchestrator")
    parser.add_argument("briefing", nargs="?", default="", help="Briefing direto")
    parser.add_argument("--from-brain", "-b", metavar="ARQUIVO", help="Ler briefing do Obsidian (briefings/ARQUIVO)")
    args = parser.parse_args()
    
    if args.from_brain:
        caid = CAID(briefing_file=args.from_brain)
    else:
        briefing = args.briefing or "criar landing page para clínica odontológica premium"
        caid = CAID(briefing=briefing)
    
    caid.run()
