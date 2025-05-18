import pandas as pd
import os
import sys

def merge_specific_files(file1, file2, output_file):
    """
    Ghép 2 file CSV cụ thể theo chiều dọc, với file1 nằm trên đầu
    
    Args:
        file1 (str): File đầu tiên (sẽ nằm trên)
        file2 (str): File thứ hai (sẽ nằm dưới)
        output_file (str): Đường dẫn file đầu ra
    """
    # Kiểm tra xem các file có tồn tại không
    if not os.path.exists(file1):
        print(f"❌ File {file1} không tồn tại!")
        return False
        
    if not os.path.exists(file2):
        print(f"❌ File {file2} không tồn tại!")
        return False
    
    print(f"Đang ghép nối 2 file CSV:")
    
    # Đọc file 1 (mùa 2024-2025)
    try:
        print(f"1. Đọc file: {os.path.basename(file1)}")
        df1 = pd.read_csv(file1)
        print(f"   - Số dòng: {len(df1):,}")
    except Exception as e:
        print(f"❌ Lỗi khi đọc file {os.path.basename(file1)}: {str(e)}")
        return False
    
    # Đọc file 2 (các mùa khác)
    try:
        print(f"2. Đọc file: {os.path.basename(file2)}")
        df2 = pd.read_csv(file2)
        print(f"   - Số dòng: {len(df2):,}")
    except Exception as e:
        print(f"❌ Lỗi khi đọc file {os.path.basename(file2)}: {str(e)}")
        return False
    
    # Ghép các DataFrame
    print("\nĐang ghép nối 2 file...")
    try:
        # Sử dụng ignore_index=True để đánh số lại các dòng
        combined_df = pd.concat([df1, df2], ignore_index=True)
        
        # Lưu kết quả
        combined_df.to_csv(output_file, index=False)
        
        print(f"\n✅ Đã ghép nối thành công 2 file CSV và lưu vào {output_file}")
        print(f"   - Số dòng file 1: {len(df1):,}")
        print(f"   - Số dòng file 2: {len(df2):,}")
        print(f"   - Tổng số dòng: {len(df1) + len(df2):,}")
        print(f"   - Số dòng sau khi ghép: {len(combined_df):,}")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi khi ghép nối file CSV: {str(e)}")
        return False

if __name__ == "__main__":
    # Thư mục chứa file CSV
    data_dir = "data"
    
    # Đường dẫn đến 2 file cụ thể
    file1 = os.path.join(data_dir, "all_matches_2024_2025.csv")  # Mùa 2024-2025 (sẽ nằm trên)
    file2 = os.path.join(data_dir, "all_seasons_20250518_055804.csv")  # Các mùa khác (sẽ nằm dưới)
    
    # File đầu ra
    output_file = os.path.join(data_dir, "all_seasons_combined.csv")
    
    # Thực hiện ghép nối
    success = merge_specific_files(file1, file2, output_file)
    
    if success:
        print(f"\nBạn có thể tìm thấy file kết quả tại: {output_file}")
    else:
        print("\nGhép nối không thành công. Vui lòng kiểm tra lại các thông báo lỗi.")
        
    sys.exit(0 if success else 1) 