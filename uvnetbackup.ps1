
# Utfør følgende kommando som administrator for å tillate lokale script å kjøre
## set-executionpolicy remotesigned

# Katalog som skal sikkerhetskopieres
$pathFrom = "D:\UV\outbox"

# Katalog der sikkerhetskopi skal lagres
$pathTo = "D:\UV\backup"

$files = @(Get-ChildItem -Path "$($pathFrom)" -File -Recurse)
$directories = @(Get-ChildItem -Path "$($pathFrom)" -Directory -Recurse)

ForEach($directory in $directories) {
	New-Item ($directory.FullName).Replace("$($pathFrom)", $pathTo) -ItemType Directory -ea SilentlyContinue | Out-Null
}

ForEach($file in $files) {	
	Move-Item -Path $file.FullName -Destination $file.FullName.Replace("$($pathFrom)", $pathTo) -Force -ErrorAction SilentlyContinue
}
