'use client'
import BottomNav from '@/components/layout/BottomNav'
import Sidebar from '@/components/layout/Sidebar'
import { ArrowRight, CheckCircle } from 'lucide-react'

const sections: any = [{"type": "hero", "title": "Nossos Servicos", "text": "Conheca tudo o que oferecemos", "className": ""}, {"type": "cards", "items": [{"title": "Acessos VIP Clientes é uma empresa que oferece soluções de acesso e gestão de cl", "text": "Acessos VIP Clientes é uma empresa que oferece soluções de acesso e gestão de clientes."}, {"title": "Gestão de acessos VIP", "text": "Gestão de acessos VIP"}, {"title": "Controle de entrada e saída", "text": "Controle de entrada e saída"}, {"title": "Relatórios personalizados", "text": "Relatórios personalizados"}, {"title": "Integração com sistemas terceiros", "text": "Integração com sistemas terceiros"}, {"title": "Suporte 24 horas", "text": "Suporte 24 horas"}, {"title": "Bem-vindo à Acessos VIP Clientes. Sua solução completa em gestão de acessos.", "text": "Bem-vindo à Acessos VIP Clientes. Sua solução completa em gestão de acessos."}, {"title": "Oferecemos tecnologia de ponta para controle de entrada e saída.", "text": "Oferecemos tecnologia de ponta para controle de entrada e saída."}, {"title": "Plano Básico: Acesso simples com relatórios mensais", "text": "Plano Básico: Acesso simples com relatórios mensais"}, {"title": "Plano Profissional: Gestão completa + integrações", "text": "Plano Profissional: Gestão completa + integrações"}, {"title": "Plano Enterprise: Tudo do Profissional + suporte dedicado + SLA", "text": "Plano Enterprise: Tudo do Profissional + suporte dedicado + SLA"}], "className": ""}, {"type": "content", "paragraphs": ["Acessos VIP Clientes é uma empresa que oferece soluções de acesso e gestão de clientes.", "Gestão de acessos VIP", "Controle de entrada e saída", "Relatórios personalizados", "Integração com sistemas terceiros", "Suporte 24 horas", "Bem-vindo à Acessos VIP Clientes. Sua solução completa em gestão de acessos.", "Oferecemos tecnologia de ponta para controle de entrada e saída.", "Nossos sistemas são integrados com as principais plataformas do mercado.", "Mais de 500 empresas confiam na Acessos VIP Clientes.", "Suporte técnico especializado disponível 24 horas por dia.", "Transforme a gestão de acessos da sua empresa com a Acessos VIP Clientes.", "Solicite uma demonstração gratuita e descubra como podemos ajudar.", "Plano Básico: Acesso simples com relatórios mensais", "Plano Profissional: Gestão completa + integrações", "Plano Enterprise: Tudo do Profissional + suporte dedicado + SLA"], "className": ""}, {"type": "footer", "text": "(c) 2026 Acessos VIP Clientes. Todos os direitos reservados.", "className": ""}]

