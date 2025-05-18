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
    LOG_FORMAT, LOG_FILE, MIN_DELAY, MAX_DELAY
)

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PlayerSpider:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(API_HEADERS)

    def get_season_players(self, season_id: str) -> List[Dict]:
        """Lấy danh sách cầu thủ của một mùa giải"""
        url = f"{API_BASE_URL}/players?pageSize=10000&compSeasons={season_id}"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            response = self.session.get(url)
            
            # In ra thông tin chi tiết về phản hồi
            logger.info(f"URL: {url}")
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Headers: {dict(response.headers)}")
            logger.info(f"Response: {response.text[:500]}...")  # In 500 ký tự đầu tiên
            
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

    def get_player_stats(self, player_id: int, season_id: str) -> Optional[Dict]:
        """Lấy thống kê của cầu thủ trong một mùa giải"""
        url = f"{API_BASE_URL}/stats/player/{player_id}?comps=1&compSeasons={season_id}"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Lỗi khi lấy thống kê cầu thủ {player_id}: {str(e)}")
            return None
    
    def extract_player_data(self, player_data: Dict, stats_data: Dict, season: str) -> Dict:
        """Trích xuất dữ liệu quan trọng từ cầu thủ"""
        # Khởi tạo dict với các trường cơ bản
        extracted_data = {
            "player_id": player_data.get("id"),
            "season": season,
            "name": player_data.get("name", {}).get("display"),
            "position": player_data.get("info", {}).get("positionInfo"),
            "shirt_num": player_data.get("info", {}).get("shirtNum"),
            "nationality": player_data.get("nationalTeam", {}).get("country") if player_data.get("nationalTeam") else None,
            "height": player_data.get("info", {}).get("height"),
            "weight": player_data.get("info", {}).get("weight"),
            "date_of_birth": player_data.get("birth", {}).get("date", {}).get("millis") if player_data.get("birth", {}).get("date") else None,
            "age": player_data.get("age"),
        }
        
        # Thêm thông tin đội bóng
        if "currentTeam" in player_data:
            extracted_data["team"] = player_data["currentTeam"].get("name")
            extracted_data["team_id"] = player_data["currentTeam"].get("id")
        
        # Thêm thống kê
        if stats_data:
            # Thống kê cơ bản
            if "entity" in stats_data:
                extracted_data["appearances"] = stats_data.get("entity", {}).get("appearances")
                extracted_data["goals"] = stats_data.get("entity", {}).get("goals")
                extracted_data["assists"] = stats_data.get("entity", {}).get("assists")
                extracted_data["wins"] = stats_data.get("entity", {}).get("wins")
                extracted_data["losses"] = stats_data.get("entity", {}).get("losses")
            
            # Thống kê chi tiết
            if "stats" in stats_data:
                for stat in stats_data["stats"]:
                    name = stat.get("name")
                    if name:
                        extracted_data[f"stat_{name}"] = stat.get("value")
        
        return extracted_data

    def scrape_player(self, player_data: Dict, season: str, season_id: str) -> Optional[Dict]:
        """Thu thập dữ liệu cho một cầu thủ"""
        player_id = int(player_data.get("id", 0))
        if player_id == 0:
            return None
        
        stats_data = self.get_player_stats(player_id, season_id)
        
        # Trích xuất dữ liệu quan trọng
        extracted_data = self.extract_player_data(player_data, stats_data, season)
        
        return extracted_data

    def scrape_season(self, season: str) -> List[Dict]:
        """Thu thập dữ liệu cầu thủ cho một mùa giải"""
        season_id = SEASONS.get(season)
        if not season_id:
            logger.error(f"Không tìm thấy ID cho mùa giải {season}")
            return []
        
        players = self.get_season_players(season_id)
        players_data = []
        
        for player in players:
            player_id = player.get("id")
            logger.info(f"Đang thu thập dữ liệu cầu thủ {player_id}")
            player_data = self.scrape_player(player, season, season_id)
            
            if player_data:
                players_data.append(player_data)
        
        return players_data

    def save_data_json(self, data: List[Dict], season: str) -> str:
        """Lưu dữ liệu vào file JSON"""
        if not data:
            logger.warning(f"Không có dữ liệu để lưu cho mùa giải {season}")
            return None
        
        output_path = get_output_path("players", season, "json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Đã lưu {len(data)} cầu thủ vào {output_path}")
        return output_path
    
    def save_data_csv(self, data: List[Dict], season: str) -> str:
        """Lưu dữ liệu vào file CSV"""
        if not data:
            logger.warning(f"Không có dữ liệu để lưu cho mùa giải {season}")
            return None
        
        output_path = get_output_path("players", season, "csv")
        
        # Lấy tất cả các trường có trong dữ liệu
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Đã lưu {len(data)} cầu thủ vào {output_path}")
        return output_path

if __name__ == "__main__":
    spider = PlayerSpider()
    for season in SEASONS.keys():
        data = spider.scrape_season(season)
        json_path = spider.save_data_json(data, season)
        csv_path = spider.save_data_csv(data, season)
        if json_path and csv_path:
            logger.info(f"Đã lưu dữ liệu cầu thủ mùa {season} vào {json_path} và {csv_path}") 