"""Dashboard Template"""
def add_to_project(project_dir: str, spec: dict):
    from pathlib import Path
    p = Path(project_dir)
    
    (p / "src/app/dashboard").mkdir(parents=True, exist_ok=True)
    
    (p / "src/app/page.tsx").write_text("""'use client'

import { BarChart3, Users, TrendingUp, DollarSign, Bell, Search, Menu } from 'lucide-react'

const stats = [
  { label: 'Receita Total', value: 'R$ 127.500', icon: DollarSign, change: '+12.5%' },
  { label: 'Usuários Ativos', value: '2.847', icon: Users, change: '+8.2%' },
  { label: 'Conversões', value: '847', icon: TrendingUp, change: '+15.3%' },
  { label: 'Ticket Médio', value: 'R$ 150', icon: BarChart3, change: '+5.1%' },
]

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b h-16 flex items-center px-6">
        <Menu className="w-6 h-6 mr-4 cursor-pointer md:hidden" />
        <h1 className="text-xl font-bold flex-1">{spec.get('project_name', 'Dashboard')}</h1>
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
          <input className="pl-10 pr-4 py-2 rounded-lg border bg-gray-50 w-64" placeholder="Buscar..." />
        </div>
        <Bell className="w-5 h-5 ml-6 text-muted-foreground cursor-pointer" />
      </header>

      <main className="p-6">
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          {stats.map((s, i) => (
            <div key={i} className="bg-white p-6 rounded-xl border">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-muted-foreground">{s.label}</span>
                <s.icon className="w-5 h-5 text-primary" />
              </div>
              <p className="text-2xl font-bold">{s.value}</p>
              <p className="text-sm text-green-600 mt-1">{s.change}</p>
            </div>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl border">
            <h3 className="font-semibold mb-4">Atividade Recente</h3>
            <div className="space-y-4">
              {[
                { user: 'João Silva', action: 'completou onboarding', time: '5min atrás' },
                { user: 'Maria Santos', action: 'fez upgrade Pro', time: '15min atrás' },
                { user: 'Pedro Costa', action: 'criou novo projeto', time: '1h atrás' },
                { user: 'Ana Oliveira', action: 'ativou conta', time: '2h atrás' },
              ].map((a, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div><span className="font-medium">{a.user}</span> <span className="text-muted-foreground">{a.action}</span></div>
                  <span className="text-xs text-muted-foreground">{a.time}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl border">
            <h3 className="font-semibold mb-4">Tarefas Pendentes</h3>
            <div className="space-y-3">
              {['Revisar relatório mensal', 'Aprovar orçamento Q3', 'Atualizar roadmap', 'Responder feedback'].map((t, i) => (
                <label key={i} className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" className="w-4 h-4 rounded border-gray-300" />
                  <span className="text-sm">{t}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
""")
    print(f"[DASHBOARD] Template adicionado com cards, atividade e tarefas")
