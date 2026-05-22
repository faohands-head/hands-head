"""SaaS Template"""
def add_to_project(project_dir: str, spec: dict):
    from pathlib import Path
    p = Path(project_dir)
    
    (p / "src/app/page.tsx").write_text("""'use client'

import { useState } from 'react'
import { Check, ArrowRight, Menu, X } from 'lucide-react'

const PLANS = [
  { name: 'Starter', price: 'R$ 49', features: ['1 usuário', '5GB armazenamento', 'Suporte email', 'API básica'] },
  { name: 'Pro', price: 'R$ 99', features: ['5 usuários', '50GB armazenamento', 'Suporte prioritário', 'API completa', 'Relatórios', 'Integrações'], popular: true },
  { name: 'Enterprise', price: 'R$ 199', features: ['Usuários ilimitados', 'Armazenamento ilimitado', 'Suporte 24/7', 'API dedicada', 'SLA garantido', 'Onboarding personalizado'] },
]

export default function SaasPage() {
  return (
    <div className="min-h-screen">
      <header className="border-b">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-primary">{spec.get('project_name', 'SaaS')}</h1>
          <nav className="hidden md:flex gap-8">
            <a href="#features" className="text-muted-foreground hover:text-primary">Recursos</a>
            <a href="#pricing" className="text-muted-foreground hover:text-primary">Preços</a>
            <a href="#contato" className="text-muted-foreground hover:text-primary">Contato</a>
          </nav>
          <div className="flex gap-4">
            <button className="px-4 py-2 rounded-lg border hover:bg-gray-50">Login</button>
            <button className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:opacity-90">Começar</button>
          </div>
        </div>
      </header>

      <section className="pt-20 pb-16 text-center max-w-4xl mx-auto px-4">
        <h2 className="text-5xl md:text-6xl font-bold mb-6">""".lstrip() + spec.get('goal', 'Transforme seu negócio') + """</h2>
        <p className="text-xl text-muted-foreground mb-8">Solução completa para sua empresa crescer</p>
        <button className="bg-primary text-primary-foreground px-8 py-3 rounded-full text-lg font-semibold inline-flex items-center gap-2">
          Começar Gratuito <ArrowRight className="w-5 h-5" />
        </button>
      </section>

      <section id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <h3 className="text-3xl font-bold text-center mb-12">Planos e Preços</h3>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {PLANS.map((plan, i) => (
              <div key={i} className={`p-8 rounded-2xl border bg-white ${plan.popular ? 'ring-2 ring-primary scale-105' : ''}`}>
                {plan.popular && <span className="text-xs bg-primary text-primary-foreground px-3 py-1 rounded-full mb-4 inline-block">Mais Popular</span>}
                <h4 className="text-xl font-bold">{plan.name}</h4>
                <p className="text-4xl font-bold mt-4 mb-8">{plan.price}<span className="text-lg text-muted-foreground">/mês</span></p>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f, j) => (
                    <li key={j} className="flex items-center gap-2 text-sm"><Check className="w-4 h-4 text-green-500" /> {f}</li>
                  ))}
                </ul>
                <button className={`w-full py-3 rounded-xl font-semibold ${plan.popular ? 'bg-primary text-primary-foreground' : 'border hover:bg-gray-50'}`}>
                  Escolher {plan.name}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
""")
    print(f"[SAAS] Template adicionado com planos e página de vendas")
