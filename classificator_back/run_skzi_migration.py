#!/usr/bin/env python3
"""Создаёт таблицу skzi в базе данных."""
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

SQL = """
CREATE TABLE IF NOT EXISTS skzi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    equipment_id UUID NOT NULL UNIQUE REFERENCES equipment(id) ON DELETE CASCADE,
    registration_number VARCHAR NOT NULL UNIQUE,
    act_of_receiving_skzi VARCHAR,
    date_of_act_of_receiving TIMESTAMP,
    sertificate_number VARCHAR,
    end_date_of_sertificate TIMESTAMP,
    date_of_creation_skzi TIMESTAMP,
    nubmer_of_jornal VARCHAR,
    issued_to_whoom VARCHAR
);
ALTER TABLE skzi DROP COLUMN IF EXISTS name;
"""

if __name__ == "__main__":
    # Парсим URL: postgresql+asyncpg://user:pass@host/ -> host, user, pass
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
    print("Таблица skzi создана успешно.")
    cur.close()
    conn.close()
