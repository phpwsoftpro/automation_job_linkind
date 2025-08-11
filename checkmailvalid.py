#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import csv
import pyautogui
import logging
import pyperclip
from pathlib import Path

def switch_to_chrome_tab(tab_index: int = 3, wait: float = 1.5):
    applescript = f'''
    tell application "Google Chrome"
        activate
        if (count of windows) = 0 then return
        try
            set active tab index of front window to {tab_index}
        end try
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])
    time.sleep(wait)

switch_to_chrome_tab(3)

CSV_PATH       = Path("/Users/phamkhue/Downloads/savecsv/full_company_info.csv")
CSV_OUT_PATH   = Path("/Users/phamkhue/Downloads/savecsv/csvtest.csv")
TAB_COUNT      = 7
RESET_POS      = (46,167)
RESULT_POS     = (444,560)
WAIT_BEFORE        = 2
WAIT_AFTER_SUBMIT  = 30
WAIT_AFTER_CLICK   = 5
TYPE_INTERVAL      = 0.10
COPY_DELAY         = 5.0

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)

logging.warning("⚠️ Hãy tắt Caps Lock trước khi chạy script!")
time.sleep(WAIT_BEFORE)

def get_result_by_right_click_and_copy() -> str:
    pyperclip.copy("")
    pyautogui.click(*RESULT_POS, button='right')
    time.sleep(COPY_DELAY)

    pyautogui.keyDown('command')
    pyautogui.press('c')
    pyautogui.keyUp('command')

    time.sleep(COPY_DELAY)
    text = pyperclip.paste().lower().strip()
    logging.debug("📋 Clipboard:\n%s", text)

    if "invalid" in text:
        return "Invalid"
    if "valid" in text:
        return "Valid"
    return "Unknown"

def load_emails(path: Path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

emails = load_emails(CSV_PATH)
if not emails:
    logging.error("❌ Không có email nào trong file CSV.")
    exit(1)

results = []
validated_count = 0

for idx, row in enumerate(emails, 1):
    email = row.get("email", "").strip()

    if not email or email.lower() == "email":
        logging.info("❌ (%d/%d) Không có email – đánh dấu là 'no email'", idx, len(emails))
        row['check_mail'] = "no email"
        results.append(row)
        continue

    logging.info("➡️ (%d/%d) Checking: %s", idx, len(emails), email)

    # ESC để đóng popup
    pyautogui.press('esc')
    time.sleep(0.5)

    # TAB tới ô nhập
    for _ in range(TAB_COUNT):
        pyautogui.press('tab')
        time.sleep(0.3)

    pyautogui.write(email, interval=TYPE_INTERVAL)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(WAIT_AFTER_SUBMIT)

    result = get_result_by_right_click_and_copy()
    row['check_mail'] = result
    results.append(row)

    # Reset form
    pyautogui.click(*RESET_POS)
    time.sleep(WAIT_AFTER_CLICK)

    # Sau mỗi 5 job valid → reload
    if result in ("Valid", "Invalid", "Unknown"):
        validated_count += 1
        if validated_count % 5 == 0:
            logging.info("🔄 Đã kiểm tra 5 email – reload lại để tránh spam")

            # Command + R (reload)
            pyautogui.keyDown('command')
            pyautogui.press('r')
            pyautogui.keyUp('command')

            time.sleep(7)
            switch_to_chrome_tab(3)
            time.sleep(2)

# === Ghi kết quả ===
if results:
    with CSV_OUT_PATH.open(mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    logging.info("✅ Xong! Kết quả lưu tại: %s", CSV_OUT_PATH)
else:
    logging.warning("⚠️ Không có kết quả để ghi.")
