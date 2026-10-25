$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Project '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) {
    throw 'EvoShield virtual environment was not found. Create .venv and install requirements.txt first.'
}
& $Python -m pip install 'Pillow>=10.0' 'pytesseract>=0.3.10'
if ($LASTEXITCODE -ne 0) { throw 'Could not install Python image OCR packages.' }
$Tesseract = Get-Command tesseract -ErrorAction SilentlyContinue
if (-not $Tesseract) {
    $KnownPath = Join-Path $env:ProgramFiles 'Tesseract-OCR\tesseract.exe'
    if (Test-Path -LiteralPath $KnownPath) {
        $TesseractPath = $KnownPath
    } else {
        $Winget = Get-Command winget -ErrorAction SilentlyContinue
        if (-not $Winget) {
            throw 'Tesseract OCR is missing and winget is unavailable. Install Tesseract OCR for Windows, then rerun this script.'
        }
        & $Winget.Source install --id UB-Mannheim.TesseractOCR --exact --accept-source-agreements --accept-package-agreements
        if ($LASTEXITCODE -ne 0) { throw 'Could not install Tesseract OCR. Install Tesseract OCR for Windows, then rerun this script.' }
        $TesseractPath = Join-Path $env:ProgramFiles 'Tesseract-OCR\tesseract.exe'
    }
    if (-not (Test-Path -LiteralPath $TesseractPath)) {
        throw 'Tesseract installation completed, but tesseract.exe was not found. Restart PowerShell and rerun this script.'
    }
    $env:Path = (Split-Path -Parent $TesseractPath) + ';' + $env:Path
}
Write-Host 'Image OCR is ready. EvoShield can now read visible text in PNG, JPEG, WEBP, BMP, and TIFF images.'
