import requests
import json
import os
import time
import random
import sys
from datetime import datetime

# Cấu hình API
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

# Danh sách 5 mùa gần nhất
TARGET_SEASONS = ['2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021']

# Cấu hình delay để tránh bị block
MIN_DELAY = 1.5
MAX_DELAY = 3.5

# Cấu hình số lượng cầu thủ tối đa
MAX_PLAYERS_PER_SEASON = 1000  # Giá trị mặc định, có thể thay đổi bằng tham số dòng lệnh

# Thư mục lưu dữ liệu
DATA_DIR = 'data'
OUTPUT_DIR = os.path.join(DATA_DIR, 'players_data')

# Danh sách User-Agent
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
]

def setup_directories():
    """Tạo thư mục lưu dữ liệu nếu chưa tồn tại"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Tạo thư mục cho từng mùa giải
    for season in TARGET_SEASONS:
        os.makedirs(os.path.join(OUTPUT_DIR, season.replace('-', '_')), exist_ok=True)

def get_random_headers():
    """Lấy headers ngẫu nhiên"""
    headers = {
        'Accept': '*/*',
        'Origin': 'https://www.premierleague.com',
        'Referer': 'https://www.premierleague.com/',
        'User-Agent': random.choice(USER_AGENTS)
    }
    return headers

def random_sleep(min_time=None, max_time=None):
    """Nghỉ ngẫu nhiên để tránh bị block"""
    min_delay = min_time or MIN_DELAY
    max_delay = max_time or MAX_DELAY
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)
    return delay

def get_players_list(season_id, page_size=500):
    """Lấy danh sách cầu thủ của một mùa giải"""
    url = f"{API_BASE_URL}/players?pageSize={page_size}&compSeasons={season_id}"
    
    try:
        response = requests.get(url, headers=get_random_headers())
        response.raise_for_status()
        
        data = response.json()
        players = data.get("content", [])
        
        # Sắp xếp cầu thủ theo ID để đảm bảo tính ổn định
        sorted_players = sorted(players, key=lambda player: int(player.get("id", 0)))
        
        return sorted_players
    except Exception as e:
        print(f"Lỗi khi lấy danh sách cầu thủ: {str(e)}")
        return []

def get_player_general_info(player_id, season_id):
    """Lấy thông tin chung về cầu thủ"""
    url = f"{API_BASE_URL}/players/{player_id}?comps=1&compSeasons={season_id}"
    
    try:
        response = requests.get(url, headers=get_random_headers())
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        print(f"Lỗi khi lấy thông tin chung về cầu thủ {player_id}: {str(e)}")
        return None

def get_player_stats(player_id, season_id):
    """Lấy thống kê của cầu thủ trong một mùa giải"""
    url = f"{API_BASE_URL}/stats/player/{player_id}?comps=1&compSeasons={season_id}"
    
    try:
        response = requests.get(url, headers=get_random_headers())
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        print(f"Lỗi khi lấy thống kê cầu thủ {player_id}: {str(e)}")
        return None

def get_player_match_stats(player_id, season_id):
    """Lấy thống kê từng trận của cầu thủ"""
    url = f"{API_BASE_URL}/players/match-stats?playerId={player_id}&compSeason={season_id}"
    
    try:
        response = requests.get(url, headers=get_random_headers())
        if response.status_code == 204:  # No content
            return None
            
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        # Nhiều cầu thủ sẽ không có thống kê trận đấu, đây không phải lỗi nghiêm trọng
        if "404" in str(e):
            return None
        print(f"Lỗi khi lấy thống kê trận đấu cầu thủ {player_id}: {str(e)}")
        return None

def extract_player_data(general_data, stats_data, match_stats, season_name):
    """Trích xuất dữ liệu cầu thủ từ các API"""
    if not general_data:
        return None
    
    # Dict để lưu dữ liệu
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
    
    # Thêm thông tin đội bóng
    if "currentTeam" in general_data:
        result["team"] = {
            "id": general_data["currentTeam"].get("id"),
            "name": general_data["currentTeam"].get("name"),
            "short_name": general_data["currentTeam"].get("shortName"),
            "club_code": general_data["currentTeam"].get("club", {}).get("abbr") if "club" in general_data["currentTeam"] else None,
        }
    
    # Thêm thống kê cơ bản
    if stats_data:
        if "entity" in stats_data:
            result["basic_stats"] = {k: v for k, v in stats_data["entity"].items() 
                                   if k not in ["id", "name", "team"]}
        
        # Thêm thống kê chi tiết
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
    
    # Thêm thống kê từng trận đấu
    if match_stats and "fixtures" in match_stats:
        result["match_stats"] = match_stats["fixtures"]
    
    return result

def save_player_json(player_data, season):
    """Lưu dữ liệu cầu thủ vào file JSON"""
    if not player_data:
        return None
    
    player_id = player_data.get("player_id")
    player_name = player_data.get("name", "").replace(" ", "_").lower()
    
    if not player_id or not player_name:
        return None
    
    season_dir = os.path.join(OUTPUT_DIR, season.replace('-', '_'))
    filename = f"{player_id}_{player_name}.json"
    filepath = os.path.join(season_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(player_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def save_season_players_summary(players_data, season):
    """Lưu tóm tắt về tất cả cầu thủ trong một mùa giải"""
    if not players_data:
        return None
    
    # Tạo danh sách tóm tắt (không bao gồm thống kê chi tiết)
    summary_data = []
    for player in players_data:
        summary = {
            "player_id": player.get("player_id"),
            "name": player.get("name"),
            "team": player.get("team", {}).get("name") if "team" in player else None,
            "position": player.get("info", {}).get("positionInfo") if "info" in player else None,
            "nationality": player.get("nationality", {}).get("country") if "nationality" in player else None,
        }
        
        # Thêm các thống kê cơ bản
        if "basic_stats" in player:
            summary.update({
                "appearances": player["basic_stats"].get("appearances"),
                "mins_played": player["basic_stats"].get("minsPlayed"),
                "goals": player["basic_stats"].get("goals"),
                "assists": player["basic_stats"].get("assists"),
            })
        
        summary_data.append(summary)
    
    # Sắp xếp theo số bàn thắng giảm dần
    summary_data.sort(key=lambda x: (x.get("goals") or 0, x.get("assists") or 0), reverse=True)
    
    # Lưu tóm tắt vào file
    season_slug = season.replace('-', '_')
    filepath = os.path.join(OUTPUT_DIR, f"players_summary_{season_slug}.json")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def collect_season_players(season, max_players=None):
    """Thu thập dữ liệu cầu thủ cho một mùa giải"""
    print(f"\n===== THU THẬP DỮ LIỆU CẦU THỦ MÙA GIẢI {season} =====")
    
    season_id = SEASONS.get(season)
    if not season_id:
        print(f"Không tìm thấy ID cho mùa giải {season}")
        return []
    
    # Lấy danh sách cầu thủ
    print(f"Đang lấy danh sách cầu thủ mùa {season}...")
    players = get_players_list(season_id)
    total_players = len(players)
    print(f"Tìm thấy {total_players} cầu thủ trong mùa giải {season}")
    
    # Giới hạn số lượng cầu thủ nếu cần
    players_to_process = players
    if max_players and max_players < total_players:
        players_to_process = players[:max_players]
        print(f"Thu thập dữ liệu cho {max_players}/{total_players} cầu thủ theo giới hạn")
    
    # Thu thập dữ liệu cho từng cầu thủ
    all_players_data = []
    for i, player in enumerate(players_to_process, 1):
        player_id = player.get("id")
        player_name = player.get("name", {}).get("display", "Unknown")
        
        print(f"[{i}/{len(players_to_process)}] Đang thu thập dữ liệu cho {player_name} (ID: {player_id})...")
        
        # Thu thập các loại dữ liệu
        general_info = get_player_general_info(player_id, season_id)
        random_sleep()
        
        stats_data = get_player_stats(player_id, season_id)
        random_sleep()
        
        match_stats = get_player_match_stats(player_id, season_id)
        random_sleep()
        
        # Trích xuất dữ liệu
        player_data = extract_player_data(general_info, stats_data, match_stats, season)
        if player_data:
            # Lưu vào file JSON
            json_path = save_player_json(player_data, season)
            
            if json_path:
                # Hiển thị thông tin ngắn gọn
                team = player_data.get("team", {}).get("name", "N/A") if "team" in player_data else "N/A"
                pos = player_data.get("info", {}).get("positionInfo", "N/A") if "info" in player_data else "N/A"
                goals = player_data.get("basic_stats", {}).get("goals", "0") if "basic_stats" in player_data else "0"
                
                print(f"  - Đã lưu {player_name} - {pos} ({team}) - Bàn thắng: {goals}")
                all_players_data.append(player_data)
            else:
                print(f"  - Không thể lưu dữ liệu cho {player_name}")
        else:
            print(f"  - Không có dữ liệu cho {player_name}")
    
    # Lưu tóm tắt cho mùa giải
    if all_players_data:
        summary_path = save_season_players_summary(all_players_data, season)
        print(f"Đã lưu tóm tắt dữ liệu {len(all_players_data)} cầu thủ mùa {season} vào {summary_path}")
    
    return all_players_data

def collect_all_seasons(seasons_list=None, max_players=None):
    """Thu thập dữ liệu cầu thủ cho nhiều mùa giải"""
    if not seasons_list:
        seasons_list = TARGET_SEASONS
    
    setup_directories()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"===== BẮT ĐẦU THU THẬP DỮ LIỆU CẦU THỦ - {timestamp} =====")
    print(f"Số mùa giải: {len(seasons_list)}")
    if max_players:
        print(f"Giới hạn số cầu thủ mỗi mùa: {max_players}")
    
    results = {}
    for season in seasons_list:
        players_data = collect_season_players(season, max_players)
        results[season] = len(players_data)
    
    # Tạo báo cáo tổng hợp
    end_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"\n===== KẾT THÚC THU THẬP DỮ LIỆU CẦU THỦ - {end_timestamp} =====")
    print(f"Thư mục lưu dữ liệu: {OUTPUT_DIR}")
    
    for season, count in results.items():
        print(f"- Mùa {season}: {count} cầu thủ")
    
    return results

if __name__ == "__main__":
    # Xử lý tham số dòng lệnh
    import argparse
    parser = argparse.ArgumentParser(description='Thu thập dữ liệu cầu thủ cho nhiều mùa giải')
    parser.add_argument('--max', type=int, default=None, 
                        help='Số lượng cầu thủ tối đa cho mỗi mùa giải (mặc định: tất cả)')
    parser.add_argument('--seasons', type=str, nargs='+',
                        help='Danh sách mùa giải cần thu thập (mặc định: 5 mùa gần nhất)')
    
    args = parser.parse_args()
    
    max_players = args.max
    seasons = args.seasons if args.seasons else TARGET_SEASONS
    
    collect_all_seasons(seasons, max_players) 