import pyautogui
import time

print("🕒 Bạn có 5 giây để di chuyển chuột đến vị trí mong muốn...")
time.sleep(5)

x, y = pyautogui.position()
print(f"📍 Tọa độ chuột sau 5 giây: ({x}, {y})")
