#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys
import json
import csv
from datetime import datetime

# Thêm thư mục gốc vào path để import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import LOG_FORMAT, LOG_FILE, SEASONS, API_BASE_URL, API_HEADERS

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

def parse_args():
    """Xử lý tham số dòng lệnh"""
    parser = argparse.ArgumentParser(description='Thu thập dữ liệu của một trận đấu duy nhất')
    parser.add_argument('--match-id', type=int, required=True,
                        help='ID của trận đấu cần thu thập')
    parser.add_argument('--season', choices=list(SEASONS.keys()), default='2023-2024',
                        help='Mùa giải của trận đấu (mặc định: 2023-2024)')
    parser.add_argument('--format', choices=['json', 'csv', 'both'], default='both',
                        help='Định dạng file output (mặc định: both - cả JSON và CSV)')
    
    return parser.parse_args()

def get_match_data(match_id, session):
    """Lấy dữ liệu trận đấu trực tiếp từ API"""
    url = f"{API_BASE_URL}/fixtures/{match_id}?altIds=true"
    
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu trận đấu {match_id}: {str(e)}")
        return None

def get_match_stats(match_id, session):
    """Lấy thống kê trận đấu trực tiếp từ API"""
    url = f"{API_BASE_URL}/stats/match/{match_id}"
    
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Lỗi khi lấy thống kê trận đấu {match_id}: {str(e)}")
        return None

def flatten_json(nested_json, prefix=''):
    """Làm phẳng cấu trúc JSON lồng nhau thành dict một cấp"""
    flattened = {}
    
    if not isinstance(nested_json, dict):
        return {prefix: nested_json}
    
    for key, value in nested_json.items():
        if isinstance(value, dict) and value:
            # Nếu giá trị là dict, đệ quy để làm phẳng
            flattened_child = flatten_json(value, f"{prefix}{key}_")
            flattened.update(flattened_child)
        elif isinstance(value, list) and value:
            # Nếu giá trị là list, chuyển thành chuỗi JSON
            flattened[f"{prefix}{key}"] = json.dumps(value)
        else:
            # Nếu là giá trị đơn giản, giữ nguyên
            flattened[f"{prefix}{key}"] = value
    
    return flattened

def main():
    """Hàm chính để chạy thu thập dữ liệu"""
    args = parse_args()
    
    # Tạo session
    import requests
    session = requests.Session()
    session.headers.update(API_HEADERS)
    
    logger.info(f"Đang thu thập dữ liệu trận đấu {args.match_id}")
    
    # Thu thập dữ liệu trận đấu
    match_data = get_match_data(args.match_id, session)
    if not match_data:
        logger.error(f"Không thể thu thập dữ liệu trận đấu {args.match_id}")
        return
    
    # Thu thập thống kê trận đấu
    stats_data = get_match_stats(args.match_id, session)
    
    # Kết hợp dữ liệu
    combined_data = {
        "id": match_data.get("id"),
        "kick_off": match_data.get("kickoff"),
        "teams": match_data.get("teams"),
        "ground": match_data.get("ground"),
        "clock": match_data.get("clock"),
        "halfTimeScore": match_data.get("halfTimeScore"),
        "teamLists": match_data.get("teamLists"),
        "events": match_data.get("events"),
        "stats": stats_data.get("data") if stats_data else None,
        "season": args.season,
        "type": "match",
        "raw_match_data": match_data,  # Lưu toàn bộ dữ liệu gốc
        "raw_stats_data": stats_data   # Lưu toàn bộ dữ liệu thống kê gốc
    }
    
    # Tạo thư mục data nếu chưa tồn tại
    os.makedirs('data', exist_ok=True)
    
    # Lưu dữ liệu
    if args.format in ['json', 'both']:
        # Tạo tên file với match_id
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = os.path.join('data', f"match_{args.match_id}_{timestamp}.json")
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Đã lưu dữ liệu JSON trận đấu {args.match_id} vào {json_file}")
    
    if args.format in ['csv', 'both']:
        # Tạo tên file với match_id
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = os.path.join('data', f"match_{args.match_id}_{timestamp}.csv")
        
        # Làm phẳng dữ liệu JSON
        flattened_data = flatten_json(combined_data)
        
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(flattened_data.keys()))
            writer.writeheader()
            writer.writerow(flattened_data)
        
        logger.info(f"Đã lưu dữ liệu CSV trận đấu {args.match_id} vào {csv_file}")
    
    logger.info(f"Thu thập dữ liệu trận đấu {args.match_id} hoàn tất!")

if __name__ == "__main__":
    main() 