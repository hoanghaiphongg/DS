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
    API_BASE_URL, API_HEADERS, MIN_DELAY, MAX_DELAY, DATA_DIR
)

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MatchFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(API_HEADERS)

    def get_match_data(self, match_id: int):
        """Lấy thông tin chi tiết về trận đấu"""
        url = f"{API_BASE_URL}/fixtures/{match_id}?altIds=true"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            logger.info(f"Đang gửi request đến: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            logger.info(f"Đã nhận phản hồi thành công (status code: {response.status_code})")
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
            
            logger.info(f"Đang gửi request đến: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            logger.info(f"Đã nhận phản hồi thành công (status code: {response.status_code})")
            return response.json()
        
        except Exception as e:
            logger.error(f"Lỗi khi lấy thống kê trận đấu {match_id}: {str(e)}")
            return None

    def fetch_match(self, match_id: int):
        """Thu thập dữ liệu cho một trận đấu và trả về dạng JSON"""
        logger.info(f"Bắt đầu thu thập dữ liệu cho trận đấu {match_id}")
        
        # Lấy dữ liệu trận đấu
        match_data = self.get_match_data(match_id)
        if not match_data:
            logger.error(f"Không thể lấy dữ liệu trận đấu {match_id}")
            return None
        
        # Lấy thống kê trận đấu
        stats_data = self.get_match_stats(match_id)
        if not stats_data:
            logger.warning(f"Không thể lấy thống kê trận đấu {match_id}")
        
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

    def save_to_json(self, data, match_id):
        """Lưu dữ liệu vào file JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"match_{match_id}_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Đã lưu dữ liệu trận đấu vào: {filepath}")
        return filepath

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Sử dụng: python fetch_match_json.py <match_id>")
        sys.exit(1)
    
    try:
        match_id = int(sys.argv[1])
        fetcher = MatchFetcher()
        match_data = fetcher.fetch_match(match_id)
        
        if match_data:
            json_path = fetcher.save_to_json(match_data, match_id)
            print(f"✅ Đã lưu dữ liệu trận đấu {match_id} vào: {json_path}")
        else:
            print(f"❌ Không thể lấy dữ liệu trận đấu {match_id}")
    
    except ValueError:
        print("Lỗi: Match ID phải là một số nguyên")
        sys.exit(1)
    except Exception as e:
        print(f"Lỗi không xác định: {str(e)}")
        sys.exit(1) 