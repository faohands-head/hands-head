import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'WebsiteApp Acessos VIP Clientes',
  description: 'WebsiteApp: Acessosvip Websiteapp',
  manifest: '/manifest.json',
  appleWebApp: { capable: true, statusBarStyle: 'default', title: 'WebsiteApp Acessos VIP Clientes' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={inter.className + ' pb-16 md:pb-0 antialiased'}>
        {children}
      </body>
    </html>
  )
}
