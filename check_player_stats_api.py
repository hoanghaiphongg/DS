import sys
import os
import json
import requests
import time
import random
from pprint import pprint

# Thêm thư mục gốc vào path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import API_BASE_URL, get_random_headers, SEASONS, MIN_DELAY, MAX_DELAY

def check_player_stats_api(season_id='719', player_id=None):
    """Kiểm tra API thống kê cầu thủ và hiển thị cấu trúc dữ liệu"""
    print(f"===== KIỂM TRA API THỐNG KÊ CẦU THỦ =====")
    
    # Tạo session
    session = requests.Session()
    session.headers.update(get_random_headers())
    
    # Nếu không có ID cầu thủ, trước tiên lấy danh sách cầu thủ
    if not player_id:
        url = f"{API_BASE_URL}/players?pageSize=10&compSeasons={season_id}"
        
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            print(f"Đang gửi request để lấy danh sách cầu thủ: {url}")
            response = session.get(url)
            response.raise_for_status()
            
            data = response.json()
            players = data.get("content", [])
            
            if not players:
                print("Không tìm thấy cầu thủ nào!")
                return
            
            # Lấy ID cầu thủ đầu tiên
            player_id = players[0].get("id")
            player_name = players[0].get("name", {}).get("display", "Unknown")
            print(f"Tìm thấy cầu thủ: {player_name} (ID: {player_id})")
        
        except Exception as e:
            print(f"Lỗi khi lấy danh sách cầu thủ: {str(e)}")
            return
    
    # Kiểm tra các API thống kê khác nhau
    endpoints = [
        # API thống kê cơ bản
        f"{API_BASE_URL}/stats/player/{player_id}?comps=1&compSeasons={season_id}",
        
        # API thống kê chi tiết theo vị trí
        f"{API_BASE_URL}/players/{player_id}",
        
        # API thống kê theo mùa giải
        f"{API_BASE_URL}/players/playerSeasons?playerId={player_id}&compSeasons={season_id}",
    ]
    
    # Kiểm tra từng endpoint
    for endpoint in endpoints:
        try:
            # Thêm delay ngẫu nhiên
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            print(f"\nĐang kiểm tra API: {endpoint}")
            response = session.get(endpoint)
            response.raise_for_status()
            
            data = response.json()
            
            # Hiển thị cấu trúc dữ liệu
            print("=== CẤU TRÚC DỮ LIỆU ===")
            if isinstance(data, dict):
                for key in data.keys():
                    print(f"- {key}")
            else:
                print("Dữ liệu trả về là một danh sách")
            
            # Lưu kết quả vào file JSON
            output_file = f"player_stats_api_{endpoint.split('/')[-1].split('?')[0]}_{player_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"Đã lưu dữ liệu vào file: {output_file}")
            
        except Exception as e:
            print(f"Lỗi khi kiểm tra API {endpoint}: {str(e)}")

if __name__ == "__main__":
    # Mặc định sử dụng mùa 2024-2025
    season_id = SEASONS.get('2024-2025', '719')
    
    # Có thể truyền ID cầu thủ qua tham số dòng lệnh
    player_id = None
    if len(sys.argv) > 1:
        player_id = sys.argv[1]
    
    check_player_stats_api(season_id, player_id) 