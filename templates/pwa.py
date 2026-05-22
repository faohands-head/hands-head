"""PWA Template with offline support"""
def add_to_project(project_dir: str, spec: dict):
    from pathlib import Path
    p = Path(project_dir)
    
    # service worker
    (p / "public").mkdir(exist_ok=True)
    (p / "public/sw.js").write_text("""const CACHE_NAME = 'v1'
const urlsToCache = ['/', '/index.html']

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache)))
})

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => response || fetch(event.request))
  )
})
""")
    
    # manifest.json
    (p / "public/manifest.json").write_text("""{
  "name": \"""" + spec.get('project_name', 'PWA') + """\",
  "short_name": \"""" + spec.get('project_name', 'PWA')[:15] + """\",
  "description": \"""" + spec.get('goal', 'App PWA') + """\",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
""")
    
    (p / "src/app/page.tsx").write_text("""'use client'

import { useEffect, useState } from 'react'
import { Wifi, WifiOff, RefreshCw } from 'lucide-react'

export default function PwaPage() {
  const [isOnline, setIsOnline] = useState(true)
  const [registered, setRegistered] = useState(false)

  useEffect(() => {
    setIsOnline(navigator.onLine)
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').then(() => setRegistered(true))
    }

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
          <h1 className="text-xl font-bold flex items-center gap-2">
            {isOnline ? <Wifi className="w-5 h-5 text-green-500" /> : <WifiOff className="w-5 h-5 text-red-500" />}
            {spec.get('project_name', 'PWA App')}
          </h1>
          {registered && <span className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full">Offline Ready</span>}
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">Bem-vindo ao """ + spec.get('project_name', 'App') + """</h2>
          <p className="text-xl text-muted-foreground">Funciona mesmo offline</p>
        </div>

        <div className="bg-white rounded-2xl p-8 shadow-sm border text-center">
          <RefreshCw className="w-12 h-12 mx-auto text-primary mb-4" />
          <p className="text-lg mb-6">Este app funciona offline. Teste desconectando a internet!</p>
          <div className="flex justify-center gap-4">
            <button className="bg-primary text-primary-foreground px-6 py-3 rounded-xl font-semibold hover:opacity-90"
              onClick={() => alert('App pronto para uso offline!')}>
              Testar
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
""")
    print(f"[PWA] Template adicionado com service worker e suporte offline")
