import os
from datetime import datetime
import random

# Cấu hình thư mục
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Tạo thư mục data nếu chưa tồn tại
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Cấu hình API
API_BASE_URL = 'https://footballapi.pulselive.com/football'

# Headers cho API - giống với dự án gốc
API_HEADERS = {
    'Accept': '*/*',
    'Origin': 'https://www.premierleague.com',
    'Referer': 'https://www.premierleague.com/',
}

# Cấu hình mùa giải - sử dụng ID giống dự án gốc
SEASONS = {
    '2024-2025': '719',  # ID cập nhật cho mùa 2024-2025
    '2023-2024': '578',
    '2022-2023': '489',
    '2021-2022': '418',
    '2020-2021': '363',
    '2019-2020': '274',
    '2018-2019': '210',
    '2017-2018': '79',
}

# Cấu hình logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = os.path.join(BASE_DIR, 'scraper.log')

# Cấu hình delay
MIN_DELAY = 1
MAX_DELAY = 3

# Hàm tạo đường dẫn output
def get_output_path(data_type, season, file_format='json'):
    """Tạo đường dẫn output cho dữ liệu
    
    Args:
        data_type (str): Loại dữ liệu (matches, players)
        season (str): Mùa giải (ví dụ: 2023-2024)
        file_format (str): Định dạng file (json, csv)
        
    Returns:
        str: Đường dẫn đầy đủ đến file output
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{data_type}_{season}_{timestamp}.{file_format}"
    return os.path.join(DATA_DIR, filename)

# Danh sách User-Agent
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
]

def get_random_headers():
    """Lấy headers ngẫu nhiên"""
    headers = API_HEADERS.copy()
    headers['User-Agent'] = random.choice(USER_AGENTS)
    return headers

# Hàm kiểm tra và cập nhật ID mùa giải
def update_season_id(season: str, season_id: int) -> None:
    """Cập nhật ID mùa giải khi có thông tin mới"""
    if season in SEASONS:
        SEASONS[season] = season_id
        print(f"Đã cập nhật ID mùa giải {season}: {season_id}") 