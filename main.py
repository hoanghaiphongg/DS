#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys
from datetime import datetime

# Thêm thư mục gốc vào path để import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scrapers.match_spider import MatchSpider
from scrapers.player_spider import PlayerSpider
from config import LOG_FORMAT, LOG_FILE, SEASONS

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
    parser = argparse.ArgumentParser(description='Thu thập dữ liệu bóng đá từ Premier League API')
    parser.add_argument('--type', choices=['match', 'player', 'all'], default='all',
                        help='Loại dữ liệu cần thu thập: match, player, hoặc all (mặc định)')
    parser.add_argument('--season', choices=list(SEASONS.keys()), default='2023-2024',
                        help='Mùa giải cần thu thập (mặc định: 2023-2024)')
    parser.add_argument('--all-seasons', action='store_true',
                        help='Thu thập dữ liệu cho tất cả các mùa giải')
    parser.add_argument('--format', choices=['json', 'csv', 'both'], default='both',
                        help='Định dạng file output (mặc định: both - cả JSON và CSV)')
    
    return parser.parse_args()

def main():
    """Hàm chính để chạy thu thập dữ liệu"""
    args = parse_args()
    
    # Xác định danh sách mùa giải cần thu thập
    seasons = list(SEASONS.keys()) if args.all_seasons else [args.season]
    
    if args.type in ['match', 'all']:
        match_spider = MatchSpider()
        for season in seasons:
            logger.info(f"Đang thu thập dữ liệu trận đấu mùa {season}")
            matches_data = match_spider.scrape_season(season)
            
            if args.format in ['json', 'both']:
                json_path = match_spider.save_data_json(matches_data, season)
                logger.info(f"Đã lưu dữ liệu JSON trận đấu mùa {season}")
            
            if args.format in ['csv', 'both']:
                csv_path = match_spider.save_data_csv(matches_data, season)
                logger.info(f"Đã lưu dữ liệu CSV trận đấu mùa {season}")
    
    if args.type in ['player', 'all']:
        player_spider = PlayerSpider()
        for season in seasons:
            logger.info(f"Đang thu thập dữ liệu cầu thủ mùa {season}")
            players_data = player_spider.scrape_season(season)
            
            if args.format in ['json', 'both']:
                json_path = player_spider.save_data_json(players_data, season)
                logger.info(f"Đã lưu dữ liệu JSON cầu thủ mùa {season}")
            
            if args.format in ['csv', 'both']:
                csv_path = player_spider.save_data_csv(players_data, season)
                logger.info(f"Đã lưu dữ liệu CSV cầu thủ mùa {season}")
    
    logger.info("Thu thập dữ liệu hoàn tất!")

if __name__ == "__main__":
    main() 