'use client'

import React, { useState } from 'react'
import { Home, Briefcase, CreditCard, Headphones, User } from 'lucide-react'

const items: { icon: React.ElementType; label: string }[] = [
  { icon: Home, label: 'Inicio' },
  { icon: Briefcase, label: 'Servicos' },
  { icon: CreditCard, label: 'Planos' },
  { icon: Headphones, label: 'Suporte' },
  { icon: User, label: 'Conta' },
]

export default function BottomNav() {
  const [active, setActive] = useState(0)
  return (
    <nav className="fixed bottom-0 left-0 right-10 flex justify-center z-50 h-16 border-t bg-background safe-area-bottom pb-1">
      <div className="flex items-center justify-around max-w-lg w-full px-2">
        {items.map((item, i) => (
          <button key={i} onClick={() => setActive(i)}
            className={`flex flex-col items-center gap-0.5 px-3 py-1 rounded-xl transition-all duration-200
              ${active === i ? 'text-primary scale-110' : 'text-muted-foreground hover:text-foreground'}`}>
            <item.icon className="w-5 h-5" />
            <span className="text-[10px] font-medium">{item.label}</span>
          </button>
        ))}
      </div>
    </nav>
  )
}
