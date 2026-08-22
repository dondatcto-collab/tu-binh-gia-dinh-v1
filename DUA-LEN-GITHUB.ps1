$ErrorActionPreference = 'Stop'
Write-Host '=== TỬ BÌNH GIA ĐÌNH V1 - ĐƯA LÊN GITHUB ===' -ForegroundColor Cyan
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host 'Chưa có Git. Cài Git for Windows rồi chạy lại file này.' -ForegroundColor Red
  exit 1
}
$repo = Read-Host 'Dán URL repo GitHub PRIVATE, ví dụ https://github.com/ten/tu-binh-gia-dinh-v1.git'
if ([string]::IsNullOrWhiteSpace($repo)) { throw 'Chưa nhập URL repo.' }
Set-Location $PSScriptRoot
if (-not (Test-Path '.git')) { git init }
git add .
$hasCommit = git rev-parse --verify HEAD 2>$null
if ($LASTEXITCODE -ne 0) {
  git commit -m 'PWA V1 gia dinh'
} else {
  $changes = git status --porcelain
  if ($changes) { git commit -m 'Cap nhat PWA V1' }
}
git branch -M main
$origin = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) { git remote set-url origin $repo } else { git remote add origin $repo }
Write-Host 'Đang đẩy lên GitHub. Nếu trình duyệt hỏi đăng nhập, hãy đăng nhập tài khoản GitHub của bạn.' -ForegroundColor Yellow
git push -u origin main
Write-Host 'XONG. Tiếp theo mở HUONG-DAN-GITHUB-PWA.md và triển khai Render.' -ForegroundColor Green
