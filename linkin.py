#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import pyautogui
import pyperclip
import subprocess
import pandas as pd
from pathlib import Path

# ====== Cấu hình ======
image_folder = Path("/Users/phamkhue/Downloads/save")
output_folder = Path("/Users/phamkhue/Downloads/savecsv")
output_csv = output_folder / "full_company_info.csv"
duplicate_csv = output_folder / "trung_company.csv"

# ====== Prompts ======
prompt1 = (
    "Tìm tên của công ty xuất hiện trong ảnh.\n\n"
    "Chỉ trả lời tên công ty đó, không thêm thông tin khác. Nếu có nhiều tên công ty, hãy chọn công ty chính.\n\n"
    "Hãy trả lời tên công ty đó trong một code block (dùng ba dấu backtick ```)."
)

prompt2 = '''From the job image below, extract structured company and job information in exactly the 6 sections below.

Please answer in Vietnamese.

The output must strictly follow this format, using numbered sections exactly as shown below (with `1.`, `2.`, etc. at the beginning of each section). Do not use bullet points, markdown symbols (**), or any additional formatting.

The 6 required sections:

1. Website chính thức và email liên hệ của công ty (tìm trên Google nếu không có trong ảnh)
2. Techstack sử dụng trong JD
3. Job Description gồm: vị trí, trách nhiệm, yêu cầu
4. Văn phòng chính của công ty có ở các khu vực: Ấn Độ, Việt Nam, Đông Nam Á, Châu Phi, Nam Mỹ không?
5. Công việc này có phải là Intern, Trainee hay Volunteer không?
6. Công ty có thuộc nhóm: Human Resources, Staffing and Recruitment, Nonprofit Organization, Outsourcing and Offshoring không?

Wrap the entire response in a single code block using triple backticks.
'''

# ====== Helper ======
def copy_file_to_clipboard_mac(filepath: str):
    applescript = f'''
    set theFile to POSIX file "{filepath}" as alias
    tell application "Finder"
        activate
        select theFile
        delay 0.2
        tell application "System Events" to keystroke "c" using command down
    end tell
    delay 0.4
    tell application "Google Chrome" to activate
    '''
    subprocess.run(["osascript", "-e", applescript])
    time.sleep(0.6)

def safe_copy_last_message(max_retry=3, wait=1.2):
    """⌘⇧; để copy message cuối. Thử lại nếu clipboard rỗng."""
    for _ in range(max_retry):
        pyperclip.copy("")
        pyautogui.hotkey('command', 'shift', ';')
        time.sleep(wait)
        txt = pyperclip.paste().strip()
        if txt:
            return txt
    return ""

def extract_company_name(text: str) -> str:
    # Ưu tiên lấy trong code block
    m = re.search(r"```(?:\w*\n)?(.*?)```", text, re.DOTALL)
    if m:
        name = m.group(1).strip().splitlines()[0].strip()
        if name:
            return name
    # fallback: dòng đầu tiên có chữ
    for line in text.splitlines():
        s = line.strip().strip("#*-` ")
        if s:
            return s
    return "[Unknown Company]"

def extract_fields_from_txt_resilient(text):
    text = re.sub(r':contentReference\[.*?\]', '', text)
    blocks = {}
    pattern = r'(?P<index>\d)\.\s(.*?)(?=\n\d\.|\Z)'
    for match in re.finditer(pattern, text, re.DOTALL):
        idx = int(match.group("index"))
        blocks[idx] = match.group(0).strip()

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', blocks.get(1, ""))
    email = email_match.group(0).strip() if email_match else ""

    url = ""
    url_match = re.search(r'(https?://[^\s\)\]\"]+)', blocks.get(1, ""))
    if url_match:
        url = url_match.group(1).strip()
    else:
        domain_match = re.search(r'\b([\w\-]+\.(?:com|net|org|io|ai|co|biz|dev))\b', blocks.get(1, ""))
        if domain_match:
            url = f"https://{domain_match.group(1).strip()}"

    return {
        "email": email,
        "url cty": url,
        "Tech stack": blocks.get(2, ""),
        "jd": blocks.get(3, ""),
        "Văn phòng chính": blocks.get(4, ""),
        "Loại hình công việc": blocks.get(5, ""),
        "Nhóm ngành": blocks.get(6, "")
    }

