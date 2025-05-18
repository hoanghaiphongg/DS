import requests
import json
import os
import pandas as pd
import sys
import time
import random
from datetime import datetime

# Cấu hình API
API_BASE_URL = 'https://footballapi.pulselive.com/football'
SEASONS = {
    '2023-2024': '578',
    '2022-2023': '489',
    '2021-2022': '418',
    '2020-2021': '363',
    '2019-2020': '274',
    '2018-2019': '210',
    '2017-2018': '79',
}

# Cấu hình delay để tránh bị block
MIN_DELAY = 1.0
MAX_DELAY = 3.0

# Danh sách User-Agent
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
]

def get_random_headers():
    """Lấy headers ngẫu nhiên"""
    headers = {
        'Accept': '*/*',
        'Origin': 'https://www.premierleague.com',
        'Referer': 'https://www.premierleague.com/',
        'User-Agent': random.choice(USER_AGENTS)
    }
    return headers

def search_player_by_name(player_name, season_id):
    """Tìm kiếm cầu thủ theo tên và mùa giải"""
    url = f"{API_BASE_URL}/players?pageSize=500&compSeasons={season_id}"
    
    print(f"Đang tìm kiếm cầu thủ '{player_name}' trong mùa giải {season_id}...")
    
    try:
        response = requests.get(url, headers=get_random_headers())
        response.raise_for_status()
        
        data = response.json()
        players = data.get("content", [])
        
        print(f"Tìm thấy {len(players)} cầu thủ trong mùa giải.")
        
        # Tìm cầu thủ theo tên (tìm không phân biệt chữ hoa/thường)
        matched_players = []
        for player in players:
            player_display_name = player.get("name", {}).get("display", "").lower()
            if player_name.lower() in player_display_name:
                matched_players.append(player)
        
        if matched_players:
            print(f"Tìm thấy {len(matched_players)} cầu thủ có tên khớp với '{player_name}':")
            
            for i, player in enumerate(matched_players, 1):
                display_name = player.get("name", {}).get("display", "Unknown")
                position = player.get("info", {}).get("positionInfo", "Unknown")
                team = player.get("currentTeam", {}).get("name", "Unknown") if "currentTeam" in player else "Unknown"
                player_id = player.get("id", "Unknown")
                
                print(f"{i}. {display_name} - {position} ({team}) - ID: {player_id}")
            
            return matched_players
        else:
            print(f"Không tìm thấy cầu thủ nào có tên '{player_name}'")
            return []
            
    except Exception as e:
        print(f"Lỗi khi tìm kiếm cầu thủ: {str(e)}")
        return []

def get_player_general_info(player_id, season_id):
    """Lấy thông tin chung về cầu thủ"""
    url = f"{API_BASE_URL}/players/{player_id}?comps=1&compSeasons={season_id}"
    
    try:
        print(f"Đang lấy thông tin chung về cầu thủ ID {player_id}...")
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        
        response = requests.get(url, headers=get_random_headers())
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        print(f"Lỗi khi lấy thông tin chung về cầu thủ: {str(e)}")
        return None

def get_player_stats(player_id, season_id):
    """Lấy thống kê của cầu thủ trong một mùa giải"""
    url = f"{API_BASE_URL}/stats/player/{player_id}?comps=1&compSeasons={season_id}"
    
    try:
        print(f"Đang lấy thống kê của cầu thủ ID {player_id}...")
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        
        response = requests.get(url, headers=get_random_headers())
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        print(f"Lỗi khi lấy thống kê cầu thủ: {str(e)}")
        return None

def get_player_match_stats(player_id, season_id):
    """Lấy thống kê từng trận của cầu thủ"""
    url = f"{API_BASE_URL}/players/match-stats?playerId={player_id}&compSeason={season_id}"
    
    try:
        print(f"Đang lấy thống kê trận đấu của cầu thủ ID {player_id}...")
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        
        response = requests.get(url, headers=get_random_headers())
        if response.status_code == 204:  # No content
            print(f"Không có dữ liệu thống kê trận đấu cho cầu thủ {player_id}")
            return None
            
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        print(f"Lỗi khi lấy thống kê trận đấu cầu thủ: {str(e)}")
        return None

