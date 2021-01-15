$idetodo_path = $PSScriptRoot
Set-Location $idetodo_path

$venv_path = Join-Path -Path $idetodo_path -ChildPath ".env\Scripts\activate.ps1"
. $venv_path

python -m idetodo