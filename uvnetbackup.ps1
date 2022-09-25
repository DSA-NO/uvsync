
# Utfør følgende kommando som administrator for å tillate lokale script å kjøre
## set-executionpolicy remotesigned

# Katalog som skal sikkerhetskopieres
$pathFrom = "D:\UV\outbox"

# Katalog der sikkerhetskopi skal lagres
$pathTo = "D:\UV\backup"

# Iterer katalog som skal sikkerhetskopieres
Get-ChildItem -Path $pathFrom | Foreach-Object { 
	
	# Opprett navn på destinasjonskatalog
	$destDir = $pathTo + "\" + $_.Name + "\"
	
	# Opprett destinasjonskatalog hvis den ikke finnes allerede
	if(!(Test-Path $destDir)) { 
	
		New-Item $destDir -ItemType Directory -ErrorAction Stop
	}
	
	# Opprett liste over CSV filer som skal kopieres
	$files = Get-ChildItem -Path $_.FullName | Where-Object { $_.Name -match '.csv$' }	
	
	# Flytt CSV filer til destinasjon
	foreach ($file in $files) { 
	
		Move-Item $file.FullName -Destination $destDir -ErrorAction SilentlyContinue 
	}	
}