def extract_all_player_data(general_data, stats_data, match_stats, season_name):
    """Trích xuất tất cả dữ liệu của cầu thủ từ các API"""
    if not general_data:
        print("Không có thông tin chung về cầu thủ!")
        return None
    
    # Dict để lưu tất cả thông tin
    result = {}
    
    # 1. Thông tin cơ bản
    print("\nĐang trích xuất thông tin cơ bản của cầu thủ...")
    result.update({
        "player_id": general_data.get("id"),
        "season": season_name,
        "name": general_data.get("name", {}).get("display"),
        "first_name": general_data.get("name", {}).get("first"),
        "last_name": general_data.get("name", {}).get("last"),
        "position": general_data.get("info", {}).get("positionInfo"),
        "shirt_num": general_data.get("info", {}).get("shirtNum"),
        "nationality": general_data.get("nationalTeam", {}).get("country") if general_data.get("nationalTeam") else None,
        "country_code": general_data.get("nationalTeam", {}).get("isoCode") if general_data.get("nationalTeam") else None,
        "height_cm": general_data.get("info", {}).get("height"),
        "weight_kg": general_data.get("info", {}).get("weight"),
        "date_of_birth": general_data.get("birth", {}).get("date", {}).get("label") if general_data.get("birth", {}).get("date") else None,
        "dob_millis": general_data.get("birth", {}).get("date", {}).get("millis") if general_data.get("birth", {}).get("date") else None,
        "age": general_data.get("age"),
    })
    
    # Thêm thông tin đội bóng
    if "currentTeam" in general_data:
        result.update({
            "team": general_data["currentTeam"].get("name"),
            "team_id": general_data["currentTeam"].get("id"),
            "team_short": general_data["currentTeam"].get("shortName"),
            "team_club_code": general_data["currentTeam"].get("club", {}).get("abbr") if "club" in general_data["currentTeam"] else None,
        })
    
    # 2. Thống kê cơ bản từ stats_data
    if stats_data:
        print("Đang trích xuất thống kê cơ bản...")
        if "entity" in stats_data:
            entity = stats_data["entity"]
            for key, value in entity.items():
                if key not in ["id", "name", "team"]:  # Bỏ qua các trường không phải thống kê
                    result[f"stat_{key}"] = value
    
    # 3. Thống kê chi tiết từ stats_data
    if stats_data and "stats" in stats_data:
        print("Đang trích xuất thống kê chi tiết...")
        for stat in stats_data["stats"]:
            name = stat.get("name")
            if name:
                result[f"stat_{name}"] = stat.get("value")
                # Lưu thêm thông tin về xếp hạng (nếu có)
                if "rank" in stat:
                    result[f"rank_{name}"] = stat.get("rank")
    
    # 4. Thống kê từng trận đấu
    if match_stats and "fixtures" in match_stats:
        print("Đang trích xuất thống kê từng trận đấu...")
        matches = match_stats["fixtures"]
        
        # Tạo một list để lưu thông tin về từng trận đấu
        match_list = []
        
        for match in matches:
            match_info = {
                "match_id": match.get("fixtureId"),
                "match_date": match.get("kickoff", {}).get("label") if "kickoff" in match else None,
                "home_team": match.get("teams", [])[0].get("team", {}).get("name") if match.get("teams") and len(match.get("teams")) > 0 else None,
                "away_team": match.get("teams", [])[1].get("team", {}).get("name") if match.get("teams") and len(match.get("teams")) > 1 else None,
                "home_score": match.get("teams", [])[0].get("score") if match.get("teams") and len(match.get("teams")) > 0 else None,
                "away_score": match.get("teams", [])[1].get("score") if match.get("teams") and len(match.get("teams")) > 1 else None,
                "player_team": "home" if match.get("teams") and len(match.get("teams")) > 0 and match.get("teams")[0].get("team", {}).get("id") == result.get("team_id") else "away",
                "minutes_played": match.get("minutesPlayed"),
                "position": match.get("position"),
                "captain": match.get("captain", False),
                "substitute": match.get("substitute", False),
            }
            
            # Thêm tất cả các thống kê của trận đấu
            if "stats" in match:
                for stat in match["stats"]:
                    stat_name = stat.get("name")
                    if stat_name:
                        match_info[f"match_stat_{stat_name}"] = stat.get("value")
            
            match_list.append(match_info)
        
        # Tính tổng số trận và số trận làm đội trưởng
        result["total_matches"] = len(match_list)
        result["matches_as_captain"] = sum(1 for m in match_list if m.get("captain", False))
        result["matches_as_substitute"] = sum(1 for m in match_list if m.get("substitute", False))
        
        # Lưu thống kê của từng trận dưới dạng list
        result["match_stats"] = match_list
    
    return result

