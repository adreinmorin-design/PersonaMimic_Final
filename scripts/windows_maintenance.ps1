param(
    [string]$StrayPath = "C:\Users\Albert Morin\Desktop\PersonaMimic_Final"
)

$ErrorActionPreference = "Continue"

function Write-Step($msg) {
    Write-Host "[*] $msg" -ForegroundColor Cyan
}

function Write-Ok($msg) {
    Write-Host "[+] $msg" -ForegroundColor Green
}

function Write-Warn($msg) {
    Write-Host "[!] $msg" -ForegroundColor Yellow
}

function Get-FreeGb($path) {
    $drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($path).TrimEnd('\').TrimEnd(':')) -ErrorAction SilentlyContinue
    if (-not $drive) { return $null }
    return [math]::Round($drive.Free / 1GB, 2)
}

function Remove-OldTempFiles($path, $days) {
    if (-not (Test-Path $path)) { return 0 }
    $cutoff = (Get-Date).AddDays(-1 * $days)
    $removed = 0
    Get-ChildItem -Path $path -Recurse -Force -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        ForEach-Object {
            try {
                if ($_.PSIsContainer) {
                    if ($_.LastWriteTime -lt $cutoff) {
                        Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
                    }
                } else {
                    if ($_.LastWriteTime -lt $cutoff) {
                        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
                        if (-not (Test-Path $_.FullName)) { $removed++ }
                    }
                }
            } catch {
            }
        }
    return $removed
}

function Compact-VhdWithDiskpart($path) {
    if (-not (Test-Path $path)) {
        Write-Warn "VHD not found: $path"
        return
    }

    $before = [math]::Round((Get-Item $path).Length / 1GB, 2)
    $temp = Join-Path $env:TEMP ("diskpart-" + [guid]::NewGuid().ToString("N") + ".txt")
@"
select vdisk file="$path"
attach vdisk readonly
compact vdisk
detach vdisk
exit
"@ | Set-Content -Path $temp -Encoding ASCII

    Write-Step "Compacting $path (before ${before} GB)"
    try {
        diskpart /s $temp | Out-Host
    } finally {
        Remove-Item $temp -Force -ErrorAction SilentlyContinue
    }

    $after = [math]::Round((Get-Item $path).Length / 1GB, 2)
    Write-Ok "Compaction finished for $path (after ${after} GB)"
}

function Remove-StrayIfVerified($path) {
    if (-not (Test-Path $path)) {
        Write-Warn "Stray path already absent: $path"
        return
    }

    $files = Get-ChildItem -Path $path -Recurse -File -Force -ErrorAction SilentlyContinue |
        ForEach-Object { $_.FullName.Substring($path.Length).TrimStart('\') -replace '\\','/' } |
        Sort-Object

    $expected = @(
        ".vscode/settings.json",
        "=0.0.9,",
        "=0.1.7,",
        "=0.110.0,",
        "=0.27.0,",
        "=1.0.1,",
        "=1.8.0,",
        "=2.5.1,",
        "=2.6.3,",
        "=23.2.1,",
        "=42.0.5,",
        "CleanAndCompact.ps1",
        "pyproject.toml.tmp"
    )

    $unexpected = Compare-Object -ReferenceObject $expected -DifferenceObject $files |
        Where-Object { $_.SideIndicator -eq "=>" } |
        Select-Object -ExpandProperty InputObject

    if ($unexpected) {
        Write-Warn "Stray folder contains unexpected files; skipping delete."
        $unexpected | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
        return
    }

    Write-Step "Removing verified stray folder: $path"
    Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
    if (-not (Test-Path $path)) {
        Write-Ok "Removed stray folder."
    } else {
        Write-Warn "Attempted stray folder removal, but it still exists."
    }
}

$beforeFree = Get-FreeGb "C:\"
Write-Host "C: free before cleanup: ${beforeFree} GB" -ForegroundColor Gray

Write-Step "Cleaning old temp files"
$removedUserTemp = Remove-OldTempFiles $env:TEMP 7
Write-Ok "Removed $removedUserTemp old temp files from $env:TEMP"

Write-Step "Stopping Docker Desktop processes if present"
Get-Process -Name "Docker Desktop","com.docker.backend","com.docker.proxy" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

$dockerCli = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerCli) {
    Write-Step "Running Docker prune"
    docker system prune -af | Out-Host
    docker builder prune -af | Out-Host
} else {
    Write-Warn "docker.exe not found in PATH; skipping prune."
}

$dockerVhds = @(
    "$env:LOCALAPPDATA\Docker\wsl\disk\docker_data.vhdx",
    "$env:LOCALAPPDATA\Docker\wsl\main\ext4.vhdx"
)

foreach ($vhd in $dockerVhds) {
    Compact-VhdWithDiskpart $vhd
}

Remove-StrayIfVerified $StrayPath

$afterFree = Get-FreeGb "C:\"
Write-Host "C: free after cleanup:  ${afterFree} GB" -ForegroundColor Gray
