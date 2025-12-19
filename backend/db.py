import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from dotenv import load_dotenv

load_dotenv()

pg_user = os.getenv('POSTGRES_USER')
pg_password = os.getenv('POSTGRES_PASSWORD')
pg_db = os.getenv('POSTGRES_DB')
pg_host = os.getenv('POSTGRES_HOST')

DATABASE_URL = f'postgresql+psycopg://{pg_user}:{pg_password}@{pg_host}:5432/{pg_db}'

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
