<#
    respaldo_datos.ps1 — Copia de seguridad de la carpeta "datos" de ControlOficios.

    Crea un archivo comprimido con la fecha en el nombre y borra los respaldos
    más antiguos que el número de días indicado.

    Uso manual (desde PowerShell, en la carpeta del ejecutable):
        .\respaldo_datos.ps1

    Con rutas propias:
        .\respaldo_datos.ps1 -Origen "C:\ControlOficios\datos" `
                             -Destino "D:\Respaldos\ControlOficios" `
                             -DiasConservar 60

    Para programarlo a diario, ver la sección 4.2 del README.

    IMPORTANTE: el respaldo incluye "clave_maestra.key". Quien tenga el archivo
    comprimido puede descifrar los datos, así que guárdelo en una ubicación con
    acceso restringido.
#>
param(
    # Por omisión, la carpeta "datos" que está junto a este script.
    [string]$Origen = (Join-Path $PSScriptRoot "datos"),
    # Por omisión, una carpeta "Respaldos" al lado de la aplicación.
    [string]$Destino = (Join-Path $PSScriptRoot "Respaldos"),
    # Respaldos más antiguos que estos días se eliminan.
    [int]$DiasConservar = 30
)

$ErrorActionPreference = "Stop"
$fecha = Get-Date -Format "yyyy-MM-dd_HHmm"
$registro = Join-Path $Destino "respaldos.log"

function Escribir-Registro([string]$texto) {
    $linea = "{0}  {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $texto
    Write-Host $linea
    try { Add-Content -Path $registro -Value $linea -Encoding UTF8 } catch { }
}

try {
    if (-not (Test-Path -LiteralPath $Origen)) {
        throw "No existe la carpeta de origen: $Origen"
    }
    New-Item -ItemType Directory -Force -Path $Destino | Out-Null

    # 1) Copia intermedia: evita comprimir archivos que la aplicación esté
    #    escribiendo en ese instante y excluye los temporales y los bloqueos.
    $temporal = Join-Path $env:TEMP "controloficios_respaldo_$fecha"
    New-Item -ItemType Directory -Force -Path $temporal | Out-Null

    robocopy $Origen $temporal /E /XF *.lock *.tmp /R:3 /W:2 /NFL /NDL /NJH /NJS | Out-Null
    # robocopy devuelve 0-7 en ejecuciones correctas; 8 o más indica error real.
    if ($LASTEXITCODE -ge 8) {
        throw "robocopy falló con código $LASTEXITCODE"
    }

    # 2) Comprimir la copia intermedia.
    $archivo = Join-Path $Destino "datos_$fecha.zip"
    Compress-Archive -Path (Join-Path $temporal "*") -DestinationPath $archivo `
                     -CompressionLevel Optimal -Force
    Remove-Item -LiteralPath $temporal -Recurse -Force

    $tamano = [math]::Round((Get-Item -LiteralPath $archivo).Length / 1MB, 2)
    Escribir-Registro "OK   respaldo creado: $archivo ($tamano MB)"

    # 3) Eliminar respaldos antiguos.
    $limite = (Get-Date).AddDays(-$DiasConservar)
    $viejos = Get-ChildItem -LiteralPath $Destino -Filter "datos_*.zip" |
              Where-Object { $_.LastWriteTime -lt $limite }
    foreach ($v in $viejos) {
        Remove-Item -LiteralPath $v.FullName -Force
        Escribir-Registro "     eliminado por antigüedad: $($v.Name)"
    }

    exit 0
}
catch {
    Escribir-Registro "ERROR  $($_.Exception.Message)"
    exit 1
}
