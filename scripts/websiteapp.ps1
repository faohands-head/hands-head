param([string]$url = "", [switch]$fromBrain)

$FAO_DIR = "C:\FaoFluxo\FAO-HANDS"
$PY = "C:\Users\faoss\AppData\Local\Programs\Python\Python315\python.exe"
$env:PYTHONPATH = "$FAO_DIR\scripts;$FAO_DIR\templates"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FAO HANDS - WebsiteApp Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($fromBrain) {
    $briefings = Get-ChildItem "$FAO_DIR\vault\briefings\*.md" | Sort-Object LastWriteTime -Descending
    if (-not $briefings) { Write-Host "Nenhum briefing encontrado." -ForegroundColor Red; exit 1 }
    Write-Host "Briefings:" -ForegroundColor Yellow
    $i = 0; $briefings | ForEach-Object { Write-Host "  [$i] $($_.Name)"; $i++ }
    $choice = Read-Host "`nNumero (Enter = 0)"
    $idx = if ($choice -match '^\d+$') { [int]$choice } else { 0 }
    & $PY "$FAO_DIR\scripts\websiteapp.py" --from-brain $briefings[$idx].Name
}
elseif ($url) {
    & $PY "$FAO_DIR\scripts\websiteapp.py" --url $url
}
else {
    Write-Host "`nModos de uso:" -ForegroundColor Cyan
    Write-Host "  1. Informar URL do cliente" -ForegroundColor White
    Write-Host "  2. Usar briefing do Obsidian" -ForegroundColor White
    $mode = Read-Host "`nEscolha (1 ou 2)"
    if ($mode -eq "2") {
        & $PSCommandPath -fromBrain
    } else {
        $u = Read-Host "URL do site do cliente"
        & $PSCommandPath -url $u
    }
}
