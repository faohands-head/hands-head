'use client'

import React, { useState } from 'react'
import { X, Menu, Home, Briefcase, CreditCard, Headphones, User } from 'lucide-react'

const items: { icon: React.ElementType; label: string }[] = [
  { icon: Home, label: 'Inicio' },
  { icon: Briefcase, label: 'Servicos' },
  { icon: CreditCard, label: 'Planos' },
  { icon: Headphones, label: 'Suporte' },
  { icon: User, label: 'Conta' },
]

export default function Sidebar() {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button onClick={() => setOpen(true)}
        className="fixed top-4 left-4 z-50 p-2 rounded-xl bg-background/80 backdrop-blur border shadow-sm">
        <Menu className="w-5 h-5" />
      </button>
      {open && <div className="fixed inset-0 bg-black/40 z-40" onClick={() => setOpen(false)} />}
      <aside className={"fixed top-0 left-0 h-full w-72 bg-background border-r z-50 transform transition-transform duration-300 shadow-2xl " + (open ? 'translate-x-0' : '-translate-x-full')}>
        <div className="flex items-center justify-between p-4 border-b">
          <span className="font-bold text-lg">Cliente</span>
          <button onClick={() => setOpen(false)}><X className="w-5 h-5" /></button>
        </div>
        <nav className="p-2">
          {items.map((item, i) => (
            <a key={i} href="#" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-muted transition-colors">
              <item.icon className="w-5 h-5 text-muted-foreground" />
              <span>{item.label}</span>
            </a>
          ))}
        </nav>
      </aside>
    </>
  )
}
