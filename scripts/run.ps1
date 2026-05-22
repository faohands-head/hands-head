param([string]$briefing = "criar landing page para clínica odontológica premium")

Write-Host "=== FAO HANDS - Multi-Agent Orchestrator ===" -ForegroundColor Cyan
Write-Host "Briefing: $briefing" -ForegroundColor Yellow
Write-Host ""

# Verificar serviços
Write-Host "[CHECK] OpenHands..." -NoNewline
try {
    $r = curl.exe -s -o nul -w "%{http_code}" http://localhost:3001 2>$null
    if ($r -eq "200") { Write-Host " OK" -ForegroundColor Green } else { Write-Host " FALHA ($r)" -ForegroundColor Red }
} catch { Write-Host " ERRO" -ForegroundColor Red }

Write-Host "[CHECK] Ollama..." -NoNewline
try {
    $r = curl.exe -s http://localhost:11434/api/tags 2>$null
    if ($r -match "qwen") { Write-Host " OK (qwen2.5-coder)" -ForegroundColor Green } else { Write-Host " SEM MODELO" -ForegroundColor Red }
} catch { Write-Host " ERRO" -ForegroundColor Red }

& "C:\Users\faoss\AppData\Local\Programs\Python\Python315\python.exe" C:\FaoFluxo\FAO-HANDS\scripts\caid.py $briefing

Write-Host ""
Write-Host "=== CONCLUÍDO ===" -ForegroundColor Green
