#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import argparse
from datetime import datetime

# Thêm thư mục scrapers vào path để import
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scrapers'))
from enhanced_player_spider import EnhancedPlayerSpider
from config import LOG_FORMAT, SEASONS

# Cấu hình logging cho file này
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("enhanced_player_data.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Thu thập dữ liệu nâng cao cho cầu thủ"""
    parser = argparse.ArgumentParser(description='Thu thập dữ liệu nâng cao về cầu thủ')
    parser.add_argument('--season', type=str, default='2024-2025',
                        help='Mùa giải cần thu thập dữ liệu (mặc định: 2024-2025)')
    parser.add_argument('--max', type=int, default=None,
                        help='Số lượng cầu thủ tối đa cần thu thập (mặc định: tất cả)')
    parser.add_argument('--player-id', type=int, default=None,
                        help='ID của cầu thủ cụ thể cần thu thập (không cần nếu thu thập toàn bộ mùa)')
    
    args = parser.parse_args()
    season = args.season
    max_players = args.max
    player_id = args.player_id
    
    # Kiểm tra xem mùa giải có tồn tại trong cấu hình không
    if season not in SEASONS:
        logger.error(f"Mùa giải {season} không tồn tại trong cấu hình. Vui lòng kiểm tra lại.")
        return
    
    season_id = SEASONS[season]
    
    logger.info(f"===== BẮT ĐẦU THU THẬP DỮ LIỆU NÂNG CAO CHO CẦU THỦ MÙA {season} =====")
    logger.info(f"Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Khởi tạo spider
    spider = EnhancedPlayerSpider()
    
    # Thu thập dữ liệu
    if player_id:
        # Thu thập dữ liệu cho một cầu thủ cụ thể
        logger.info(f"Đang thu thập dữ liệu cho cầu thủ ID: {player_id}")
        player_data = {"id": player_id, "name": {"display": f"Player {player_id}"}}
        player_info = spider.scrape_player(player_data, season, season_id)
        
        if player_info:
            data = [player_info]
            logger.info(f"Đã thu thập thành công dữ liệu cho cầu thủ ID: {player_id}")
        else:
            data = []
            logger.warning(f"Không thể thu thập dữ liệu cho cầu thủ ID: {player_id}")
    else:
        # Thu thập dữ liệu cho toàn bộ mùa giải
        max_msg = f" (giới hạn {max_players} cầu thủ)" if max_players else ""
        logger.info(f"Đang thu thập dữ liệu cho tất cả cầu thủ trong mùa giải {season}{max_msg}")
        data = spider.scrape_season(season, max_players)
    
    # Lưu dữ liệu
    if data:
        # Lưu dạng JSON
        json_path = spider.save_data_json(data, season)
        logger.info(f"Đã lưu dữ liệu dạng JSON: {json_path}")
        
        # Lưu dạng CSV
        csv_path = spider.save_data_csv(data, season)
        logger.info(f"Đã lưu dữ liệu dạng CSV: {csv_path}")
        
        # Lưu chi tiết trận đấu dạng CSV
        match_csv_path = spider.save_match_details_csv(data, season)
        if match_csv_path:
            logger.info(f"Đã lưu dữ liệu chi tiết trận đấu dạng CSV: {match_csv_path}")
        
        logger.info(f"Tổng số cầu thủ đã thu thập: {len(data)}")
    else:
        logger.warning(f"Không thu thập được dữ liệu cầu thủ nào cho mùa {season}")
    
    logger.info(f"===== KẾT THÚC THU THẬP DỮ LIỆU NÂNG CAO CHO CẦU THỦ MÙA {season} =====")
    logger.info(f"Thời gian kết thúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 