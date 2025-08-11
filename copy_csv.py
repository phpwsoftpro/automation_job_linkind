import shutil
from pathlib import Path

# ✅ Sửa đường dẫn đúng với máy bạn
output_folder = Path("/Users/phamkhue/Downloads/savecsv")

csv_path = output_folder / "full_company_info.csv"
csv_copy_path = output_folder / "csvtest.csv"

try:
    shutil.copyfile(csv_path, csv_copy_path)
    print(f"✅ Đã nhân bản: {csv_path} ➜ {csv_copy_path}")
except FileNotFoundError:
    print("❌ Không tìm thấy file full_company_info.csv để nhân bản.")
