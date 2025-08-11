import pyautogui
import time
import subprocess

# (Tùy chọn) Mở Chrome nếu chưa chạy
subprocess.Popen(["open", "-a", "Google Chrome"])

# Đợi 5 giây để bạn kịp chuyển sang tab mong muốn trong Chrome
print("Bạn có 5 giây để chuyển sang Chrome...")
time.sleep(5)

# Gửi tổ hợp phím Option + Shift + 1
pyautogui.hotkey('option', 'shift', '1')  # ⌥⇧1
