import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'WebsiteApp Quotes to Scrape',
  description: 'WebsiteApp baseado em https://quotes.toscrape.com/',
  manifest: '/manifest.json',
  appleWebApp: { capable: true, statusBarStyle: 'default', title: 'WebsiteApp Quotes to Scrape' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={inter.className + ' pb-16 md:pb-0'}>
        {children}
      </body>
    </html>
  )
}
