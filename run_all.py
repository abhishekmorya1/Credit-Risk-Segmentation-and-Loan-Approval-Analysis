# Runs all steps one after another
# Usage (from the project folder): python run_all.py
import subprocess
import sys

steps = [
    "scripts/01_data_cleaning.py",
    "scripts/02_eda_visualization.py",
    "scripts/03_load_to_sqlite.py",
    "scripts/04_export_for_powerbi.py",
]

for step in steps:
    print("\n--- Running", step, "---")
    result = subprocess.run([sys.executable, step])
    if result.returncode != 0:
        print("Stopped: error in", step)
        break
