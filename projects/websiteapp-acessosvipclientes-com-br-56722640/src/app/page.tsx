'use client'

import BottomNav from '@/components/layout/BottomNav'
import Sidebar from '@/components/layout/Sidebar'

const sections: any[] = [{"type": "hero", "title": "Acessos VIP Clientes é uma empresa que oferece soluções de acesso e gestão de clientes.", "text": "Bem-vindo à Acessos VIP Clientes. Sua solução completa em gestão de acessos.", "className": ""}, {"type": "cards", "items": [{"title": "Oferecemos tecnologia de ponta para controle de entrada e sa", "text": "Oferecemos tecnologia de ponta para controle de entrada e saída."}, {"title": "Nossos sistemas são integrados com as principais plataformas", "text": "Nossos sistemas são integrados com as principais plataformas do mercado."}, {"title": "Mais de 500 empresas confiam na Acessos VIP Clientes.", "text": "Mais de 500 empresas confiam na Acessos VIP Clientes."}, {"title": "Suporte técnico especializado disponível 24 horas por dia.", "text": "Suporte técnico especializado disponível 24 horas por dia."}, {"title": "Solicite uma demonstração gratuita e descubra como podemos a", "text": "Solicite uma demonstração gratuita e descubra como podemos ajudar."}, {"title": "Transforme a gestão de acessos da sua empresa com a Acessos ", "text": "Transforme a gestão de acessos da sua empresa com a Acessos VIP Clientes."}], "className": ""}, {"type": "footer", "text": "(c) 2026 Cliente. Todos os direitos reservados.", "className": ""}]

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
      <Sidebar />
      <main className="max-w-5xl mx-auto px-4 pt-20 pb-24 md:pb-12">
        {sections.map((section, i) => (
          <section key={i} className={'mb-16 ' + (section.className || '')}>
            {section.type === 'hero' && (
              <header className="text-center mb-12">
                <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">{section.title}</h1>
                <p className="text-xl text-muted-foreground max-w-3xl mx-auto">{section.text}</p>
              </header>
            )}
            {section.type === 'cards' && section.items && (
              <div className="grid gap-6 md:grid-cols-3">
                {section.items.map((item: any, j: number) => (
                  <div key={j} className="bg-card rounded-2xl p-6 shadow-sm border hover:shadow-md transition-shadow">
                    <h3 className="font-semibold mb-2">{item.title}</h3>
                    <p className="text-sm text-muted-foreground">{item.text}</p>
                  </div>
                ))}
              </div>
            )}
            {section.type === 'content' && section.paragraphs && (
              <div className="prose prose-gray max-w-none">
                {section.paragraphs.map((p: string, j: number) => (
                  <p key={j} className="text-muted-foreground mb-4">{p}</p>
                ))}
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
