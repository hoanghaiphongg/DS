import json
import logging
import requests
import time
import random
import sys
import os
from datetime import datetime

# Thêm thư mục gốc vào path để import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import (
    API_BASE_URL, API_HEADERS, SEASONS, MIN_DELAY, MAX_DELAY, DATA_DIR,
    get_output_path
)

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraper_seasons.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SeasonFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(API_HEADERS)

    def get_season_matches(self, season_id: str):
        """Lấy danh sách ID trận đấu của một mùa giải"""
        url = f"{API_BASE_URL}/fixtures?comps=1&compSeasons={season_id}&page=0&pageSize=2000"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            logger.info(f"Đang gửi request đến: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            logger.info(f"Đã nhận phản hồi thành công (status code: {response.status_code})")
            data = response.json()
            match_ids = []
            
            for match in data.get("content", []):
                match_ids.append(int(match.get("id")))
            
            logger.info(f"Tìm thấy {len(match_ids)} trận đấu cho mùa giải {season_id}")
            return match_ids
        
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách trận đấu: {str(e)}")
            return []

    def get_match_data(self, match_id: int):
        """Lấy thông tin chi tiết về trận đấu"""
        url = f"{API_BASE_URL}/fixtures/{match_id}?altIds=true"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            logger.info(f"Đang lấy dữ liệu trận đấu {match_id}")
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin trận đấu {match_id}: {str(e)}")
            return None

    def get_match_stats(self, match_id: int):
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

    def scrape_match(self, match_id: int, season: str):
        """Thu thập dữ liệu cho một trận đấu"""
        match_data = self.get_match_data(match_id)
        if not match_data:
            return None
        
        stats_data = self.get_match_stats(match_id)
        
        # Kết hợp dữ liệu
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

    def scrape_season(self, season: str):
        """Thu thập dữ liệu cho một mùa giải"""
        season_id = SEASONS.get(season)
        if not season_id:
            logger.error(f"Không tìm thấy ID cho mùa giải {season}")
            return []
        
        logger.info(f"Bắt đầu thu thập dữ liệu mùa giải {season} (ID: {season_id})")
        match_ids = self.get_season_matches(season_id)
        
        if not match_ids:
            logger.error(f"Không tìm thấy trận đấu nào cho mùa giải {season}")
            return []
        
        logger.info(f"Chuẩn bị thu thập dữ liệu cho {len(match_ids)} trận đấu")
        matches_data = []
        
        for idx, match_id in enumerate(match_ids):
            logger.info(f"Đang thu thập dữ liệu trận đấu {match_id} ({idx+1}/{len(match_ids)})")
            match_data = self.scrape_match(match_id, season)
            
            if match_data:
                matches_data.append(match_data)
        
        logger.info(f"Đã thu thập dữ liệu {len(matches_data)}/{len(match_ids)} trận đấu cho mùa giải {season}")
        return matches_data

    def save_data_json(self, data, season: str):
        """Lưu dữ liệu vào file JSON"""
        if not data:
            logger.warning(f"Không có dữ liệu để lưu cho mùa giải {season}")
            return None
        
        output_path = get_output_path("matches", season, "json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Đã lưu {len(data)} trận đấu vào {output_path}")
        return output_path

def fetch_multiple_seasons(seasons):
    """Thu thập dữ liệu cho nhiều mùa giải"""
    fetcher = SeasonFetcher()
    results = {}
    
    for season in seasons:
        logger.info(f"===== Bắt đầu thu thập dữ liệu mùa giải {season} =====")
        data = fetcher.scrape_season(season)
        
        if data:
            json_path = fetcher.save_data_json(data, season)
            results[season] = {
                "total_matches": len(data),
                "output_file": json_path
            }
            logger.info(f"===== Hoàn thành thu thập dữ liệu mùa giải {season} =====")
        else:
            logger.error(f"Không thu thập được dữ liệu cho mùa giải {season}")
            results[season] = {
                "total_matches": 0,
                "output_file": None
            }
    
    return results

if __name__ == "__main__":
    target_seasons = ['2023-2024', '2022-2023', '2021-2022', '2020-2021']
    logger.info(f"Bắt đầu thu thập dữ liệu cho {len(target_seasons)} mùa giải: {', '.join(target_seasons)}")
    
    results = fetch_multiple_seasons(target_seasons)
    
    print("\n===== KẾT QUẢ THU THẬP DỮ LIỆU =====")
    for season, result in results.items():
        status = "✅ Thành công" if result["total_matches"] > 0 else "❌ Thất bại"
        print(f"{status} - Mùa {season}: {result['total_matches']} trận đấu")
        if result["output_file"]:
            print(f"  File: {result['output_file']}")
    print("=====================================") 