param(
    [Parameter(Mandatory=$true)]
    [string]$LlvmMingwRoot
)

$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Clang = Join-Path $LlvmMingwRoot 'bin\clang++.exe'
$ReadObj = Join-Path $LlvmMingwRoot 'bin\llvm-readobj.exe'
$Source = Join-Path $Root 'NemoChainProbe161.cpp'
$Output = Join-Path $Root 'NemoChainProbe161.dll'

if (-not (Test-Path -LiteralPath $Clang)) {
    throw "clang++.exe not found under $LlvmMingwRoot"
}

if (Test-Path -LiteralPath $Output) {
    Remove-Item -LiteralPath $Output -Force
}

& $Clang `
    --target=x86_64-w64-windows-gnu `
    -std=c++17 `
    -O2 `
    -fno-exceptions `
    -fno-rtti `
    -shared `
    -o $Output `
    $Source

if ($LASTEXITCODE -ne 0) {
    throw "clang++ failed with exit code $LASTEXITCODE"
}

$Hash = (Get-FileHash -LiteralPath $Output -Algorithm SHA256).Hash
$Size = (Get-Item -LiteralPath $Output).Length

Write-Host 'BUILD_OK'
Write-Host "SIZE=$Size"
Write-Host "SHA256=$Hash"

if (Test-Path -LiteralPath $ReadObj) {
    & $ReadObj --coff-exports --coff-imports $Output
}
