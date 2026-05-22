'use client'

import BottomNav from '@/components/layout/BottomNav'
import Sidebar from '@/components/layout/Sidebar'

const sections = [{"type": "hero", "title": "choices", "text": "deep-thoughts", "className": ""}, {"type": "cards", "items": [{"title": "“I have not failed. I've just found 10,000 ways that won't w", "text": "“I have not failed. I've just found 10,000 ways that won't work.”"}, {"title": "humor", "text": "humor"}, {"title": "simile", "text": "simile"}, {"title": "be-yourself", "text": "be-yourself"}, {"title": "“The person, be it gentleman or lady, who has not pleasure i", "text": "“The person, be it gentleman or lady, who has not pleasure in a good novel, must be intolerably stupid.”"}, {"title": "Thomas A. Edison", "text": "Thomas A. Edison"}], "className": ""}, {"type": "content", "paragraphs": ["“It is our choices, Harry, that show what we truly are, far more than our abilities.”", "misattributed-eleanor-roosevelt", "“A day without sunshine is like, you know, night.”", "“It is better to be hated for what you are than to be loved for what you are not.”", "“A woman is like a tea bag; you never know how strong it is until it's in hot water.”", "“There are only two ways to live your life. One is as though nothing is a miracle. The other is as though everything is a miracle.”", "“Imperfection is beauty, madness is genius and it's better to be absolutely ridiculous than absolutely boring.”", "“Try not to become a man of success. Rather become a man of value.”", "“The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”"], "className": ""}, {"type": "footer", "text": "(c) 2026 Quotes to Scrape. Todos os direitos reservados.", "className": ""}]

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
                {section.items.map((item, j) => (
                  <div key={j} className="bg-card rounded-2xl p-6 shadow-sm border hover:shadow-md transition-shadow">
                    <h3 className="font-semibold mb-2">{item.title}</h3>
                    <p className="text-sm text-muted-foreground">{item.text}</p>
                  </div>
                ))}
              </div>
            )}
            {section.type === 'content' && section.paragraphs && (
              <div className="prose prose-gray max-w-none">
                {section.paragraphs.map((p, j) => (
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
