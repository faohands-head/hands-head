'use client'
import React, { useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { X, Menu, Home, Briefcase, CreditCard, Headphones, User } from 'lucide-react'

const items: { icon: React.ElementType; label: string; route: string }[] = [{ icon: Home, label: "Inicio", route: "/" }, { icon: Briefcase, label: "Servicos", route: "/servicos" }, { icon: CreditCard, label: "Planos", route: "/planos" }, { icon: Headphones, label: "Suporte", route: "/suporte" }, { icon: User, label: "Conta", route: "/conta" }]

export default function Sidebar() {
  const [open, setOpen] = useState(false)
  const router = useRouter()
  const pathname = usePathname()
  return (
    <>
      <button onClick={() => setOpen(true)}
        className="fixed top-4 left-4 z-50 p-2 rounded-xl bg-background/80 backdrop-blur border shadow-sm hover:bg-muted transition-colors">
        <Menu className="w-5 h-5" />
      </button>
      {open && <div className="fixed inset-0 bg-black/40 z-40" onClick={() => setOpen(false)} />}
      <aside className={"fixed top-0 left-0 h-full w-72 bg-background border-r z-50 transform transition-transform duration-300 shadow-2xl " + (open ? 'translate-x-0' : '-translate-x-full')}>
        <div className="flex items-center justify-between p-4 border-b">
          <span className="font-bold text-lg">Acessos VIP Clientes</span>
          <button onClick={() => setOpen(false)} className="hover:bg-muted p-1 rounded-lg transition-colors"><X className="w-5 h-5" /></button>
        </div>
        <nav className="p-2">
          {items.map((item, i) => {
            const isActive = pathname === item.route
            return (
              <a key={i} href={item.route} onClick={(e) => { e.preventDefault(); router.push(item.route); setOpen(false) }}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-colors mb-1 ${isActive ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-muted text-foreground'}`}>
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </a>
            )
          })}
        </nav>
      </aside>
    </>
  )
}
