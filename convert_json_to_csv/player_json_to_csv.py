import json
import csv
import os

def convert_json_to_csv(json_file_path, output_csv_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        players = json.load(f)

    processed_players = []
    all_keys = set()

    for player in players:
        processed = {}
        for k, v in player.items():
            # Loại bỏ tiền tố 'stat_' nếu có
            clean_key = k[5:] if k.startswith("stat_") else k
            processed[clean_key] = v
            all_keys.add(clean_key)
        processed_players.append(processed)

    # Ưu tiên thứ tự cột cơ bản
    preferred_order = [
        'player_id', 'name', 'first_name', 'last_name', 'season', 'position',
        'shirt_num', 'nationality', 'age', 'team_name', 'team_short_name',
        'mins_played', 'goals', 'assists', 'clean_sheets'
    ]
    all_keys = list(sorted(all_keys - set(preferred_order)))
    fieldnames = preferred_order + all_keys

    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for player in processed_players:
            writer.writerow(player)

    print(f"✅ Đã tạo file CSV: {output_csv_path}")

# ==== CÁCH DÙNG ====
# Bạn thay đường dẫn tương ứng nếu muốn xử lý file khác
convert_json_to_csv(
    json_file_path='data\players_enhanced_2021_2022_20250518_122704.json',
    output_csv_path='data/players_2021_2022.csv'
)
