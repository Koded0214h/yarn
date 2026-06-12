from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import get_settings


def get_engine():
    settings = get_settings()
    url = settings.DATABASE_URL
    # SQLAlchemy requires postgresql+psycopg2:// but .env often uses postgres://
    url = url.replace('postgres://', 'postgresql://')
    return create_engine(url, pool_pre_ping=True)


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
