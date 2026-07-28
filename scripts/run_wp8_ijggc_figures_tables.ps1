param()

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

Write-Host "[WP8] Building IJGGC figures, tables and supplementary data"
& python (Join-Path $Root "scripts\journal_neutral\build_wp8_ijggc_figures_tables.py")
if ($LASTEXITCODE -ne 0) { throw "WP8 figure/table build failed." }

Write-Host "[WP8] Validating evidence denominators, traceability and release boundaries"
& python (Join-Path $Root "scripts\journal_neutral\validate_wp8_ijggc_figures_tables.py")
if ($LASTEXITCODE -ne 0) { throw "WP8 figure/table validation failed." }

Write-Host "[WP8] PASS"