def handle_one_image(image_path: Path, output_txt_path: Path):
    # Copy file ảnh vào clipboard rồi mở Chrome
    copy_file_to_clipboard_mac(str(image_path))

    # New chat
    pyautogui.hotkey('command', 'shift', 'o')
    time.sleep(1.2)

    # Focus khung chat
    pyautogui.hotkey('shift', 'esc')
    time.sleep(1.2)

    # Paste ảnh
    pyautogui.hotkey('command', 'v')
    time.sleep(2.0)

    # === Prompt 1: hỏi tên công ty ===
    pyperclip.copy(prompt1)
    pyautogui.hotkey('command', 'v')
    time.sleep(0.6)
    pyautogui.hotkey('shift', 'esc')
    time.sleep(0.6)
    pyautogui.press('enter')

    # Đợi 15s để có câu trả lời, rồi copy
    time.sleep(15.0)
    response1 = safe_copy_last_message()
    company_name = extract_company_name(response1) if response1 else "[Unknown Company]"
    print(f"🏷️ Company: {company_name}")

    # === Prompt 2: hỏi chi tiết ===
    pyperclip.copy(prompt2)
    pyautogui.hotkey('command', 'v')
    time.sleep(0.6)
    pyautogui.hotkey('shift', 'esc')
    time.sleep(0.6)
    pyautogui.press('enter')
    print("🟢 Prompt 2 sent.")

    # Đợi để model trả lời đầy đủ rồi copy
    time.sleep(30.0)
    final_response = safe_copy_last_message()
    if not final_response or len(final_response) < 30:
        print("❌ No useful response from Prompt 2.")
        return None, company_name

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(final_response)

    return final_response, company_name

# ====== MAIN ======
output_folder.mkdir(parents=True, exist_ok=True)

def extract_index(file: Path):
    m = re.search(r'pic(\d+)', file.stem, re.IGNORECASE)
    return int(m.group(1)) if m else float('inf')

image_files = sorted(
    (f for f in image_folder.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")),
    key=extract_index
)

rows = []
for idx, image_path in enumerate(image_files, start=1):
    txt_path = output_folder / image_path.with_suffix(".txt").name
    print(f"📸 ({idx}) Đang xử lý ảnh: {image_path.name}")

    final_response, company_name = None, "[Unknown Company]"
    for attempt in range(2):
        final_response, company_name = handle_one_image(image_path, txt_path)
        if final_response:
            break
        print(f"⚠️ Thử lại ảnh: {image_path.name} (lần {attempt+1})")

    if not final_response:
        print(f"❌ Bỏ qua ảnh: {image_path.name}")
        continue

    with open(txt_path, "r", encoding="utf-8") as f:
        parsed = extract_fields_from_txt_resilient(f.read())

    parsed["source"] = image_path.name
    parsed["company name"] = company_name
    rows.append(parsed)

# ====== Xuất CSV ======
df_all = pd.DataFrame(rows)

# 1) Lưu toàn bộ (kể cả trùng)
df_all.to_csv(duplicate_csv, index=False)
print(f"📂 Đã lưu toàn bộ dữ liệu (kể cả trùng) vào: {duplicate_csv}")

# 2) Lọc trùng theo company name, nhưng KHÔNG lọc các dòng company name rỗng
if "company name" not in df_all.columns:
    df_all["company name"] = ""

mask_nonempty = df_all["company name"].astype(str).str.strip() != ""
df_unique = pd.concat([
    df_all[~mask_nonempty],  # giữ nguyên dòng tên rỗng
    df_all[mask_nonempty].drop_duplicates(subset=["company name"], keep="first")
], ignore_index=True)

df_unique.to_csv(output_csv, index=False)
print(f"✅ Đã lưu dữ liệu đã lọc trùng theo company name vào: {output_csv}")
