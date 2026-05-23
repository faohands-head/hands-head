'use client'
import React from 'react'
export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <section className="text-center py-20 px-4">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">Hello World</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">Test</p>
        <a href="#" className="inline-flex items-center justify-center rounded-lg bg-primary px-8 py-3 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90">Click</a>
      </section>
    </main>
  )
}
