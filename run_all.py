import subprocess
import sys
import os

# Scripts will be run in this fixed order
order = [
    "mapdiem.py",         # 1) capture LinkedIn
    "linkin.py",          # 2) ask ChatGPT
    "copy_csv.py",        # 3) duplicate CSV
    "checkmailvalid.py",  # 4) filter mail
    "goptong.py",         # 5) gop tat ca lai
    "report.py"           # 5) report
]

for script in order:
    path = os.path.join(os.path.dirname(__file__), script)
    print(f"\n===== Running {script} =====")
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("--- errors ---")
        print(result.stderr)
