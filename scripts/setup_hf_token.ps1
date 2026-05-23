param(
    [switch]$Upload,
    [switch]$CleanedOnly
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Write-Host ""
Write-Host "Configurar HF_TOKEN persistente"
Write-Host "Cole o token do Hugging Face quando solicitado. Ele nao sera exibido."
Write-Host ""

$secureToken = Read-Host "HF_TOKEN" -AsSecureString
$bstr = [IntPtr]::Zero

try {
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)

    if ([string]::IsNullOrWhiteSpace($token)) {
        throw "Token vazio."
    }

    if (-not $token.StartsWith("hf_")) {
        throw "O token nao parece um token Hugging Face valido; ele deveria comecar com hf_."
    }

    [Environment]::SetEnvironmentVariable("HF_TOKEN", $token, "User")
    $env:HF_TOKEN = $token

    Write-Host ""
    Write-Host "HF_TOKEN salvo no ambiente persistente do usuario Windows."
    Write-Host "Novos terminais e novas sessoes do Codex devem conseguir usar o token."

    if ($Upload -or $CleanedOnly) {
        $python = Join-Path $repoRoot ".venv\Scripts\python.exe"
        if (-not (Test-Path $python)) {
            $python = "python"
        }

        if ($CleanedOnly) {
            Write-Host ""
            Write-Host "Rodando upload apenas dos parquets cleaned..."
            & $python "pipelines\upload_cleaned_only.py"
        } else {
            Write-Host ""
            Write-Host "Rodando upload completo raw + cleaned..."
            & $python "pipelines\upload_hf.py"
        }

        exit $LASTEXITCODE
    }
}
finally {
    if ($bstr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}
