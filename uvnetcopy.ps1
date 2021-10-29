
Set-Location -Path "C:\test\in"

$today = (Get-Date).ToString("yyMMdd")
$yesterday = (Get-Date).AddDays(-1).ToString("yyMMdd")

$files = Get-ChildItem | Where-Object { $_.Name -match '^GUV_[0-9]*_C_(' + $today + '|' + $yesterday + ').csv$' }

foreach ($file in $files) {	
	Copy-Item -Force -Path $file.Name -Destination A$file
}
