# modules/todo.py
import json
import os

FILENAME = "data/todo.json"

def load_tasks():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    os.makedirs("data", exist_ok=True)
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
