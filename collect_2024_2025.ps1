Write-Host "Starting data collection for the 2024-2025 season..."
Write-Host "Date/Time: $(Get-Date)"

# Create logs directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Run the python script and tee output to log file
python collect_single_season.py --season 2024-2025 | Tee-Object -FilePath "logs\season_2024_2025.log"

Write-Host "Data collection for 2024-2025 season completed."
Write-Host "Date/Time: $(Get-Date)"
Write-Host "Press any key to close this window..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null 