# Premier League Player Data Collection

This folder contains scripts for collecting player data from the Premier League API for multiple seasons.

## Available Scripts

### Main Data Collection Scripts

- `collect_single_season.py` - Python script to collect data for a specific season
- `collect_players_multiple_seasons.py` - Original script to collect data for multiple seasons sequentially

### Season-Specific PowerShell Scripts

Individual scripts for each season:
- `collect_2020_2021.ps1` - PowerShell script for 2020-2021 season
- `collect_2021_2022.ps1` - PowerShell script for 2021-2022 season
- `collect_2022_2023.ps1` - PowerShell script for 2022-2023 season
- `collect_2023_2024.ps1` - PowerShell script for 2023-2024 season
- `collect_2024_2025.ps1` - PowerShell script for 2024-2025 season

### Batch Launchers

- `run_all_seasons.bat` - Batch file to run all seasons in parallel using direct Python commands
- `launch_all_collectors.bat` - Batch file to launch all PowerShell scripts in separate windows

## How to Use

### Option 1: Run All Seasons in Parallel (Recommended)

Simply run:
```
launch_all_collectors.bat
```

This will:
1. Start 5 separate PowerShell windows, one for each season
2. Collect data for all players in each season in parallel
3. Save the data to `data/players_data/[season]` folders
4. Create log files in the `logs` directory

### Option 2: Run a Specific Season

You can run a specific season using the PowerShell script:
```
powershell -File collect_2023_2024.ps1
```

Or directly using Python:
```
python collect_single_season.py --season 2023-2024
```

### Option 3: Limit Number of Players

To limit the number of players (for testing):
```
python collect_single_season.py --season 2023-2024 --max 10
```

## Data Storage

All collected data is stored in:
- `data/players_data/[season]/[player_id]_[player_name].json` - Individual player data files
- `data/players_data/players_summary_[season].json` - Season summary files

## Logs

Log files are stored in the `logs` directory:
- `logs/season_[year]_[year].log` 