export default function Page() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
      <Sidebar />
      <main className="max-w-5xl mx-auto px-4 pt-20 pb-24 md:pb-12">
        {sections.map((section: any, i: number) => (
          <section key={i} className={'mb-16 ' + (section.className || '')}>
            {section.type === 'hero' && (
              <header className="text-center mb-12 py-8">
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">{section.title}</h1>
                {section.text && <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">{section.text}</p>}
              </header>
            )}
            {section.type === 'cards' && section.items && (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {section.items.map((item: any, j: number) => (
                  <div key={j} className="group bg-card rounded-2xl p-6 shadow-sm border hover:shadow-lg hover:border-primary/20 transition-all duration-300">
                    <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                      <CheckCircle className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="font-semibold mb-2 text-lg">{item.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{item.text}</p>
                  </div>
                ))}
              </div>
            )}
            {section.type === 'content' && section.paragraphs && (
              <div className="max-w-3xl mx-auto">
                <div className="space-y-6">
                  {section.paragraphs.map((p, j) => (
                    <p key={j} className="text-muted-foreground leading-relaxed text-lg">{p}</p>
                  ))}
                </div>
              </div>
            )}
            {section.type === 'stats' && section.items && (
              <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
                {section.items.map((item, j) => (
                  <div key={j} className="bg-card rounded-xl border p-6 shadow-sm hover:shadow-md transition-shadow text-center">
                    <p className="text-2xl font-bold text-primary">{item.value}</p>
                    <p className="text-sm text-muted-foreground mt-1">{item.label}</p>
                  </div>
                ))}
              </div>
            )}
            {section.type === 'cta' && (
              <div className="rounded-2xl border bg-card p-8 md:p-12 text-center shadow-sm">
                <h2 className="text-2xl md:text-3xl font-bold mb-4">{section.title}</h2>
                {section.text && <p className="text-muted-foreground mb-8 max-w-xl mx-auto">{section.text}</p>}
                <a href={section.button_url || '#contato'}
                  className="inline-flex items-center gap-2 rounded-xl bg-primary px-8 py-3 text-sm font-medium text-primary-foreground shadow transition-all hover:bg-primary/90 hover:shadow-lg hover:scale-105 active:scale-100">
                  {section.button_label || 'Saiba Mais'}
                  <ArrowRight className="w-4 h-4" />
                </a>
              </div>
            )}
            {section.type === 'pricing' && section.plans && (
              <div className="grid gap-6 md:grid-cols-3">
                {section.plans.map((plan, j) => (
                  <div key={j} className={`bg-card rounded-xl border p-6 shadow-sm flex flex-col hover:shadow-lg transition-shadow ${j === 1 ? 'border-primary ring-1 ring-primary' : ''}`}>
                    {j === 1 && <span className="text-xs font-semibold text-primary bg-primary/10 px-3 py-1 rounded-full self-start mb-3">Mais Popular</span>}
                    <h3 className="text-lg font-semibold">{plan.name}</h3>
                    <p className="text-3xl font-bold mt-2">{plan.price}</p>
                    {plan.features && plan.features.length > 0 && (
                      <ul className="mt-4 space-y-2 flex-1">
                        {plan.features.map((feat, k) => (
                          <li key={k} className="text-sm text-muted-foreground flex items-start gap-2">
                            <CheckCircle className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                            {feat}
                          </li>
                        ))}
                      </ul>
                    )}
                    <a href={plan.cta_url || '#contato'} className="mt-6 inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground shadow transition-all hover:bg-primary/90 hover:shadow-md">
                      {plan.cta || 'Contratar'}
                    </a>
                  </div>
                ))}
              </div>
            )}
            {section.type === 'form' && section.fields && (
              <div className="max-w-lg mx-auto bg-card rounded-xl border p-8 shadow-sm">
                <form className="space-y-4">
                  {section.fields.map((f, j) => (
                    <div key={j}>
                      <label className="text-sm font-medium mb-1.5 block">{f.label}</label>
                      {f.type === 'textarea'
                        ? <textarea className="flex min-h-[100px] w-full rounded-lg border bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors" name={f.name} required={f.required} />
                        : <input type={f.type} className="flex h-10 w-full rounded-lg border bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors" name={f.name} required={f.required} />}
                    </div>
                  ))}
                  <button type="submit" className="inline-flex items-center justify-center rounded-lg bg-primary px-8 py-2.5 text-sm font-medium text-primary-foreground shadow transition-all hover:bg-primary/90 hover:shadow-md w-full">
                    {section.submit_label || 'Enviar'}
                  </button>
                </form>
              </div>
            )}
            {section.type === 'footer' && (
              <footer className="border-t pt-8 mt-12 text-center text-sm text-muted-foreground">
                <p>{section.text}</p>
              </footer>
            )}
          </section>
        ))}
      </main>
      <BottomNav />
    </div>
  )
}
