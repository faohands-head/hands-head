'use client'
import React from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { X, Home, Briefcase, CreditCard, Headphones, User } from 'lucide-react'

const items: { icon: React.ElementType; label: string; route: string }[] = [{ icon: Home, label: "Inicio", route: "/" }, { icon: Briefcase, label: "Servicos", route: "/servicos" }, { icon: CreditCard, label: "Planos", route: "/planos" }, { icon: Headphones, label: "Suporte", route: "/suporte" }, { icon: User, label: "Conta", route: "/conta" }]

type Props = { mobileOpen?: boolean; onClose?: () => void }

export default function Sidebar({ mobileOpen = false, onClose }: Props) {
  const router = useRouter()
  const pathname = usePathname()

  const nav = (
    <nav className="p-3 space-y-1">
      {items.map((item, i) => {
        const isActive = pathname === item.route
        return (
          <button key={i} type="button" onClick={() => { router.push(item.route); onClose?.() }}
            className={'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors text-left ' + (isActive ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-muted text-foreground')}>
            <item.icon className="w-5 h-5 shrink-0" />
            <span>{item.label}</span>
          </button>
        )
      })}
    </nav>
  )

  return (
    <>
      <aside className="hidden md:flex md:flex-col md:fixed md:top-14 md:left-0 md:w-[270px] md:h-[calc(100vh-3.5rem)] md:border-r md:bg-background/95 md:z-30">
        <div className="p-4 border-b font-bold text-lg truncate">Acessos VIP Clientes</div>
        {nav}
      </aside>
      {mobileOpen && <div className="md:hidden fixed inset-0 bg-black/40 z-40" onClick={onClose} aria-hidden />}
      <aside className={'md:hidden fixed top-0 left-0 h-full w-[270px] bg-background border-r z-50 shadow-2xl transform transition-transform duration-300 ' + (mobileOpen ? 'translate-x-0' : '-translate-x-full')}>
        <div className="flex items-center justify-between p-4 border-b mt-14">
          <span className="font-bold text-lg truncate">Acessos VIP Clientes</span>
          <button type="button" onClick={onClose} className="hover:bg-muted p-1 rounded-lg" aria-label="Fechar menu"><X className="w-5 h-5" /></button>
        </div>
        {nav}
      </aside>
    </>
  )
}
