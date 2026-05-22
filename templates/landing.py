"""Landing Page Template"""
def add_to_project(project_dir: str, spec: dict):
    from pathlib import Path
    p = Path(project_dir)
    
    # app/page.tsx - Landing page completa
    (p / "src/app/page.tsx").write_text("""'use client'

import { useState } from 'react'
import { Phone, Calendar, ChevronRight, Star, Menu, X } from 'lucide-react'

const NAV_ITEMS = ['Home', 'Serviços', 'Depoimentos', 'Contato']

export default function LandingPage() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [form, setForm] = useState({ nome: '', email: '', telefone: '', mensagem: '' })

  const handleSubmit = (e) => {
    e.preventDefault()
    alert('Agendamento enviado! Entraremos em contato.')
  }

  return (
    <div className="min-h-screen">
      <header className="fixed top-0 w-full bg-white/95 backdrop-blur z-50 border-b">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-primary">{spec.get('project_name', 'Empresa')}</h1>
          <nav className="hidden md:flex gap-8">
            {NAV_ITEMS.map(item => (
              <a key={item} href={`#${item.toLowerCase()}`} className="text-muted-foreground hover:text-primary transition">
                {item}
              </a>
            ))}
          </nav>
          <a href="https://wa.me/5511999999999" target="_blank"
             className="hidden md:flex items-center gap-2 bg-green-500 text-white px-4 py-2 rounded-full hover:bg-green-600 transition">
            <Phone className="w-4 h-4" /> WhatsApp
          </a>
          <button className="md:hidden" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </header>

      <section id="home" className="pt-32 pb-20 bg-gradient-to-br from-blue-50 via-white to-blue-50">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h2 className="text-5xl md:text-7xl font-bold mb-6">{spec.get('goal', 'Sua melhor escolha')}</h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Profissionais dedicados ao seu sorriso com tecnologia de ponta e atendimento humanizado
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="#contato" className="bg-primary text-primary-foreground px-8 py-3 rounded-full text-lg font-semibold hover:opacity-90 transition flex items-center justify-center gap-2">
              Agende sua Consulta <Calendar className="w-5 h-5" />
            </a>
            <a href="https://wa.me/5511999999999" target="_blank"
               className="bg-green-500 text-white px-8 py-3 rounded-full text-lg font-semibold hover:bg-green-600 transition flex items-center justify-center gap-2">
              Fale Conosco <Phone className="w-5 h-5" />
            </a>
          </div>
        </div>
      </section>

      <section id="servicos" className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <h3 className="text-3xl font-bold text-center mb-12">Nossos Serviços</h3>
          <div className="grid md:grid-cols-3 gap-8">
            {['Implantes Dentários', 'Clareamento', 'Ortodontia'].map((s, i) => (
              <div key={i} className="p-8 rounded-2xl border bg-white hover:shadow-lg transition">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Star className="w-6 h-6 text-primary" />
                </div>
                <h4 className="text-xl font-semibold mb-2">{s}</h4>
                <p className="text-muted-foreground">Tecnologia avançada e profissionais especializados para o melhor tratamento.</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="depoimentos" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <h3 className="text-3xl font-bold text-center mb-12">O que nossos pacientes dizem</h3>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { nome: 'Maria S.', texto: 'Excelente atendimento! Meu sorriso nunca esteve tão bonito.' },
              { nome: 'João P.', texto: 'Equipe muito profissional e dedicada. Recomendo!' },
              { nome: 'Ana C.', texto: 'Resultado incrível! Superou todas as minhas expectativas.' }
            ].map((d, i) => (
              <div key={i} className="p-6 rounded-2xl bg-white border">
                <div className="flex gap-1 mb-3">
                  {[...Array(5)].map((_, j) => <Star key={j} className="w-4 h-4 fill-yellow-400 text-yellow-400" />)}
                </div>
                <p className="text-muted-foreground mb-4">{d.texto}</p>
                <p className="font-semibold">- {d.nome}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="contato" className="py-20">
        <div className="max-w-3xl mx-auto px-4">
          <h3 className="text-3xl font-bold text-center mb-12">Agende sua Consulta</h3>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <input placeholder="Nome" value={form.nome} onChange={e => setForm({...form, nome: e.target.value})}
                     className="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-primary outline-none" required />
              <input placeholder="E-mail" type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                     className="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-primary outline-none" required />
              <input placeholder="Telefone" type="tel" value={form.telefone} onChange={e => setForm({...form, telefone: e.target.value})}
                     className="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-primary outline-none" required />
              <input placeholder="Melhor horário" value={form.mensagem} onChange={e => setForm({...form, mensagem: e.target.value})}
                     className="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-primary outline-none" />
            </div>
            <button type="submit" className="w-full bg-primary text-primary-foreground py-4 rounded-xl text-lg font-semibold hover:opacity-90 transition flex items-center justify-center gap-2">
              Agendar <ChevronRight className="w-5 h-5" />
            </button>
          </form>
        </div>
      </section>

      <footer className="py-8 bg-gray-900 text-white text-center">
        <p>© 2025 {spec.get('project_name', 'Empresa')}. Todos os direitos reservados.</p>
      </footer>

      <a href="https://wa.me/5511999999999" target="_blank"
         className="fixed bottom-6 right-6 bg-green-500 text-white p-4 rounded-full shadow-lg hover:bg-green-600 transition z-50">
        <Phone className="w-6 h-6" />
      </a>
    </div>
  )
}
""")
    
    # app/layout.tsx
    (p / "src/app/layout.tsx").write_text("""import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '""" + spec.get('project_name', 'Clínica') + """',
  description: '""" + spec.get('goal', 'Landing Page') + """',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
""")
    
    print(f"[LANDING] Componentes adicionados: Hero, Serviços, Depoimentos, Contato, WhatsApp")
