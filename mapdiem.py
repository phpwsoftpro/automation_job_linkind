import pyautogui
import subprocess
import time
import os
import csv
import pyperclip
from pathlib import Path

# === Cấu hình ===
image_folder = Path("//Users/phamkhue/Downloads/save")
output_csv_path = Path("/Users/phamkhue/Downloads/Savecsv/linkedin_urls.csv")

WAIT_SHORT = 0.15
WAIT_MEDIUM = 0.4
WAIT_LONG = 1.0

BASE_TAB_COUNT = 12
TAB_INCREMENT = 2
JOB_LIST_AREA = (100, 207)
NEXT_BUTTON_COORDS = (612, 729)


def activate_chrome():
    subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'])
    time.sleep(WAIT_MEDIUM)

def copy_linkedin_url():
    pyautogui.keyDown('command')
    pyautogui.press('l')
    pyautogui.keyUp('command')
    time.sleep(WAIT_SHORT)

    pyautogui.keyDown('command')
    pyautogui.press('c')
    pyautogui.keyUp('command')
    time.sleep(WAIT_SHORT)

    return pyperclip.paste().strip()

def process_jobs_on_page(start_index, writer, image_index_start=1, jobs_to_process=25):
    job_tab_counts = [BASE_TAB_COUNT + i * TAB_INCREMENT for i in range(jobs_to_process)]
    for i, tab_count in enumerate(job_tab_counts):
        job_number = start_index + i + 1
        image_index = image_index_start + i
        print(f"[Job {job_number}] Đang xử lý...")

        pyautogui.moveTo(*JOB_LIST_AREA)
        pyautogui.click()
        time.sleep(WAIT_SHORT)

        for _ in range(tab_count):
            pyautogui.press('tab')
            time.sleep(0.025)

        pyautogui.press('enter')
        time.sleep(WAIT_MEDIUM)

        # Copy URL
        url = copy_linkedin_url()
        if not url.startswith("http"):
            url = "❌ Không lấy được URL"
        print(f"🔗 {url}")

        # Chụp ảnh: command + shift + k
        pyautogui.keyDown('command')
        pyautogui.keyDown('shift')
        pyautogui.press('k')
        pyautogui.keyUp('shift')
        pyautogui.keyUp('command')
        time.sleep(20)

        # Ghi lại danh sách ảnh trước khi lưu
        image_files_before = set(image_folder.glob("*.png"))

        # Lưu ảnh: command + shift + s
        pyautogui.keyDown('command')
        pyautogui.keyDown('shift')
        pyautogui.press('s')
        pyautogui.keyUp('shift')
        pyautogui.keyUp('command')
        time.sleep(2)

        # Luôn đóng tab ảnh sau khi lưu
        pyautogui.keyDown('command')
        pyautogui.press('w')
        pyautogui.keyUp('command')
        time.sleep(2)
        print("✅ Đã đóng tab ảnh.")

        # Quay lại tab LinkedIn
        pyautogui.keyDown('command')
        pyautogui.press('1')
        pyautogui.keyUp('command')
        time.sleep(WAIT_SHORT)

        # Đổi tên ảnh mới nhất
        image_files_after = set(image_folder.glob("*.png"))
        new_images = image_files_after - image_files_before
        if new_images:
            latest_img = max(new_images, key=os.path.getmtime)
            new_name = f"pic{image_index}{latest_img.suffix}"
            new_path = image_folder / new_name
            try:
                latest_img.rename(new_path)
                source = f"pic{image_index}.txt"
                print(f"✅ Đổi tên ảnh: {latest_img.name} → {new_name}")
            except Exception as e:
                print(f"❌ Lỗi đổi tên {latest_img.name}: {e}")
                source = ""
        else:
            source = ""

        writer.writerow([url, source])

        pyautogui.moveTo(*JOB_LIST_AREA)
        pyautogui.click()
        time.sleep(WAIT_SHORT)

def go_to_next_page():
    print("\n➡️ Sang trang kế tiếp...")
    pyautogui.moveTo(*JOB_LIST_AREA)
    pyautogui.click()
    time.sleep(WAIT_SHORT)
    for _ in range(74):
        pyautogui.press('tab')
        time.sleep(0.025)
    pyautogui.moveTo(*NEXT_BUTTON_COORDS)
    pyautogui.click()
    time.sleep(3)

if __name__ == "__main__":
    total_jobs_to_process = 5

    activate_chrome()
    image_folder.mkdir(parents=True, exist_ok=True)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_csv_path, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["url_linkedin", "source"])

        jobs_done = 0
        page = 0

        while jobs_done < total_jobs_to_process:
            remaining = total_jobs_to_process - jobs_done
            count = min(25, remaining)
            print(f"\n📄 Trang {page + 1} - xử lý {count} job...")
            process_jobs_on_page(jobs_done, writer, image_index_start=jobs_done + 1, jobs_to_process=count)
            jobs_done += count
            page += 1
            if jobs_done < total_jobs_to_process:
                go_to_next_page()

    print(f"\n✅ Đã hoàn tất xử lý {total_jobs_to_process} job.")
    print(f"📄 File đã lưu: {output_csv_path}")

    # Quay về ChatGPT: command + 2
    pyautogui.keyDown('command')
    pyautogui.press('2')
    pyautogui.keyUp('command')
    time.sleep(WAIT_SHORT)
