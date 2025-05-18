import json
import csv
import traceback

def extract_player_names(player_list):
    """Chuyển danh sách cầu thủ thành danh sách tên (hiển thị)"""
    if not player_list:
        return []
    return [p.get("name", {}).get("display", "") for p in player_list]

def parse_match_data(match, index=None):
    """Phân tích dữ liệu trận đấu, với xử lý lỗi cẩn thận"""
    try:
        if not match:
            print(f"⚠️ Bỏ qua trận đấu thứ {index}: Dữ liệu trận đấu trống")
            return None
            
        # ==== A. Thông tin cơ bản ====
        # Kiểm tra và cung cấp giá trị mặc định khi clock là None
        clock = match.get("clock") or {}
        
        row = {
            "match_id": match.get("id"),
            "match_date": match.get("kick_off", {}).get("label") if match.get("kick_off") else None,
            "kickoff_millis": match.get("kick_off", {}).get("millis") if match.get("kick_off") else None,
            "stadium": match.get("ground", {}).get("name") if match.get("ground") else None,
            "city": match.get("ground", {}).get("city") if match.get("ground") else None,
            "duration_secs": clock.get("secs"),
            "ht_home_score": match.get("halfTimeScore", {}).get("homeScore") if match.get("halfTimeScore") else None,
            "ht_away_score": match.get("halfTimeScore", {}).get("awayScore") if match.get("halfTimeScore") else None,
        }

        # ==== B. Thông tin 2 đội ====
        teams = match.get("teams", [])
        if len(teams) != 2:
            print(f"⚠️ Bỏ qua trận đấu thứ {index}: Không đủ 2 đội (chỉ có {len(teams)} đội)")
            return None  # Bỏ qua nếu dữ liệu không đủ 2 đội

        home_team = teams[0] if teams and len(teams) > 0 else {}
        away_team = teams[1] if teams and len(teams) > 1 else {}
        
        # Kiểm tra xem home_team và away_team có phải là dict không
        if not isinstance(home_team, dict) or not isinstance(away_team, dict):
            print(f"⚠️ Bỏ qua trận đấu thứ {index}: Dữ liệu đội không hợp lệ")
            return None
            
        # Kiểm tra cẩn thận các trường dữ liệu đội
        home_team_obj = home_team.get("team", {}) if home_team else {}
        away_team_obj = away_team.get("team", {}) if away_team else {}
        
        row.update({
            "home_team_name": home_team_obj.get("name") if home_team_obj else None,
            "home_team_id": home_team_obj.get("id") if home_team_obj else None,
            "home_score": home_team.get("score"),
            "away_team_name": away_team_obj.get("name") if away_team_obj else None,
            "away_team_id": away_team_obj.get("id") if away_team_obj else None,
            "away_score": away_team.get("score"),
        })

        # Kiểm tra ID của đội nhà và đội khách có tồn tại không
        home_id = row.get("home_team_id")
        away_id = row.get("away_team_id")
        
        if not home_id or not away_id:
            print(f"⚠️ Trận đấu thứ {index}: Thiếu ID đội nhà hoặc đội khách, bỏ qua thống kê chi tiết")
            return row  # Vẫn trả về thông tin cơ bản nếu không có ID đội

        # ==== C. Lấy thống kê ====
        stats = match.get("stats", {})
        if not stats:
            # Trận đấu không có thống kê, vẫn tiếp tục với các thông tin khác
            print(f"⚠️ Trận đấu thứ {index}: Không có thống kê")
        
        # Xử lý an toàn hơn với các trường hợp có thể None
        home_stats_obj = stats.get(str(home_id), {}) if stats and home_id else {}
        away_stats_obj = stats.get(str(away_id), {}) if stats and away_id else {}
        
        home_stats_list = home_stats_obj.get("M", []) if home_stats_obj else []
        away_stats_list = away_stats_obj.get("M", []) if away_stats_obj else []
        
        home_stats = {}
        for s in home_stats_list:
            if isinstance(s, dict) and "name" in s and "value" in s:
                home_stats[s["name"]] = s["value"]
                
        away_stats = {}
        for s in away_stats_list:
            if isinstance(s, dict) and "name" in s and "value" in s:
                away_stats[s["name"]] = s["value"]

        for key, value in home_stats.items():
            row[f"home_{key}"] = value
        for key, value in away_stats.items():
            row[f"away_{key}"] = value

        # ==== D. Lấy đội hình đá chính và dự bị ====
        team_lists = match.get("teamLists", []) or []
        
        # Tìm đội hình theo ID, xử lý an toàn hơn
        home_list = None
        away_list = None
        
        if home_id:
            for team_list in team_lists:
                if isinstance(team_list, dict) and team_list.get("teamId") == home_id:
                    home_list = team_list
                    break
                    
        if away_id:
            for team_list in team_lists:
                if isinstance(team_list, dict) and team_list.get("teamId") == away_id:
                    away_list = team_list
                    break

        home_starting = extract_player_names(home_list.get("lineup", [])) if home_list else []
        home_subs = extract_player_names(home_list.get("substitutes", [])) if home_list else []
        away_starting = extract_player_names(away_list.get("lineup", [])) if away_list else []
        away_subs = extract_player_names(away_list.get("substitutes", [])) if away_list else []

        for i in range(11):
            row[f"home_starting_{i+1}_name"] = home_starting[i] if i < len(home_starting) else ""
            row[f"away_starting_{i+1}_name"] = away_starting[i] if i < len(away_starting) else ""

        for i in range(9):
            row[f"home_sub_{i+1}_name"] = home_subs[i] if i < len(home_subs) else ""
            row[f"away_sub_{i+1}_name"] = away_subs[i] if i < len(away_subs) else ""

        return row
        
    except Exception as e:
        print(f"❌ Lỗi xử lý trận đấu thứ {index}: {str(e)}")
        traceback.print_exc()
        return None

# ==== MAIN ====
# Thêm xử lý lỗi khi mở file và đọc json
try:
    input_path = "data/matches_2024-2025_20250518_071839.json"     # <== Thay bằng đường dẫn file của bạn
    output_path = "data/all_matches_2024_2025.csv"

    print(f"Đang đọc dữ liệu từ file: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        matches = json.load(f)

    print(f"Đã đọc {len(matches)} trận đấu, đang xử lý...")
    rows = []
    for i, match in enumerate(matches):
        try:
            row = parse_match_data(match, i)
            if row:
                rows.append(row)
        except Exception as e:
            print(f"❌ Lỗi khi xử lý trận đấu thứ {i}: {str(e)}")
            
    print(f"Đã xử lý thành công {len(rows)}/{len(matches)} trận đấu")

    if not rows:
        print("❌ Không có dữ liệu trận đấu nào để ghi vào file CSV")
        exit(1)

    # Lấy toàn bộ tên cột
    all_keys = set()
    for row in rows:
        all_keys.update(row.keys())
    fieldnames = sorted(all_keys)

    print(f"Đang ghi dữ liệu vào file CSV: {output_path}")
    with open(output_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("✅ Đã tạo file CSV:", output_path)
    
except FileNotFoundError:
    print(f"❌ Lỗi: Không tìm thấy file {input_path}")
    print("Hãy kiểm tra lại đường dẫn file JSON đầu vào.")
    
except json.JSONDecodeError:
    print(f"❌ Lỗi: File JSON không hợp lệ, không thể đọc dữ liệu từ {input_path}")
    
except Exception as e:
    print(f"❌ Lỗi không xác định: {str(e)}")
    traceback.print_exc()
