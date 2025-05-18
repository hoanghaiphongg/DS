@echo off
echo Starting data collection for all 5 seasons in parallel...

:: Start PowerShell scripts in separate windows
start "Season 2020-2021" powershell -NoExit -File ".\collect_2020_2021.ps1"
timeout /t 2

start "Season 2021-2022" powershell -NoExit -File ".\collect_2021_2022.ps1"
timeout /t 2

start "Season 2022-2023" powershell -NoExit -File ".\collect_2022_2023.ps1"
timeout /t 2

start "Season 2023-2024" powershell -NoExit -File ".\collect_2023_2024.ps1"
timeout /t 2

start "Season 2024-2025" powershell -NoExit -File ".\collect_2024_2025.ps1"

echo All data collection processes have been started.
echo Each process runs in its own window and logs output to the logs directory.
echo Press any key to close this launcher window...
pause > nul 