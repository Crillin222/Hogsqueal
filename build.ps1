# build.ps1 — limpa, garante venv, instala deps e builda via .spec
$ErrorActionPreference = 'Stop'

# 1) Criar venv se não existir
if (-not (Test-Path .\.venv\Scripts\python.exe)) {
  Write-Host ">> Criando venv..." -ForegroundColor Cyan
  python -m venv .venv
}

# 2) Atualizar pip e instalar dependências de build no venv
Write-Host ">> Instalando dependências..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install pyinstaller PySide6 requests certifi

# 3) Limpeza
Write-Host ">> Limpando build/dist anteriores..." -ForegroundColor Cyan
Remove-Item -Recurse -Force .\build, .\dist -ErrorAction SilentlyContinue

# 4) Build a partir do .spec (one-dir)
Write-Host ">> Buildando via PyInstaller (.spec)..." -ForegroundColor Cyan
.\.venv\Scripts\pyinstaller.exe --clean --noconfirm .\Hobgoblin.spec

# 5) Resultado
if (Test-Path .\dist\Hobgoblin\Hobgoblin.exe) {
  Write-Host "`nSUCESSO! Pasta final:" -ForegroundColor Green
  Write-Host (Resolve-Path .\dist\Hobgoblin\) -ForegroundColor Yellow
} else {
  Write-Host "`nAlgo deu errado. Verifique os logs acima." -ForegroundColor Red
  exit 1
}
