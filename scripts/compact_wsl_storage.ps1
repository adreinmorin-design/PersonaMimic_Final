param(
    [switch]$IncludeDocker = $true
)

$ErrorActionPreference = "Stop"

function Get-CompactTargets {
    $targets = @()

    $distroDisks = Get-ChildItem "$env:LOCALAPPDATA\Packages" -Directory -ErrorAction SilentlyContinue |
        ForEach-Object {
            Get-ChildItem $_.FullName -Filter ext4.vhdx -Recurse -ErrorAction SilentlyContinue
        }

    $targets += $distroDisks

    if ($IncludeDocker) {
        $dockerPaths = @(
            "$env:LOCALAPPDATA\Docker\wsl\disk\docker_data.vhdx",
            "$env:LOCALAPPDATA\Docker\wsl\main\ext4.vhdx"
        )
        foreach ($path in $dockerPaths) {
            if (Test-Path $path) {
                $targets += Get-Item $path
            }
        }
    }

    $targets | Sort-Object FullName -Unique
}

function Get-SizeGb([string]$Path) {
    if (-not (Test-Path $Path)) { return 0 }
    return [math]::Round((Get-Item $Path).Length / 1GB, 2)
}

Write-Host "Stopping WSL so VHD files can be compacted..." -ForegroundColor Cyan
wsl --shutdown

$targets = Get-CompactTargets
if (-not $targets) {
    Write-Host "No WSL VHD files found." -ForegroundColor Yellow
    exit 0
}

foreach ($target in $targets) {
    $path = $target.FullName
    $before = Get-SizeGb $path
    Write-Host ""
    Write-Host "Compacting $path" -ForegroundColor Green
    Write-Host "Before: ${before} GB" -ForegroundColor Gray

    $scriptPath = Join-Path $env:TEMP "compact-wsl-$([guid]::NewGuid().ToString('N')).txt"
    @"
select vdisk file="$path"
attach vdisk readonly
compact vdisk
detach vdisk
exit
"@ | Set-Content -Path $scriptPath -Encoding ASCII

    try {
        diskpart /s $scriptPath | Out-Host
    } finally {
        Remove-Item $scriptPath -Force -ErrorAction SilentlyContinue
    }

    $after = Get-SizeGb $path
    Write-Host "After:  ${after} GB" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Compaction complete. Start WSL again normally when you're ready." -ForegroundColor Cyan
