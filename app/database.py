from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import Settings

Base = declarative_base()
settings = Settings()
database_url = settings.SQLALCHEMY_DATABASE_URL
engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
