import pandas as pd
import re

# ==== CẤU HÌNH ĐƯỜNG DẪN FILE ====
path = "/Users/phamkhue/Downloads/Savecsv/merged_output.csv"

# ==== HÀM XỬ LÝ ====
def split_candidates(text: str):
    if not isinstance(text, str):
        text = "" if pd.isna(text) else str(text)
    parts = re.split(r"[;,/|\s]+", text)
    return [p.strip() for p in parts if p and p.strip()]

# ==== ĐỌC FILE CSV ====
for enc in ["utf-8-sig", "utf-8", "latin1"]:
    try:
        df = pd.read_csv(path, encoding=enc)
        break
    except Exception:
        pass

df.columns = [str(c).strip() for c in df.columns]

# ==== XÁC ĐỊNH CỘT EMAIL ====
possible_email_cols = [c for c in df.columns if any(k in c.lower() for k in ["email", "e-mail", "mail"])]
email_col = possible_email_cols[0] if possible_email_cols else None

email_regex_full = re.compile(r"^(?:[A-Z0-9._%+-]+)@(?:[A-Z0-9.-]+)\.[A-Z]{2,}$", re.IGNORECASE)
email_regex_find = re.compile(r"(?:[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", re.IGNORECASE)

# ==== ĐẾM ====
total_jobs = len(df)
valid_count = 0
invalid_count = 0
unknown_count = 0
rows_no_email = 0

if email_col is not None:
    for val in df[email_col]:
        candidates = split_candidates(val)
        if not candidates:
            rows_no_email += 1
            continue
        row_has_valid = False
        for c in candidates:
            if email_regex_full.match(c):
                valid_count += 1
                row_has_valid = True
            elif c:  # sai format email
                invalid_count += 1
            else:
                unknown_count += 1
        if not row_has_valid:
            rows_no_email += 1
else:
    text_cols = [c for c in df.columns if df[c].dtype == "object"]
    for _, row in df[text_cols].iterrows():
        combined = " ".join([str(row[c]) for c in text_cols if pd.notna(row[c])])
        found = email_regex_find.findall(combined)
        if found:
            valid_count += len(found)
        else:
            rows_no_email += 1

# ==== IN KẾT QUẢ ====
print(f"Tổng số job: {total_jobs}")
print(f"Tổng số mail tìm được: {valid_count + invalid_count + unknown_count}")
print(f"Tổng số mail valid: {valid_count}")
print(f"Tổng số mail invalid: {invalid_count}")
print(f"Tổng số mail unknown: {unknown_count}")
print(f"Số job không có email: {rows_no_email}")
print(f"Lấy được cuối : {valid_count} / {total_jobs} ≈ {valid_count/total_jobs*100:.1f}% ✅")
