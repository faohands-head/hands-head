"""
Boilerplate Generator - Next.js + Tailwind + shadcn/ui
"""
import os, subprocess, json, shutil
from pathlib import Path

def create_nextjs_project(project_dir: str, project_name: str, types: list):
    """Cria projeto Next.js com Tailwind e shadcn/ui"""
    path = Path(project_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    os.chdir(project_dir)
    
    print(f"[TEMPLATE] Criando {project_name} em {project_dir}")
    
    # package.json
    package = {
        "name": project_name,
        "version": "0.1.0",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "next lint"
        },
        "dependencies": {
            "next": "^14.2.0",
            "react": "^18.3.0",
            "react-dom": "^18.3.0",
            "lucide-react": "^0.400.0",
            "class-variance-authority": "^0.7.0",
            "clsx": "^2.1.0",
            "tailwind-merge": "^2.3.0",
            "tailwindcss-animate": "^1.0.7",
            "@radix-ui/react-slot": "^1.0.2",
            "@radix-ui/react-dialog": "^1.0.5",
            "@radix-ui/react-dropdown-menu": "^2.0.6",
            "@radix-ui/react-toast": "^1.1.5"
        },
        "devDependencies": {
            "@types/node": "^20.0.0",
            "@types/react": "^18.3.0",
            "@types/react-dom": "^18.3.0",
            "typescript": "^5.4.0",
            "tailwindcss": "^3.4.0",
            "postcss": "^8.4.0",
            "autoprefixer": "^10.4.0"
        }
    }
    
    (path / "package.json").write_text(json.dumps(package, indent=2))
    
    # tsconfig.json
    tsconfig = {
        "compilerOptions": {
            "target": "es5",
            "lib": ["dom", "dom.iterable", "esnext"],
            "allowJs": True,
            "skipLibCheck": True,
            "strict": True,
            "noEmit": True,
            "esModuleInterop": True,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "jsx": "preserve",
            "incremental": True,
            "plugins": [{"name": "next"}],
            "paths": {"@/*": ["./src/*"]}
        },
        "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
        "exclude": ["node_modules"]
    }
    (path / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2))
    
    # next.config.js
    (path / "next.config.js").write_text("/** @type {import('next').NextConfig} */\nconst nextConfig = { reactStrictMode: true }\nmodule.exports = nextConfig\n")
    
    # tailwind.config.ts
    (path / "tailwind.config.ts").write_text("""import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
export default config
""")
    
    # postcss.config.js
    (path / "postcss.config.js").write_text("module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }\n")
    
    # Diretórios src
    for d in ["src/app", "src/components/ui", "src/lib", "src/pages/api"]:
        (path / d).mkdir(parents=True, exist_ok=True)
    
    # globals.css
    (path / "src/app/globals.css").write_text("""@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
""")
    
    # lib/utils.ts
    (path / "src/lib/utils.ts").write_text("""import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
""")
    
    print(f"[TEMPLATE] Projeto base criado em {project_dir}")
    return True

def install_deps(project_dir: str):
    """Notifica usuário para instalar dependências"""
    print(f"\n[TEMPLATE] Para instalar dependências, execute:")
    print(f"  cd {project_dir}")
    print(f"  npm install --legacy-peer-deps\n")
    return True
