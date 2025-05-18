import json
import csv
import logging
import requests
import time
import random
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

# Thêm thư mục gốc vào path để import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    API_BASE_URL, API_HEADERS, SEASONS, get_output_path, 
    LOG_FORMAT, LOG_FILE, MIN_DELAY, MAX_DELAY, get_random_headers
)

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("enhanced_player_spider.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EnhancedPlayerSpider:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(API_HEADERS)
        
        # Đảm bảo có User-Agent
        if 'User-Agent' not in self.session.headers:
            self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})

    def get_season_players(self, season_id: str) -> List[Dict]:
        """Lấy danh sách cầu thủ của một mùa giải"""
        url = f"{API_BASE_URL}/players?pageSize=1000&compSeasons={season_id}"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            # Thay đổi User-Agent mỗi lần gọi API
            self.session.headers.update(get_random_headers())
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            players = data.get("content", [])
            
            logger.info(f"Tìm thấy {len(players)} cầu thủ cho mùa giải {season_id}")
            
            # Sắp xếp cầu thủ theo ID (từ nhỏ đến lớn)
            sorted_players = sorted(players, key=lambda player: int(player.get("id", 0)))
            return sorted_players
        
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách cầu thủ: {str(e)}")
            return []

    def get_player_general_info(self, player_id: int, season_id: str) -> Optional[Dict]:
        """Lấy thông tin chung về cầu thủ"""
        url = f"{API_BASE_URL}/players/{player_id}?comps=1&compSeasons={season_id}"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            # Thay đổi User-Agent mỗi lần gọi API
            self.session.headers.update(get_random_headers())
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin chung về cầu thủ {player_id}: {str(e)}")
            return None

    def get_player_stats(self, player_id: int, season_id: str) -> Optional[Dict]:
        """Lấy thống kê chi tiết của cầu thủ trong một mùa giải"""
        url = f"{API_BASE_URL}/stats/player/{player_id}?comps=1&compSeasons={season_id}"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            # Thay đổi User-Agent mỗi lần gọi API
            self.session.headers.update(get_random_headers())
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Lỗi khi lấy thống kê cầu thủ {player_id}: {str(e)}")
            return None
    
    def get_player_match_stats(self, player_id: int, season_id: str) -> Optional[Dict]:
        """Lấy thống kê trận đấu của cầu thủ"""
        url = f"{API_BASE_URL}/players/match-stats?playerId={player_id}&compSeason={season_id}"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            # Thay đổi User-Agent mỗi lần gọi API
            self.session.headers.update(get_random_headers())
            
            response = self.session.get(url)
            
            # Kiểm tra nếu không có dữ liệu (204 No Content)
            if response.status_code == 204:
                logger.info(f"Không có thống kê trận đấu cho cầu thủ {player_id}")
                return None
                
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            # Nhiều cầu thủ sẽ không có thống kê trận đấu, đây không phải lỗi nghiêm trọng
            if "404" in str(e):
                logger.info(f"Không có thống kê trận đấu cho cầu thủ {player_id}")
                return None
            logger.error(f"Lỗi khi lấy thống kê trận đấu của cầu thủ {player_id}: {str(e)}")
            return None
    
    def extract_player_data(self, general_data: Dict, stats_data: Dict, match_stats: Dict, season: str) -> Dict:
        """Trích xuất dữ liệu cầu thủ đầy đủ từ các API"""
        if not general_data:
            return None
        
        # Khởi tạo dict với các trường cơ bản
        result = {
            "player_id": general_data.get("id"),
            "season": season,
            "name": general_data.get("name", {}).get("display"),
            "first_name": general_data.get("name", {}).get("first"),
            "last_name": general_data.get("name", {}).get("last"),
            "position": general_data.get("info", {}).get("positionInfo"),
            "shirt_num": general_data.get("info", {}).get("shirtNum"),
            "nationality": general_data.get("nationalTeam", {}).get("country") if general_data.get("nationalTeam") else None,
            "nationality_code": general_data.get("nationalTeam", {}).get("isoCode") if general_data.get("nationalTeam") else None,
            "height": general_data.get("info", {}).get("height"),
            "weight": general_data.get("info", {}).get("weight"),
            "date_of_birth": general_data.get("birth", {}).get("date", {}).get("millis") if general_data.get("birth", {}).get("date") else None,
            "age": general_data.get("age"),
            "image_url": general_data.get("altImageUrl") or general_data.get("imageUrl")
        }
        
        # Thêm thông tin đội bóng
        if "currentTeam" in general_data:
            result["team_id"] = general_data["currentTeam"].get("id")
            result["team_name"] = general_data["currentTeam"].get("name")
            result["team_short_name"] = general_data["currentTeam"].get("shortName")
            result["team_abbr"] = general_data["currentTeam"].get("club", {}).get("abbr") if "club" in general_data["currentTeam"] else None
            result["team_slug"] = general_data["currentTeam"].get("club", {}).get("slug") if "club" in general_data["currentTeam"] else None
        
        # Thêm các thống kê cơ bản
        if stats_data:
            if "entity" in stats_data:
                basic_stats = stats_data.get("entity", {})
                
                # Các thống kê cơ bản
                result["appearances"] = basic_stats.get("appearances")
                result["sub_on"] = basic_stats.get("subOn")
                result["sub_off"] = basic_stats.get("subOff")
                result["mins_played"] = basic_stats.get("minsPlayed")
                result["goals"] = basic_stats.get("goals")
                result["assists"] = basic_stats.get("assists")
                result["clean_sheets"] = basic_stats.get("cleanSheets")
                result["wins"] = basic_stats.get("wins")
                result["losses"] = basic_stats.get("losses")
                result["yellow_cards"] = basic_stats.get("yellowCards")
                result["red_cards"] = basic_stats.get("redCards")
                result["fouls"] = basic_stats.get("fouls")
                result["offsides"] = basic_stats.get("offsides")
                result["bonus"] = basic_stats.get("bonus")
            
            # Thêm thống kê chi tiết
            if "stats" in stats_data:
                for stat in stats_data["stats"]:
                    name = stat.get("name")
                    value = stat.get("value")
                    
                    if name:
                        # Chuyển đổi tên thống kê thành snake_case
                        stat_name = name.replace(" ", "_").lower()
                        result[f"stat_{stat_name}"] = value
                        
                        # Thêm thứ hạng nếu có
                        if "rank" in stat:
                            result[f"rank_{stat_name}"] = stat.get("rank")
        
        # Thêm thống kê từng trận đấu
        if match_stats and "fixtures" in match_stats:
            fixtures = match_stats["fixtures"]
            result["matches_count"] = len(fixtures)
            
            # Lưu danh sách các trận đấu
            match_list = []
            for fixture in fixtures:
                match_detail = {
                    "match_id": fixture.get("id"),
                    "match_date": fixture.get("kickoff", {}).get("millis"),
                    "home_team": fixture.get("teams", [])[0].get("team", {}).get("name") if fixture.get("teams") and len(fixture.get("teams")) > 0 else None,
                    "away_team": fixture.get("teams", [])[1].get("team", {}).get("name") if fixture.get("teams") and len(fixture.get("teams")) > 1 else None,
                    "score": f"{fixture.get('teams', [])[0].get('score')}-{fixture.get('teams', [])[1].get('score')}" if fixture.get("teams") and len(fixture.get("teams")) > 1 else None,
                    "mins_played": fixture.get("stats", {}).get("minsPlayed"),
                    "goals": fixture.get("stats", {}).get("goals"),
                    "assists": fixture.get("stats", {}).get("assists"),
                    "yellow_cards": fixture.get("stats", {}).get("yellowCards"),
                    "red_cards": fixture.get("stats", {}).get("redCards")
                }
                match_list.append(match_detail)
            
            result["match_details"] = match_list
        
        return result

    def scrape_player(self, player_data: Dict, season: str, season_id: str) -> Optional[Dict]:
        """Thu thập dữ liệu đầy đủ cho một cầu thủ"""
        player_id = int(player_data.get("id", 0))
        player_name = player_data.get("name", {}).get("display", "Unknown")
        
        if player_id == 0:
            logger.warning(f"Cầu thủ không có ID hợp lệ: {player_name}")
            return None
        
        logger.info(f"Thu thập dữ liệu cho cầu thủ: {player_name} (ID: {player_id})")
        
        # Thu thập thông tin từ các API
        general_info = self.get_player_general_info(player_id, season_id)
        stats_data = self.get_player_stats(player_id, season_id)
        match_stats = self.get_player_match_stats(player_id, season_id)
        
        # Trích xuất dữ liệu
        player_full_data = self.extract_player_data(general_info, stats_data, match_stats, season)
        
        # Log kết quả
        if player_full_data:
            logger.info(f"Đã thu thập thành công dữ liệu cho {player_name}")
        else:
            logger.warning(f"Không thể thu thập dữ liệu cho {player_name}")
        
        return player_full_data

    def scrape_season(self, season: str, max_players: int = None) -> List[Dict]:
        """Thu thập dữ liệu cầu thủ cho một mùa giải"""
        season_id = SEASONS.get(season)
        if not season_id:
            logger.error(f"Không tìm thấy ID cho mùa giải {season}")
            return []
        
        logger.info(f"Bắt đầu thu thập dữ liệu cầu thủ cho mùa giải {season} (ID: {season_id})")
        
        # Lấy danh sách cầu thủ
        players = self.get_season_players(season_id)
        
        # Giới hạn số lượng cầu thủ nếu cần
        if max_players and max_players < len(players):
            logger.info(f"Giới hạn thu thập {max_players}/{len(players)} cầu thủ")
            players = players[:max_players]
        
        players_data = []
        
        # Thu thập dữ liệu cho từng cầu thủ
        for i, player in enumerate(players, 1):
            logger.info(f"[{i}/{len(players)}] Đang thu thập dữ liệu cho cầu thủ ID: {player.get('id')}")
            player_data = self.scrape_player(player, season, season_id)
            
            if player_data:
                players_data.append(player_data)
        
        logger.info(f"Đã thu thập dữ liệu cho {len(players_data)}/{len(players)} cầu thủ")
        return players_data

    def save_data_json(self, data: List[Dict], season: str) -> str:
        """Lưu dữ liệu vào file JSON"""
        if not data:
            logger.warning(f"Không có dữ liệu để lưu cho mùa giải {season}")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"players_enhanced_{season.replace('-', '_')}_{timestamp}.json"
        output_path = os.path.join("data", filename)
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs("data", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Đã lưu {len(data)} cầu thủ vào {output_path}")
        return output_path
    
    def save_data_csv(self, data: List[Dict], season: str) -> str:
        """Lưu dữ liệu vào file CSV"""
        if not data:
            logger.warning(f"Không có dữ liệu để lưu cho mùa giải {season}")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"players_enhanced_{season.replace('-', '_')}_{timestamp}.csv"
        output_path = os.path.join("data", filename)
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs("data", exist_ok=True)
        
        # Lấy tất cả các trường có trong dữ liệu, ngoại trừ match_details
        fieldnames = set()
        for item in data:
            item_copy = item.copy()
            # Loại bỏ trường match_details vì nó là một list (không thể xuất trực tiếp vào CSV)
            if "match_details" in item_copy:
                item_copy.pop("match_details")
            fieldnames.update(item_copy.keys())
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            
            for item in data:
                item_copy = item.copy()
                # Loại bỏ trường match_details
                if "match_details" in item_copy:
                    item_copy.pop("match_details")
                writer.writerow(item_copy)
        
        logger.info(f"Đã lưu {len(data)} cầu thủ vào {output_path}")
        return output_path
    
    def save_match_details_csv(self, data: List[Dict], season: str) -> str:
        """Lưu thông tin chi tiết trận đấu của cầu thủ vào file CSV riêng"""
        if not data:
            logger.warning(f"Không có dữ liệu để lưu cho mùa giải {season}")
            return None
        
        match_details = []
        
        # Tạo danh sách chi tiết trận đấu
        for player in data:
            player_id = player.get("player_id")
            player_name = player.get("name")
            
            if "match_details" in player and player["match_details"]:
                for match in player["match_details"]:
                    match_copy = match.copy()
                    match_copy["player_id"] = player_id
                    match_copy["player_name"] = player_name
                    match_details.append(match_copy)
        
        if not match_details:
            logger.warning(f"Không có thông tin trận đấu để lưu cho mùa giải {season}")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"player_match_details_{season.replace('-', '_')}_{timestamp}.csv"
        output_path = os.path.join("data", filename)
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs("data", exist_ok=True)
        
        # Lấy tất cả các trường
        fieldnames = set()
        for item in match_details:
            fieldnames.update(item.keys())
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(match_details)
        
        logger.info(f"Đã lưu {len(match_details)} chi tiết trận đấu vào {output_path}")
        return output_path

if __name__ == "__main__":
    # Test với một cầu thủ
    spider = EnhancedPlayerSpider()
    season_to_scrape = "2024-2025"
    
    # Kiểm tra xem mùa giải có tồn tại trong cấu hình không
    if season_to_scrape not in SEASONS:
        print(f"Mùa giải {season_to_scrape} không tồn tại trong cấu hình")
        sys.exit(1)
    
    # Thu thập dữ liệu cho một cầu thủ cụ thể (nếu biết ID)
    # player_id = 139648  # Ví dụ: Erling Haaland
    # season_id = SEASONS[season_to_scrape]
    # player_data = {"id": player_id, "name": {"display": "Sample Player"}}
    # data = [spider.scrape_player(player_data, season_to_scrape, season_id)]
    
    # Hoặc thu thập dữ liệu cho tất cả cầu thủ trong mùa giải
    data = spider.scrape_season(season_to_scrape)
    
    if data:
        # Lưu dữ liệu vào files
        json_path = spider.save_data_json(data, season_to_scrape)
        csv_path = spider.save_data_csv(data, season_to_scrape)
        match_csv_path = spider.save_match_details_csv(data, season_to_scrape)
        
        print(f"Đã thu thập và lưu dữ liệu cho {len(data)} cầu thủ")
        print(f"JSON: {json_path}")
        print(f"CSV: {csv_path}")
        print(f"Match details CSV: {match_csv_path}") 