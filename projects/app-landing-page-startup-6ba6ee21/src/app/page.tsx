'use client'
import React from 'react'


export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <section className="text-center py-20 px-4">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">landing page startup IA</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">Gerado por FAO HANDS</p>
        <a href="#" className="inline-flex items-center justify-center rounded-lg bg-primary px-8 py-3 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90">Começar</a>
      </section>

      <section className="max-w-5xl mx-auto px-4 py-12">
        <div className="grid gap-6 md:grid-cols-3">
          <div key={0} className="bg-card rounded-xl p-6 border shadow-sm hover:shadow-md transition-shadow"><h3 className="font-semibold mb-2">Feature 1</h3><p className="text-sm text-muted-foreground">Descrição da feature 1</p></div>
          <div key={1} className="bg-card rounded-xl p-6 border shadow-sm hover:shadow-md transition-shadow"><h3 className="font-semibold mb-2">Feature 2</h3><p className="text-sm text-muted-foreground">Descrição da feature 2</p></div>
        </div>
      </section>

      <footer className="border-t py-8 mt-12">
        <div className="max-w-5xl mx-auto px-4 text-center text-sm text-muted-foreground">
          <p className="inline">© 2026 landing-page-startup. Todos os direitos reservados.</p>
        </div>
      </footer>
    </main>
  )
}
