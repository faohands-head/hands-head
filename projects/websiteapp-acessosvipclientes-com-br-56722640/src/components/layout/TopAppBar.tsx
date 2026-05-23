'use client'
import React from 'react'
import { Menu, Search, Moon, Sun } from 'lucide-react'
import { useTheme } from '@/components/ThemeProvider'

type Props = { title: string; onMenuClick?: () => void }

export default function TopAppBar({ title, onMenuClick }: Props) {
  const { theme, toggle } = useTheme()
  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-14 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80 pt-[env(safe-area-inset-top)]">
      <div className="flex items-center justify-between h-14 px-3 md:px-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 min-w-0">
          <button type="button" onClick={onMenuClick} className="md:hidden p-2 rounded-xl hover:bg-muted" aria-label="Abrir menu">
            <Menu className="w-5 h-5" />
          </button>
          <span className="font-semibold text-base md:text-lg truncate">WebsiteApp Acessos VIP Clientes</span>
        </div>
        <div className="flex items-center gap-1">
          <button type="button" className="p-2 rounded-xl hover:bg-muted text-muted-foreground" aria-label="Buscar">
            <Search className="w-5 h-5" />
          </button>
          <button type="button" onClick={toggle} className="p-2 rounded-xl hover:bg-muted" aria-label="Alternar tema">
            {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </header>
  )
}
