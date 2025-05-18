Write-Host "Starting data collection for the 2022-2023 season..."
Write-Host "Date/Time: $(Get-Date)"

# Create logs directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Run the python script and tee output to log file
python collect_single_season.py --season 2022-2023 | Tee-Object -FilePath "logs\season_2022_2023.log"

Write-Host "Data collection for 2022-2023 season completed."
Write-Host "Date/Time: $(Get-Date)"
Write-Host "Press any key to close this window..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null 