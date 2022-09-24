
# set-executionpolicy remotesigned

$pathFrom = "D:\UV\outbox"
$pathTo = "D:\UV\backup"

Get-ChildItem -Path $pathFrom | Foreach-Object { 
	
	$destDir = $pathTo + "\" + $_.Name + "\"
	
	if(!(Test-Path $destDir)) { 
		New-Item $destDir -ItemType Directory -ErrorAction Stop
	}
	
	$files = Get-ChildItem -Path $_.FullName | Where-Object { $_.Name -match '.csv$' }	
	
	foreach ($file in $files) { 
		Move-Item $file.FullName -Destination $destDir -ErrorAction SilentlyContinue 
	}	
}