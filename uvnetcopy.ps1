# Script used to make copies of today and yesterday UV log files
# This script should run repeatedly on all UV logging machines using
# the Windows Task Scheduler or similar, every 30 min or so

# Change directory to where the UV log files are stored by the instrument.
# Modify this as needed:
Set-Location -Path "C:\test\in"

# Create formatted date strings of today and yesterday
$today = (Get-Date).ToString("yyMMdd")
$yesterday = (Get-Date).AddDays(-1).ToString("yyMMdd")

# Search for files matching UV log files for the last two days
$files = Get-ChildItem | Where-Object { $_.Name -match '^GUV_[0-9]*_C_(' + $today + '|' + $yesterday + ').csv$' }

# Make a file copy of each file found, adding an 'A' at the beginning of the filename
foreach ($file in $files) {	
	Copy-Item -Force -Path $file.Name -Destination A$file
}
