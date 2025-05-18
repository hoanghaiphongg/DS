Write-Host "Starting data collection for the 2021-2022 season..."
Write-Host "Date/Time: $(Get-Date)"

# Create logs directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Run the python script and tee output to log file
python collect_single_season.py --season 2021-2022 | Tee-Object -FilePath "logs\season_2021_2022.log"

Write-Host "Data collection for 2021-2022 season completed."
Write-Host "Date/Time: $(Get-Date)"
Write-Host "Press any key to close this window..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null 