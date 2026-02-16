from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import uuid
from models import Base

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))) # Добавляем корень проекта в sys.path

from passlib.context import CryptContext
hasher = CryptContext(schemes=['sha256_crypt'])


import asyncio
if __name__=='__main__':


    CONNECTION = 'postgresql+psycopg2://classificator:classificator@192.168.1.35/classificator'
    engine = create_engine(CONNECTION)

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS ltree"))    
    Base.metadata.create_all(engine)

    # Миграция: добавить колонку staff_number в equipment_type (если ещё не существует)
    with engine.begin() as connection:
        connection.execute(text("""
            ALTER TABLE equipment_type ADD COLUMN IF NOT EXISTS staff_number VARCHAR
        """))
        # Миграция: удалить колонку name из skzi (если существует)
        connection.execute(text("ALTER TABLE skzi DROP COLUMN IF EXISTS name"))
        # Миграция: создать таблицу skzi (если ещё не существует)
        connection.execute(text("""
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
            )
        """))
    session = Session(engine)
    session.commit()

    sql = text("""
               INSERT INTO users (id, login, first_name, last_name, role, is_superuser, password)
               VALUES (:id, :login, :first_name, :last_name, :role, :is_superuser, :password)
               """)
    password = hasher.hash('admin')
    params = {
        'id': uuid.uuid4(),
        'login': 'admin',
        'first_name': 'admin',
        'last_name': 'admin',
        'role': 'head',
        'is_superuser': True,
        'password': password,
    }
    session.execute(sql, params)
    session.commit()

