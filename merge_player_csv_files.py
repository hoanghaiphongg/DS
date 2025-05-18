import os
import csv
import pandas as pd
from datetime import datetime

def merge_csv_files(input_files, output_file):
    """
    Gộp nhiều file CSV theo chiều dọc (vertical concatenation)
    
    Args:
        input_files (list): Danh sách đường dẫn đến các file CSV đầu vào
        output_file (str): Đường dẫn đến file CSV kết quả
    """
    # Kiểm tra xem tất cả các file đầu vào có tồn tại không
    for file_path in input_files:
        if not os.path.exists(file_path):
            print(f"⚠️ File không tồn tại: {file_path}")
            return
    
    print(f"Bắt đầu gộp {len(input_files)} file...")
    
    # Sử dụng pandas để đọc và gộp file
    dataframes = []
    
    for file_path in input_files:
        try:
            # Đọc file CSV
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # Thêm thông tin nguồn (source) nếu chưa có trong dữ liệu
            if 'source_file' not in df.columns:
                df['source_file'] = os.path.basename(file_path)
            
            dataframes.append(df)
            print(f"✓ Đã đọc file: {file_path} - {len(df)} dòng")
        except Exception as e:
            print(f"⚠️ Lỗi khi đọc file {file_path}: {str(e)}")
    
    if not dataframes:
        print("❌ Không có dữ liệu để gộp.")
        return
    
    # Gộp tất cả dataframe
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    # Tạo thư mục đích nếu chưa tồn tại
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Lưu vào file kết quả
    merged_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n✅ Đã gộp {len(dataframes)} file thành công!")
    print(f"✅ Tổng số dòng: {len(merged_df)}")
    print(f"✅ File kết quả: {output_file}")

if __name__ == "__main__":
    # Danh sách các file cần gộp
    input_files = [
        "data/data_csv/player/players_2021_2022.csv",
        "data/data_csv/player/players_2022_2023.csv",
        "data/data_csv/player/players_2023_2024.csv",
        "data/data_csv/player/players_2024_2025.csv"
    ]
    
    # Tạo tên file đầu ra với timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/data_csv/player/all_players_merged_{timestamp}.csv"
    
    # Thực hiện gộp
    merge_csv_files(input_files, output_file) 