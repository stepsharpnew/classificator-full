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

