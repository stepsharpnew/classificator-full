#!/usr/bin/env python3
"""Добавляет колонку is_skzi_admin в таблицу users."""
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

SQL = """
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_skzi_admin BOOLEAN DEFAULT FALSE;
"""

if __name__ == "__main__":
    server = os.getenv("POSTGRESQL_SERVER", "")
    if server.startswith("postgresql+asyncpg://"):
        server = server.replace("postgresql+asyncpg://", "")
    if "@" in server:
        auth, host = server.split("@", 1)
        user, password = auth.split(":", 1)
    else:
        host = "localhost"
        user = os.getenv("POSTGRESQL_USER", "classificator")
        password = os.getenv("POSTGRESQL_PASS", "classificator")
    host = host.rstrip("/").split("/")[0]
    db = os.getenv("POSTGRESQL_DB", "classificator")

    conn_str = f"postgresql://{user}:{password}@{host}/{db}"
    print(f"Подключение к {host}/{db}...")
    conn = psycopg2.connect(conn_str)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(SQL)
    print("Колонка is_skzi_admin добавлена успешно.")
    cur.close()
    conn.close()
