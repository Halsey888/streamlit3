# modules/db_manager.py
import sqlite3
import os
import json
import datetime

DB_PATH = "database/novel_chat.db"

def init_db():
    """初始化資料庫與資料表"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_message(role: str, content: str):
    """儲存單筆訊息至資料庫"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (role, content) VALUES (?, ?)', (role, content))
    conn.commit()
    conn.close()

def get_history() -> list:
    """取得所有對話歷史"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT role, content FROM messages ORDER BY id ASC')
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]

def export_to_json() -> str:
    """將資料庫內容匯出為 JSON 文件，返回檔案名稱"""
    history = get_history()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"novel_backup_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    return filename