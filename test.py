import pyautogui
import time

# Tọa độ bạn muốn di chuột đến
x = 444
y = 560

print("⏳ Đợi 2 giây rồi di chuột...")
time.sleep(5)

# Di chuột đến tọa độ (x, y)
pyautogui.moveTo(x, y, duration=0.5)  # duration giúp chuột di chuyển mượt hơn
print(f"✅ Đã di chuột đến tọa độ ({x}, {y})")
