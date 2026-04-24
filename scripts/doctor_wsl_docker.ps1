param()

$ErrorActionPreference = "SilentlyContinue"

Write-Host "PersonaMimic Doctor: WSL + Docker" -ForegroundColor Cyan
Write-Host ""

$c = Get-PSDrive -Name C
if ($c) {
    $freeGb = [math]::Round(($c.Free / 1GB), 2)
    $usedGb = [math]::Round((($c.Used) / 1GB), 2)
    $totalGb = [math]::Round((($c.Used + $c.Free) / 1GB), 2)
    Write-Host ("C: {0} GB free / {1} GB total (used {2} GB)" -f $freeGb, $totalGb, $usedGb)
    if ($freeGb -lt 15) {
        Write-Host "WARNING: Low free space on C: is the #1 cause of WSL/Docker crashes (ENOSPC)." -ForegroundColor Yellow
    }
    Write-Host ""
}

$wslConfig = Join-Path $env:USERPROFILE ".wslconfig"
if (Test-Path $wslConfig) {
    Write-Host ".wslconfig:" -ForegroundColor Gray
    Get-Content $wslConfig | ForEach-Object { Write-Host ("  " + $_) }
    Write-Host ""
}

$dockerVhd = Join-Path $env:LOCALAPPDATA "Docker\\wsl\\disk\\docker_data.vhdx"
if (Test-Path $dockerVhd) {
    $vhdGb = [math]::Round(((Get-Item $dockerVhd).Length / 1GB), 2)
    Write-Host ("Docker data VHDX: {0} GB  ({1})" -f $vhdGb, $dockerVhd) -ForegroundColor Gray
    Write-Host ""
}

Write-Host "WSL distros:" -ForegroundColor Gray
wsl -l -v
Write-Host ""

Write-Host "Docker daemon check:" -ForegroundColor Gray
docker version
Write-Host ""

Write-Host "Next actions (quick):" -ForegroundColor Gray
Write-Host "1) Free 15-30 GB on C: (Docker needs headroom to start reliably)."
Write-Host "2) Start Docker Desktop, then run: docker system df"
Write-Host "3) If needed: docker system prune -af  (careful: deletes unused images/containers)"
Write-Host "4) If databases can be rebuilt: docker volume prune  (deletes Postgres/Redis/n8n data)"
