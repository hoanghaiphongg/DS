import requests
import json
import os
import time
import random
import sys
from datetime import datetime

# API Configuration
API_BASE_URL = 'https://footballapi.pulselive.com/football'
SEASONS = {
    '2024-2025': '719',
    '2023-2024': '578',
    '2022-2023': '489',
    '2021-2022': '418',
    '2020-2021': '363',
    '2019-2020': '274',
    '2018-2019': '210',
    '2017-2018': '79',
}

# Delay configuration to avoid being blocked
MIN_DELAY = 1.5
MAX_DELAY = 3.5

# Data directories
DATA_DIR = 'data'
OUTPUT_DIR = os.path.join(DATA_DIR, 'players_data')

# User-Agent list
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
]

def setup_directories(season):
    """Create data directories if they don't exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create directory for the season
    season_dir = os.path.join(OUTPUT_DIR, season.replace('-', '_'))
    os.makedirs(season_dir, exist_ok=True)
    
    return season_dir

def get_random_headers():
    """Get random headers"""
    headers = {
        'Accept': '*/*',
        'Origin': 'https://www.premierleague.com',
        'Referer': 'https://www.premierleague.com/',
        'User-Agent': random.choice(USER_AGENTS)
    }
    return headers

def random_sleep(min_time=None, max_time=None):
    """Random sleep to avoid being blocked"""
    min_delay = min_time or MIN_DELAY
    max_delay = max_time or MAX_DELAY
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)
    return delay

def get_players_list(season_id, page_size=500):
    """Get players list for a season"""
    url = f"{API_BASE_URL}/players?pageSize={page_size}&compSeasons={season_id}"
    
    try:
        response = requests.get(url, headers=get_random_headers())
        response.raise_for_status()
        
        data = response.json()
        players = data.get("content", [])
        
        # Sort players by ID for stability
        sorted_players = sorted(players, key=lambda player: int(player.get("id", 0)))
        
        return sorted_players
    except Exception as e:
        print(f"Error getting players list: {str(e)}")
        return []

def get_player_general_info(player_id, season_id):
    """Get general player information"""
    url = f"{API_BASE_URL}/players/{player_id}?comps=1&compSeasons={season_id}"
    
    try:
        response = requests.get(url, headers=get_random_headers())
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        print(f"Error getting general info for player {player_id}: {str(e)}")
        return None

def get_player_stats(player_id, season_id):
    """Get player statistics for a season"""
    url = f"{API_BASE_URL}/stats/player/{player_id}?comps=1&compSeasons={season_id}"
    
    try:
        response = requests.get(url, headers=get_random_headers())
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        print(f"Error getting statistics for player {player_id}: {str(e)}")
        return None

def get_player_match_stats(player_id, season_id):
    """Get player match statistics"""
    url = f"{API_BASE_URL}/players/match-stats?playerId={player_id}&compSeason={season_id}"
    
    try:
        response = requests.get(url, headers=get_random_headers())
        if response.status_code == 204:  # No content
            return None
            
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        # Many players won't have match statistics, this is not a serious error
        if "404" in str(e):
            return None
        print(f"Error getting match statistics for player {player_id}: {str(e)}")
        return None

def extract_player_data(general_data, stats_data, match_stats, season_name):
    """Extract player data from APIs"""
    if not general_data:
        return None
    
    # Dict to store data
    result = {
        "player_id": general_data.get("id"),
        "season": season_name,
        "name": general_data.get("name", {}).get("display"),
        "first_name": general_data.get("name", {}).get("first"),
        "last_name": general_data.get("name", {}).get("last"),
        "info": general_data.get("info"),
        "nationality": general_data.get("nationalTeam"),
        "birth": general_data.get("birth"),
        "age": general_data.get("age"),
    }
    
    # Add team information
    if "currentTeam" in general_data:
        result["team"] = {
            "id": general_data["currentTeam"].get("id"),
            "name": general_data["currentTeam"].get("name"),
            "short_name": general_data["currentTeam"].get("shortName"),
            "club_code": general_data["currentTeam"].get("club", {}).get("abbr") if "club" in general_data["currentTeam"] else None,
        }
    
    # Add basic statistics
    if stats_data:
        if "entity" in stats_data:
            result["basic_stats"] = {k: v for k, v in stats_data["entity"].items() 
                                   if k not in ["id", "name", "team"]}
        
        # Add detailed statistics
        if "stats" in stats_data:
            result["detailed_stats"] = []
            for stat in stats_data["stats"]:
                stat_obj = {
                    "name": stat.get("name"),
                    "value": stat.get("value")
                }
                if "rank" in stat:
                    stat_obj["rank"] = stat.get("rank")
                result["detailed_stats"].append(stat_obj)
    
    # Add match statistics
    if match_stats and "fixtures" in match_stats:
        result["match_stats"] = match_stats["fixtures"]
    
    return result

def save_player_json(player_data, season_dir, season):
    """Save player data to JSON file"""
    if not player_data:
        return None
    
    player_id = player_data.get("player_id")
    player_name = player_data.get("name", "").replace(" ", "_").lower()
    
    if not player_id or not player_name:
        return None
    
    filename = f"{player_id}_{player_name}.json"
    filepath = os.path.join(season_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(player_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def save_season_players_summary(players_data, season):
    """Save a summary of all players in a season"""
    if not players_data:
        return None
    
    # Create summary list (not including detailed stats)
    summary_data = []
    for player in players_data:
        summary = {
            "player_id": player.get("player_id"),
            "name": player.get("name"),
            "team": player.get("team", {}).get("name") if "team" in player else None,
            "position": player.get("info", {}).get("positionInfo") if "info" in player else None,
            "nationality": player.get("nationality", {}).get("country") if "nationality" in player else None,
        }
        
        # Add basic statistics
        if "basic_stats" in player:
            summary.update({
                "appearances": player["basic_stats"].get("appearances"),
                "mins_played": player["basic_stats"].get("minsPlayed"),
                "goals": player["basic_stats"].get("goals"),
                "assists": player["basic_stats"].get("assists"),
            })
        
        summary_data.append(summary)
    
    # Sort by goals scored in descending order
    summary_data.sort(key=lambda x: (x.get("goals") or 0, x.get("assists") or 0), reverse=True)
    
    # Save summary to file
    season_slug = season.replace('-', '_')
    filepath = os.path.join(OUTPUT_DIR, f"players_summary_{season_slug}.json")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def collect_season_players(season, max_players=None):
    """Collect player data for a season"""
    print(f"\n===== COLLECTING PLAYER DATA FOR SEASON {season} =====")
    
    season_id = SEASONS.get(season)
    if not season_id:
        print(f"Season ID not found for {season}")
        return []
    
    # Create directory for this season
    season_dir = setup_directories(season)
    
    # Get players list
    print(f"Getting players list for season {season}...")
    players = get_players_list(season_id)
    total_players = len(players)
    print(f"Found {total_players} players in season {season}")
    
    # Limit number of players if needed
    players_to_process = players
    if max_players and max_players < total_players:
        players_to_process = players[:max_players]
        print(f"Collecting data for {max_players}/{total_players} players as limited")
    
    # Collect data for each player
    all_players_data = []
    for i, player in enumerate(players_to_process, 1):
        player_id = player.get("id")
        player_name = player.get("name", {}).get("display", "Unknown")
        
        print(f"[{i}/{len(players_to_process)}] Collecting data for {player_name} (ID: {player_id})...")
        
        # Collect different types of data
        general_info = get_player_general_info(player_id, season_id)
        random_sleep()
        
        stats_data = get_player_stats(player_id, season_id)
        random_sleep()
        
        match_stats = get_player_match_stats(player_id, season_id)
        random_sleep()
        
        # Extract data
        player_data = extract_player_data(general_info, stats_data, match_stats, season)
        if player_data:
            # Save to JSON file
            json_path = save_player_json(player_data, season_dir, season)
            
            if json_path:
                # Display brief information
                team = player_data.get("team", {}).get("name", "N/A") if "team" in player_data else "N/A"
                pos = player_data.get("info", {}).get("positionInfo", "N/A") if "info" in player_data else "N/A"
                goals = player_data.get("basic_stats", {}).get("goals", "0") if "basic_stats" in player_data else "0"
                
                print(f"  - Saved {player_name} - {pos} ({team}) - Goals: {goals}")
                all_players_data.append(player_data)
            else:
                print(f"  - Could not save data for {player_name}")
        else:
            print(f"  - No data for {player_name}")
    
    # Save season summary
    if all_players_data:
        summary_path = save_season_players_summary(all_players_data, season)
        print(f"Saved summary data for {len(all_players_data)} players in season {season} to {summary_path}")
    
    return all_players_data

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Collect player data for a specific season')
    parser.add_argument('--season', type=str, required=True, 
                        help='Season to collect (e.g., 2024-2025)')
    parser.add_argument('--max', type=int, default=None, 
                        help='Maximum number of players to collect (default: all)')
    
    args = parser.parse_args()
    
    season = args.season
    max_players = args.max
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"===== STARTING PLAYER DATA COLLECTION FOR {season} - {timestamp} =====")
    
    collect_season_players(season, max_players)
    
    end_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"\n===== COMPLETED PLAYER DATA COLLECTION FOR {season} - {end_timestamp} =====") 