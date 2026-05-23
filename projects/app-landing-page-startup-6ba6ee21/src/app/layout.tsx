import type { Metadata } from 'next'
import './globals.css'
export const metadata: Metadata = { title: 'landing-page-startup', description: 'landing page startup IA' }
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="pt-BR"><body>{children}</body></html>
}
