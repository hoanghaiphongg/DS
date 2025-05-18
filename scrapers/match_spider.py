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

class MatchSpider:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(API_HEADERS)

    def get_season_matches(self, season_id: str) -> List[int]:
        """Lấy danh sách ID trận đấu của một mùa giải"""
        url = f"{API_BASE_URL}/fixtures?comps=1&compSeasons={season_id}&page=0&pageSize=2000"
        
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
            match_ids = []
            
            for match in data.get("content", []):
                match_ids.append(int(match.get("id")))
            
            logger.info(f"Tìm thấy {len(match_ids)} trận đấu cho mùa giải {season_id}")
            return match_ids
        
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách trận đấu: {str(e)}")
            return []

    def get_match_data(self, match_id: int) -> Optional[Dict]:
        """Lấy thông tin chi tiết về trận đấu"""
        url = f"{API_BASE_URL}/fixtures/{match_id}?altIds=true"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin trận đấu {match_id}: {str(e)}")
            return None

    def get_match_stats(self, match_id: int) -> Optional[Dict]:
        """Lấy thống kê của trận đấu"""
        url = f"{API_BASE_URL}/stats/match/{match_id}"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Lỗi khi lấy thống kê trận đấu {match_id}: {str(e)}")
            return None

    def extract_match_data(self, match_data: Dict, stats_data: Dict, season: str) -> Dict:
        """Trích xuất dữ liệu quan trọng từ trận đấu"""
        # Giữ lại cấu trúc dữ liệu giống dự án gốc
        combined_data = {
            "id": match_data.get("id"),
            "kick_off": match_data.get("kickoff"),
            "teams": match_data.get("teams"),
            "ground": match_data.get("ground"),
            "clock": match_data.get("clock"),
            "halfTimeScore": match_data.get("halfTimeScore"),
            "teamLists": match_data.get("teamLists"),
            "stats": stats_data.get("data") if stats_data else None,
            "season": season,
            "type": "match"
        }
        
        # Lọc sự kiện (chỉ lấy bàn thắng, phạt đền và phản lưới)
        events = []
        if "events" in match_data:
            for event in match_data["events"]:
                if isinstance(event, dict) and event.get("type") in ["G", "P", "O"]:
                    events.append(event)
        
        combined_data["events"] = events
        
        return combined_data

    def scrape_match(self, match_id: int, season: str) -> Optional[Dict]:
        """Thu thập dữ liệu cho một trận đấu"""
        match_data = self.get_match_data(match_id)
        if not match_data:
            return None
        
        stats_data = self.get_match_stats(match_id)
        
        # Trích xuất dữ liệu quan trọng
        extracted_data = self.extract_match_data(match_data, stats_data, season)
        
        return extracted_data

    def scrape_season(self, season: str) -> List[Dict]:
        """Thu thập dữ liệu cho một mùa giải"""
        season_id = SEASONS.get(season)
        if not season_id:
            logger.error(f"Không tìm thấy ID cho mùa giải {season}")
            return []
        
        match_ids = self.get_season_matches(season_id)
        matches_data = []
        
        for match_id in match_ids:
            logger.info(f"Đang thu thập dữ liệu trận đấu {match_id}")
            match_data = self.scrape_match(match_id, season)
            
            if match_data:
                matches_data.append(match_data)
        
        return matches_data

    def save_data_json(self, data: List[Dict], season: str) -> str:
        """Lưu dữ liệu vào file JSON"""
        if not data:
            logger.warning(f"Không có dữ liệu để lưu cho mùa giải {season}")
            return None
        
        output_path = get_output_path("matches", season, "json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Đã lưu {len(data)} trận đấu vào {output_path}")
        return output_path
    
    def save_data_csv(self, data: List[Dict], season: str) -> str:
        """Lưu dữ liệu vào file CSV"""
        if not data:
            logger.warning(f"Không có dữ liệu để lưu cho mùa giải {season}")
            return None
        
        output_path = get_output_path("matches", season, "csv")
        
        # Lấy tất cả các trường có trong dữ liệu
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Đã lưu {len(data)} trận đấu vào {output_path}")
        return output_path

if __name__ == "__main__":
    spider = MatchSpider()
    for season in SEASONS.keys():
        data = spider.scrape_season(season)
        json_path = spider.save_data_json(data, season)
        csv_path = spider.save_data_csv(data, season)
        if json_path and csv_path:
            logger.info(f"Đã lưu dữ liệu trận đấu mùa {season} vào {json_path} và {csv_path}") 