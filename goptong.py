import csv
import os

file_main = "/Users/phamkhue/Downloads/savecsv/csvtest.csv"
file_linkedin = "/Users/phamkhue/Downloads/savecsv/linkedin_urls.csv"
file_output = "/Users/phamkhue/Downloads/savecsv/merged_output.csv"

# === Đọc file chính ===
with open(file_main, newline='', encoding='utf-8-sig') as f_main:
    main_reader = list(csv.DictReader(f_main))

# === Đọc LinkedIn URL và chuẩn hóa đuôi .txt
with open(file_linkedin, newline='', encoding='utf-8-sig') as f_url:
    url_reader = csv.DictReader(f_url)
    url_map = {}
    for row in url_reader:
        raw_source = row.get('source', '').strip()
        norm_source = os.path.splitext(raw_source)[0]  # bỏ .txt
        url_map[norm_source] = row.get('url_linkedin', '').strip()

# === Gán linkedin_url cho từng dòng
for row in main_reader:
    raw_source = row.get('source', '').strip()
    norm_source = os.path.splitext(raw_source)[0]  # bỏ .png
    row['linkedin_url'] = url_map.get(norm_source, '')

    # ❌ Xóa cột check_valid nếu có
    if 'check_valid' in row:
        del row['check_valid']

# === Ghi file kết quả
if main_reader:
    fieldnames = list(main_reader[0].keys())
    if 'check_valid' in fieldnames:
        fieldnames.remove('check_valid')  # loại khỏi header nếu có

    with open(file_output, mode='w', newline='', encoding='utf-8-sig') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(main_reader)

print(f"✅ Đã gộp xong! File đã lưu tại: {file_output}")
