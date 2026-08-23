$ErrorActionPreference = "Stop"
Write-Host "=== CAP NHAT TU BINH GIA DINH V1 -> VERCEL ===" -ForegroundColor Cyan
if (-not (Test-Path ".git")) {
  Write-Host "LOI: Hay chay file nay trong thu muc repo GitHub tu-binh-gia-dinh-v1 (noi co thu muc .git)." -ForegroundColor Red
  exit 1
}
git add -A
git status --short
$confirm = Read-Host "Tiep tuc commit va push? (Y/N)"
if ($confirm -notin @('Y','y')) { exit 0 }
git commit -m "Chuyen V1 sang Vercel PWA local-data stateless"
if ($LASTEXITCODE -ne 0) { Write-Host "Neu Git bao nothing to commit thi co the bo qua." -ForegroundColor Yellow }
git push origin main
Write-Host "XONG. Quay lai Vercel va bam Deploy." -ForegroundColor Green
