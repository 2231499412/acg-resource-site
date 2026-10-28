param(
  [ValidateSet('h2', 'mysql')]
  [string]$Database = 'h2'
)

$ErrorActionPreference = "Stop"
$java = "C:\Program Files\Java\jdk-21\bin\java.exe"
$jar = Join-Path $PSScriptRoot "halo-2.27.1.jar"
$configDir = (($PSScriptRoot -replace '\\', '/') + '/')

if (-not (Test-Path -LiteralPath $java)) { throw "Java 21 not found: $java" }
if (-not (Test-Path -LiteralPath $jar)) { throw "Halo JAR not found: $jar" }

$javaArgs = @(
  '-Dfile.encoding=UTF-8',
  '-server',
  '-Xms256m',
  '-Xmx512m',
  '-jar',
  $jar,
  "--spring.config.additional-location=optional:file:$configDir"
)
if ($Database -eq 'mysql') {
  if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'application-mysql.yaml'))) {
    throw 'Copy application-mysql.yaml.example to application-mysql.yaml first.'
  }
  if ([string]::IsNullOrWhiteSpace($env:HALO_DB_PASSWORD)) {
    throw 'Set HALO_DB_PASSWORD for the independent Halo MySQL account first.'
  }
  $javaArgs += '--spring.profiles.active=mysql'
}
& $java @javaArgs
