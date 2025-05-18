# EPL Data Collector

Dự án thu thập dữ liệu Premier League bao gồm thông tin trận đấu và cầu thủ.

## Cài đặt

1. Cài đặt Python 3.8 trở lên
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## Cấu trúc dự án

```
epl_data_collector/
├── data/                  # Thư mục chứa dữ liệu đã thu thập
├── scrapers/             # Chứa các spider thu thập dữ liệu
│   ├── match_spider.py   # Spider thu thập dữ liệu trận đấu
│   └── player_spider.py  # Spider thu thập dữ liệu cầu thủ
├── utils/                # Các tiện ích và hàm hỗ trợ
├── config.py            # Cấu hình dự án
└── main.py             # File chính để chạy thu thập dữ liệu
```

## Sử dụng

1. Thu thập dữ liệu trận đấu:
```bash
python main.py --type match
```

2. Thu thập dữ liệu cầu thủ:
```bash
python main.py --type player
```

## Dữ liệu thu thập

### Dữ liệu trận đấu
- Thông tin cơ bản: ID, ngày giờ, sân vận động
- Thông tin đội bóng: Đội hình, thay người
- Thống kê trận đấu: Sút, sút trúng đích, kiểm soát bóng,...
- Sự kiện: Bàn thắng, thẻ đỏ, thẻ vàng,...

### Dữ liệu cầu thủ
- Thông tin cơ bản: ID, tên, vị trí, quốc tịch
- Thống kê mùa giải: Số trận, bàn thắng, kiến tạo,...
- Thông tin chuyển nhượng
- Lịch sử thi đấu 