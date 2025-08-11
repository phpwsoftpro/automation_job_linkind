import pandas as pd
import re

# ==== CẤU HÌNH ĐƯỜNG DẪN FILE ====
path = "/Users/phamkhue/Downloads/Savecsv/merged_output.csv"  # đổi nếu cần

# ==== HÀM PHỤ ====
def split_candidates(text: str):
    if not isinstance(text, str):
        text = "" if pd.isna(text) else str(text)
    parts = re.split(r"[;,/|\s]+", text)
    return [p.strip() for p in parts if p and p.strip()]

def load_csv_any_encoding(p):
    for enc in ["utf-8-sig", "utf-8", "latin1"]:
        try:
            return pd.read_csv(p, encoding=enc)
        except Exception:
            continue
    raise RuntimeError("Không đọc được CSV với các encoding thử sẵn.")

# ==== ĐỌC FILE ====
df = load_csv_any_encoding(path)
df.columns = [str(c).strip() for c in df.columns]
total_jobs = len(df)

# ==== KHỞI TẠO BIẾN ĐẾM ====
valid_count = invalid_count = unknown_count = rows_no_email = 0

# ==== ƯU TIÊN DÙNG CỘT check_mail (nếu có) ====
check_col = None
for c in df.columns:
    if c.strip().lower() == "check_mail":
        check_col = c
        break

if check_col is not None:
    s = df[check_col].fillna("").astype(str).str.strip().str.lower()

    valid_count   = (s == "valid").sum()
    invalid_count = (s == "invalid").sum()
    unknown_count = (s == "unknown").sum()
    rows_no_email = s.isin(["no email", "noemail", ""]).sum()

else:
    # ---- Fallback: không có check_mail -> dựa vào cột email bằng regex ----
    possible_email_cols = [c for c in df.columns if any(k in c.lower() for k in ["email", "e-mail", "mail"])]
    email_col = possible_email_cols[0] if possible_email_cols else None

    email_regex_full = re.compile(r"^(?:[A-Z0-9._%+-]+)@(?:[A-Z0-9.-]+)\.[A-Z]{2,}$", re.IGNORECASE)
    if email_col is not None:
        for val in df[email_col]:
            candidates = split_candidates(val)
            if not candidates:
                rows_no_email += 1
                continue
            valids = [c for c in candidates if email_regex_full.fullmatch(c)]
            invalids = [c for c in candidates if c and not email_regex_full.fullmatch(c)]
            valid_count += len(valids)
            invalid_count += len(invalids)
        # Fallback này không xác định "unknown"
    else:
        # Không có cột email -> coi như không tìm thấy email ở từng dòng
        rows_no_email = total_jobs

# ==== TÍNH & IN KẾT QUẢ ====
found_total = valid_count + invalid_count + unknown_count
pct = (valid_count / total_jobs * 100) if total_jobs else 0.0

print(f"Tổng số job: {total_jobs}")
print(f"Tổng số mail tìm được: {found_total}")
print(f"Tổng số mail valid: {valid_count}")
print(f"Tổng số mail invalid: {invalid_count}")
print(f"Tổng số mail unknown: {unknown_count}")
print(f"Số job không có email: {rows_no_email}")

# <-- CHỈ SỬA DÒNG NÀY
print(f"Lấy được cuối : {valid_count} email hợp lệ ✅  ({pct:.1f}% trên tổng job)")
