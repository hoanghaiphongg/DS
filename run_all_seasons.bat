@echo off
echo Starting data collection for 5 seasons in parallel...

:: Create log directory
mkdir logs 2>nul

:: Start each season in a separate window
start "Season 2020-2021" powershell -Command "python collect_single_season.py --season 2020-2021 | Tee-Object -FilePath logs\season_2020_2021.log"
timeout /t 2

start "Season 2021-2022" powershell -Command "python collect_single_season.py --season 2021-2022 | Tee-Object -FilePath logs\season_2021_2022.log"
timeout /t 2

start "Season 2022-2023" powershell -Command "python collect_single_season.py --season 2022-2023 | Tee-Object -FilePath logs\season_2022_2023.log"
timeout /t 2

start "Season 2023-2024" powershell -Command "python collect_single_season.py --season 2023-2024 | Tee-Object -FilePath logs\season_2023_2024.log"
timeout /t 2

start "Season 2024-2025" powershell -Command "python collect_single_season.py --season 2024-2025 | Tee-Object -FilePath logs\season_2024_2025.log"

echo All seasons started. Check the individual windows for progress.
echo Log files will be saved in the logs directory. 