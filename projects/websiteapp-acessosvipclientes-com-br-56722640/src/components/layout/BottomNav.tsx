'use client'
import React from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { Home, Briefcase, CreditCard, Headphones, User } from 'lucide-react'

const items: { icon: React.ElementType; label: string; route: string }[] = [{ icon: Home, label: "Inicio", route: "/" }, { icon: Briefcase, label: "Servicos", route: "/servicos" }, { icon: CreditCard, label: "Planos", route: "/planos" }, { icon: Headphones, label: "Suporte", route: "/suporte" }, { icon: User, label: "Conta", route: "/conta" }]

export default function BottomNav() {
  const router = useRouter()
  const pathname = usePathname()
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 h-16 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80 pb-[env(safe-area-inset-bottom)]">
      <div className="flex items-center justify-around max-w-lg mx-auto h-full px-1">
        {items.slice(0, 5).map((item, i) => {
          const active = pathname === item.route
          return (
            <button key={i} type="button" onClick={() => router.push(item.route)}
              className={'flex flex-col items-center gap-0.5 px-2 py-1 rounded-xl transition-all duration-200 ' + (active ? 'text-primary scale-110' : 'text-muted-foreground hover:text-foreground')}>
              <item.icon className="w-5 h-5" />
              <span className="text-[10px] font-medium leading-none">{item.label}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