def save_player_data(player_data, player_name, season):
    """Lưu dữ liệu cầu thủ vào file JSON và CSV"""
    if not player_data:
        print("Không có dữ liệu cầu thủ để lưu!")
        return None, None
    
    # Tạo thư mục data nếu chưa tồn tại
    os.makedirs("data", exist_ok=True)
    
    # Tạo tên file với timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    player_slug = player_name.lower().replace(" ", "_")
    season_slug = season.replace("-", "_")
    
    # 1. Lưu toàn bộ dữ liệu vào JSON
    json_path = os.path.join("data", f"player_{player_slug}_{season_slug}_{timestamp}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(player_data, f, ensure_ascii=False, indent=2)
    
    print(f"Đã lưu dữ liệu đầy đủ vào JSON: {json_path}")
    
    # 2. Lưu dữ liệu cơ bản vào CSV (không bao gồm thống kê từng trận)
    csv_data = player_data.copy()
    if "match_stats" in csv_data:
        del csv_data["match_stats"]  # Loại bỏ thống kê từng trận vì nó là một list
    
    csv_path = os.path.join("data", f"player_{player_slug}_{season_slug}_{timestamp}.csv")
    pd.DataFrame([csv_data]).to_csv(csv_path, index=False)
    
    print(f"Đã lưu dữ liệu cơ bản vào CSV: {csv_path}")
    
    # 3. Lưu thống kê từng trận riêng (nếu có)
    if "match_stats" in player_data and player_data["match_stats"]:
        match_csv_path = os.path.join("data", f"player_{player_slug}_matches_{season_slug}_{timestamp}.csv")
        pd.DataFrame(player_data["match_stats"]).to_csv(match_csv_path, index=False)
        
        print(f"Đã lưu thống kê từng trận vào CSV: {match_csv_path}")
        return json_path, [csv_path, match_csv_path]
    
    return json_path, [csv_path]

def collect_player_detailed_data(player_name, season):
    """Thu thập dữ liệu chi tiết về một cầu thủ cụ thể"""
    print(f"===== THU THẬP DỮ LIỆU CHI TIẾT VỀ CẦU THỦ {player_name.upper()} MÙA {season} =====\n")
    
    # 1. Lấy ID mùa giải
    season_id = SEASONS.get(season)
    if not season_id:
        print(f"Không tìm thấy ID cho mùa giải {season}")
        return None
    
    # 2. Tìm kiếm cầu thủ
    matched_players = search_player_by_name(player_name, season_id)
    if not matched_players:
        return None
    
    # Nếu tìm thấy nhiều cầu thủ, chọn cầu thủ đầu tiên
    selected_player = matched_players[0]
    player_id = selected_player.get("id")
    player_name = selected_player.get("name", {}).get("display")
    print(f"\nĐã chọn cầu thủ: {player_name} (ID: {player_id}) để thu thập dữ liệu\n")
    
    # 3. Thu thập dữ liệu chi tiết
    general_info = get_player_general_info(player_id, season_id)
    stats_data = get_player_stats(player_id, season_id)
    match_stats = get_player_match_stats(player_id, season_id)
    
    # 4. Trích xuất và ghép nối tất cả dữ liệu
    player_detailed_data = extract_all_player_data(general_info, stats_data, match_stats, season)
    
    # 5. Lưu dữ liệu
    if player_detailed_data:
        json_path, csv_paths = save_player_data(player_detailed_data, player_name, season)
        
        # 6. Hiển thị thông tin tóm tắt
        print("\n===== THÔNG TIN TÓM TẮT =====")
        print(f"Tên cầu thủ: {player_detailed_data.get('name')}")
        print(f"Đội bóng: {player_detailed_data.get('team')}")
        print(f"Vị trí: {player_detailed_data.get('position')}")
        print(f"Mùa giải: {player_detailed_data.get('season')}")
        print(f"Tuổi: {player_detailed_data.get('age')}")
        print(f"Quốc tịch: {player_detailed_data.get('nationality')}")
        
        print("\n----- Thống kê thi đấu -----")
        print(f"Số trận: {player_detailed_data.get('stat_appearances', 'N/A')}")
        print(f"Số phút: {player_detailed_data.get('stat_minsPlayed', 'N/A')}")
        
        # Hiển thị các thống kê khác tùy theo vị trí
        position = player_detailed_data.get('position', '').lower()
        
        if "defender" in position:
            print("\n----- Thống kê phòng ngự -----")
            print(f"Số lần tắc bóng: {player_detailed_data.get('stat_tackles', 'N/A')}")
            print(f"Số lần cắt bóng: {player_detailed_data.get('stat_interception', 'N/A')}")
            print(f"Số lần phá bóng: {player_detailed_data.get('stat_clearance', 'N/A')}")
            print(f"Số lần giành bóng bổng: {player_detailed_data.get('stat_aerialWon', 'N/A')}")
            print(f"Số lần cứu thua: {player_detailed_data.get('stat_blocks', 'N/A')}")
            
        elif "midfielder" in position or "forward" in position:
            print("\n----- Thống kê tấn công -----")
            print(f"Số bàn thắng: {player_detailed_data.get('stat_goals', 'N/A')}")
            print(f"Số đường kiến tạo: {player_detailed_data.get('stat_assists', 'N/A')}")
            print(f"Số cơ hội tạo ra: {player_detailed_data.get('stat_bigChanceCreated', 'N/A')}")
            print(f"Số lần sút: {player_detailed_data.get('stat_totalScoringAtt', 'N/A')}")
            print(f"Số đường chuyền chính xác: {player_detailed_data.get('stat_accuratePass', 'N/A')}")
            
        elif "goalkeeper" in position:
            print("\n----- Thống kê thủ môn -----")
            print(f"Số lần cứu thua: {player_detailed_data.get('stat_saves', 'N/A')}")
            print(f"Số trận giữ sạch lưới: {player_detailed_data.get('stat_cleanSheet', 'N/A')}")
            print(f"Số bàn thủng lưới: {player_detailed_data.get('stat_goalsConceded', 'N/A')}")
            
        print("\n----- Các file đã lưu -----")
        print(f"JSON: {json_path}")
        for path in csv_paths:
            print(f"CSV: {path}")
            
        return player_detailed_data
        
    return None

def collect_player_by_id(player_id, season):
    """Thu thập dữ liệu chi tiết về một cầu thủ theo ID cụ thể"""
    print(f"===== THU THẬP DỮ LIỆU CHI TIẾT VỀ CẦU THỦ ID {player_id} MÙA {season} =====\n")
    
    # 1. Lấy ID mùa giải
    season_id = SEASONS.get(season)
    if not season_id:
        print(f"Không tìm thấy ID cho mùa giải {season}")
        return None
    
    # 2. Thu thập thông tin cơ bản về cầu thủ
    general_info = get_player_general_info(player_id, season_id)
    if not general_info:
        print(f"Không tìm thấy thông tin cơ bản cho cầu thủ ID {player_id}")
        return None
        
    player_name = general_info.get("name", {}).get("display", f"Player_{player_id}")
    print(f"\nĐã tìm thấy cầu thủ: {player_name} (ID: {player_id})\n")
    
    # 3. Thu thập dữ liệu chi tiết
    stats_data = get_player_stats(player_id, season_id)
    match_stats = get_player_match_stats(player_id, season_id)
    
    # 4. Trích xuất và ghép nối tất cả dữ liệu
    player_detailed_data = extract_all_player_data(general_info, stats_data, match_stats, season)
    
    # 5. Lưu dữ liệu
    if player_detailed_data:
        json_path, csv_paths = save_player_data(player_detailed_data, player_name, season)
        
        # 6. Hiển thị thông tin tóm tắt
        print("\n===== THÔNG TIN TÓM TẮT =====")
        print(f"Tên cầu thủ: {player_detailed_data.get('name')}")
        print(f"Đội bóng: {player_detailed_data.get('team')}")
        print(f"Vị trí: {player_detailed_data.get('position')}")
        print(f"Mùa giải: {player_detailed_data.get('season')}")
        print(f"Tuổi: {player_detailed_data.get('age')}")
        print(f"Quốc tịch: {player_detailed_data.get('nationality')}")
        
        print("\n----- Thống kê thi đấu -----")
        print(f"Số trận: {player_detailed_data.get('stat_appearances', 'N/A')}")
        print(f"Số phút: {player_detailed_data.get('stat_minsPlayed', 'N/A')}")
        
        # Hiển thị tất cả các thống kê có giá trị (trừ các thống kê cơ bản)
        print("\n----- Tất cả thống kê chi tiết -----")
        stat_keys = [k for k in player_detailed_data.keys() if k.startswith('stat_') and k not in ['stat_appearances', 'stat_minsPlayed', 'stat_goals', 'stat_assists']]
        stat_keys.sort()
        
        for key in stat_keys:
            value = player_detailed_data.get(key)
            if value is not None and value != 'N/A':
                # Loại bỏ tiền tố 'stat_' để hiển thị dễ đọc hơn
                clean_key = key.replace('stat_', '')
                print(f"{clean_key}: {value}")
        
        # In ra tổng số các loại thống kê
        print(f"\nTổng số trường thống kê: {len(stat_keys)}")
            
        print("\n----- Các file đã lưu -----")
        print(f"JSON: {json_path}")
        for path in csv_paths:
            print(f"CSV: {path}")
            
        return player_detailed_data
        
    return None

if __name__ == "__main__":
    # Thu thập dữ liệu cầu thủ có ID 139648 mùa 2023-2024
    collect_player_by_id(139648, "2023-2024") 